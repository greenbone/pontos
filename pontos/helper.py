# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import subprocess
import sys
import warnings
from contextlib import asynccontextmanager, contextmanager
from datetime import timedelta
from enum import Enum
from functools import wraps
from pathlib import Path
from types import ModuleType
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterator,
    Callable,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import httpx

from pontos.errors import PontosError

DEFAULT_TIMEOUT = 1000
DEFAULT_CHUNK_SIZE = 4096


async def upload(file_path: Path) -> AsyncIterator[bytes]:
    with file_path.open("rb") as f:
        read = f.read(DEFAULT_CHUNK_SIZE)
        while read:
            yield read
            read = f.read(DEFAULT_CHUNK_SIZE)


T = TypeVar("T", str, bytes)


class AsyncDownloadProgressIterable(Generic[T]):
    def __init__(
        self,
        *,
        content_iterator: AsyncIterator[T],
        url: str,
        length: Optional[int],
    ):
        """
        An async iterator to iterate over a downloadable content and the
        progress.

        Args:
            content_iterator: An async iterator to call for getting the content.
                Should be a stream of bytes or strings.
            url: The URL where the content gets downloaded.
            length: Length of the content.

        Example:
            .. code-block:: python

            it = AsyncDownloadProgressIterable(...)
            async for content, progress in it:
                file.write(content)
                print(progress)
        """
        self._content_iterator = content_iterator
        self._url = url
        self._length = None if length is None else int(length)

    @property
    def length(self) -> Optional[int]:
        """
        Size in bytes of the to be downloaded file or None if the size is not
        available
        """
        return self._length

    @property
    def url(self) -> str:
        """
        The URL where the content gets downloaded from
        """
        return self._url

    async def _download(self) -> AsyncIterator[Tuple[T, Optional[float]]]:
        dl = 0
        async for content in self._content_iterator:
            dl += len(content)
            progress = dl / self._length * 100 if self._length else None
            yield content, progress

    def __aiter__(self) -> AsyncIterator[Tuple[T, Optional[float]]]:
        """
        Returns an async iterator yielding a tuple of content and progress.
        The progress is expressed as percent of the content length.
        """
        return self._download()


