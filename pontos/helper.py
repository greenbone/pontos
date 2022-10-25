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

import subprocess
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterator,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import httpx

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