@asynccontextmanager
async def download_async(
    stream: AsyncContextManager[httpx.Response],
    *,
    content_length: Optional[int] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> AsyncIterator[AsyncDownloadProgressIterable[bytes]]:
    """
    An async context manager that returns an AsyncDownloadProgressIterable.

    It ensures that the stream is closed automatically via the context manager.

    Args:
        stream: An async context manager providing a streaming response.
        content_length: Optional length of the content to download. If now
            provided it is determined from the response if available.
        chunk_size: Download the content in chunks of this size.

    Returns:
        A context manager containing an AsyncDownloadProgressIterable

    Raises:
        HTTPStatusError if the request was invalid

    Example:
        .. code-block:: python

        client = httpx.AsyncClient(...)
        stream = client.stream("GET, "https://foo.bar/baz.zip)

        async with download_async(stream) as download:
            async for content, progress in download:
                file.write(content)
                print(progress)
    """
    async with stream as response:
        response.raise_for_status()

        if not content_length:
            content_length = response.headers.get("content-length")

        yield AsyncDownloadProgressIterable(
            url=response.url,
            content_iterator=response.aiter_bytes(chunk_size=chunk_size),
            length=content_length,
        )


class DownloadProgressIterable:
    def __init__(
        self,
        *,
        content_iterator: Iterator,
        url: str,
        destination: Path,
        length: int,
    ):
        self._content_iterator = content_iterator
        self._url = url
        self._destination = destination
        self._length = None if length is None else int(length)

    @property
    def length(self) -> Optional[int]:
        """
        Size in bytes of the to be downloaded file or None if the size is not
        available
        """
        return self._length

    @property
    def destination(self) -> Path:
        """
        Destination path of the to be downloaded file
        """
        return self._destination

    @property
    def url(self) -> str:
        return self._url

    def _download(self) -> Iterator[Optional[float]]:
        dl = 0
        with self._destination.open("wb") as f:
            for content in self._content_iterator:
                dl += len(content)
                f.write(content)
                yield dl / self._length if self._length else None

    def __iter__(self) -> Iterator[Optional[float]]:
        return self._download()

    def run(self):
        """
        Just run the download without caring about the progress
        """
        try:
            it = iter(self)
            while True:
                next(it)
        except StopIteration:
            pass


@contextmanager
def download(
    url: str,
    destination: Optional[Union[Path, str]] = None,
    *,
    headers: Dict[str, Any] = None,
    params: Dict[str, Any] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout: int = DEFAULT_TIMEOUT,
) -> Generator[DownloadProgressIterable, None, None]:
    """Download file in url to filename

    Arguments:
        url: The url of the file we want to download
        destination: Path of the file to store the download in. If set it will
                     be derived from the passed URL.
        headers: HTTP headers to use for the download
        params: HTTP request parameters to use for the download
        chunk_size: Download file in chunks of this size
        timeout: Connection timeout

    Raises:
        HTTPError if the request was invalid

    Returns:
        A DownloadProgressIterator that yields the progress of the download in
        percent for each downloaded chunk or None for each chunk if the progress
        is unknown.

    Example:
        .. code-block:: python

        with download("https://example.com/some/file")) as progress_it:
            for progress in progress_it:
                print(progress)
    """
    destination = (
        Path(url.split("/")[-1]) if not destination else Path(destination)
    )

    with httpx.stream(
        "GET",
        url,
        timeout=timeout,
        follow_redirects=True,
        headers=headers,
        params=params,
    ) as response:
        response.raise_for_status()

        total_length = response.headers.get("content-length")

        yield DownloadProgressIterable(
            url=url,
            content_iterator=response.iter_bytes(chunk_size=chunk_size),
            destination=destination,
            length=total_length,
        )


def shell_cmd_runner(args: Iterable[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        shell=True,
        check=True,
        errors="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def deprecated(
    _func_or_cls: Union[str, Callable, Type] = None,
    *,
    since: str = None,
    reason: str = None,
):
    """
    A decorator to mark functions, classes and methods as deprecated

    Args:
        since: An optional version since the referenced item is deprecated.
        reason: An optional reason why the references item is deprecated.

    Examples:
        .. code-block:: python

        @deprecated
        def my_function(*args, **kwargs):
            ...

        @deprecated("The function is obsolete. Please use my_func instead.")
        def my_function(*args, **kwargs):
            ...

        @deprecated(
            since="1.2.3",
            reason="The function is obsolete. Please use my_func instead."
        )
        def my_function(*args, **kwargs):
            ...

        @deprecated(reason="The class will be removed in version 3.4.5")
        class Foo:
            ...

        class Foo:
            @deprecated(since="2.3.4")
            def bar(self, *args, **kwargs):
                ...
    """
    if isinstance(_func_or_cls, str):
        reason = _func_or_cls
        _func_or_cls = None

    def decorator_repeat(func_or_cls):
        module = func_or_cls.__module__
        name = func_or_cls.__name__

        if module == "__main__":
            msg = f"{name} is deprecated."
        else:
            msg = f"{module}.{name} is deprecated."

        if since:
            msg += f" It is deprecated since version {since}."
        if reason:
            msg += f" {reason}"

        @wraps(func_or_cls)
        def wrapper(*args, **kwargs):
            warnings.warn(msg, category=DeprecationWarning, stacklevel=3)
            return func_or_cls(*args, **kwargs)

        return wrapper

    if _func_or_cls is None:
        return decorator_repeat
    else:
        return decorator_repeat(_func_or_cls)


@contextmanager
def add_sys_path(
    directory: Union[str, os.PathLike]
) -> Generator[None, None, None]:
    """
    Context Manager to add a directory path to the module search path aka.
    sys.path. The directory path is removed when the context manager is left.

    Args:
        directory: A os.PathLike directory to add to sys.path

    Example:
        .. code-block:: python

            with add_sys_path("/tmp/test-modules"):
                import mymodule
    """
    directory = os.fspath(directory)

    if sys.path[0] != directory:
        sys.path.insert(0, directory)

    try:
        yield
    finally:
        try:
            sys.path.remove(directory)
        except ValueError:
            # directory was not in the path
            pass


def unload_module(module: Union[str, ModuleType]) -> None:
    """
    Unload a Python module

    Args:
        name: Module instance or name of the Python module to unload.
            For example: foo.bar
    """
    name = module.__name__ if isinstance(module, ModuleType) else module

    if name in sys.modules:
        del sys.modules[name]


@contextmanager
def ensure_unload_module(
    module: Union[str, ModuleType]
) -> Generator[None, None, None]:
    """
    A context manager to ensure that a module gets removed even if an error
    occurs

    Args:
        name: Module instance or name of the Python module to unload.
            For example: foo.bar

    Example:
        .. code-block:: python

            with ensure_unload_module("foo.bar"):
                do_something()
    """
    try:
        yield
    finally:
        unload_module(module)


def snake_case(value: str) -> str:
    """
    Convert a string to snake case/underscore naming scheme

    Example:
        snake_case("CamelCase") will return "camel_case"
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def enum_or_value(value: Union[Enum, Any]) -> Any:
    """
    Return the value of an Enum or the value if it isn't an Enum
    """
    if isinstance(value, Enum):
        return value.value

    return value


regex = re.compile(
    r"^((?P<weeks>[\.\d]+?)w)?((?P<days>[\.\d]+?)d)?((?P<hours>[\.\d]+?)h)?"
    r"((?P<minutes>[\.\d]+?)m)?((?P<seconds>[\.\d]+?)s)?$"
)


def parse_timedelta(time_str: str) -> timedelta:
    """
    Parse a timedelta from a string

    Examples:
        .. code-block:: python

        parse_timedelta("1.5h")
        parse_timedelta("1w2d4h5m6s")
    """
    parts = regex.match(time_str)
    if not parts:
        raise PontosError(f"Invalid timedelta format '{time_str}'.")

    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = float(param)

    return timedelta(**time_params)
