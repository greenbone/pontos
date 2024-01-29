# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
import importlib
import os
from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Generator, Union

from httpx import Timeout

from pontos.github.api.api import GitHubAsyncRESTApi
from pontos.github.script.errors import GitHubScriptError
from pontos.helper import add_sys_path, ensure_unload_module

GITHUB_SCRIPT_FUNCTION_NAME = "github_script"
GITHUB_SCRIPT_PARSER_FUNCTION_NAME = "add_script_arguments"


@contextmanager
def load_script(
    script: Union[str, os.PathLike]
) -> Generator[ModuleType, None, None]:
    """
    A context manager to load a script module.

    The script is unloaded when the context manager exits.

    Args:
        script: Name or path of the script module to load

    Example:
        .. code-block:: python

            from pontos.github.script import load_script

            with load_script("path/to/script.py") as module:
                module.func()

            with load_script("some.python.module") as module:
                module.func()
    """
    path = Path(script)
    if path.suffix == ".py":
        module_name = path.stem

        with (
            add_sys_path(path.parent.absolute()),
            ensure_unload_module(module_name),
        ):
            yield importlib.import_module(module_name)
    else:
        module_name = str(path)
        with ensure_unload_module(module_name):
            yield importlib.import_module(module_name)


def run_github_script_function(
    module: ModuleType, token: str, timeout: float, args: Namespace
) -> int:
    """
    Run a github_script function from a Python module

    Args:
        module: Module that the GitHub script function contains
        token: A GitHub token for authentication
        timeout: Timeout for the GitHub requests in seconds
        args: Arguments forwarded to the script function

    Raises:
        GitHubScriptError: If the module doesn't have a github_script function
            or if the github_script function is not an async coroutine.

    Returns:
        The return value of the github_script coroutine

    Example:
        .. code-block:: python

            from pontos.github.script import (
                load_script,
                run_github_script_function,
            )

            with load_script("path/to/script.py") as module:
                return run_github_script_function(module, token, 60.0, args)

            with load_script("some.python.module") as module:
                return run_github_script_function(module, token, 60.0, args)
    """
    if not hasattr(module, GITHUB_SCRIPT_FUNCTION_NAME):
        raise GitHubScriptError(
            f"{module.__file__} is not a valid Pontos GitHub Script. A "
            f"{GITHUB_SCRIPT_FUNCTION_NAME} function is missing."
        )
    func = getattr(module, GITHUB_SCRIPT_FUNCTION_NAME)
    if not asyncio.iscoroutinefunction(func):
        # it's not async
        raise GitHubScriptError(
            f"{module.__file__} is not a valid Pontos GitHub Script. "
            f"{GITHUB_SCRIPT_FUNCTION_NAME} need to be an async coroutine "
            "function."
        )

    async def run_async() -> int:
        async with GitHubAsyncRESTApi(token, timeout=Timeout(timeout)) as api:
            return await func(api, args)

    loop_owner = False
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop_owner = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        retval = loop.run_until_complete(run_async())
    finally:
        if loop_owner:
            loop.close()
    return retval


def run_add_arguments_function(
    module: ModuleType, parser: ArgumentParser
) -> None:
    """
    Run a GitHub script add_script_arguments function (if available in the
    module).

    Args:
        module: Module containing the GitHub script add_script_arguments
            function
        parser: An ArgumentParser to add additional CLI arguments

    Example:
        .. code-block:: python

            from argparse import ArgumentParser
            from pontos.github.script import (
                load_script,
                run_github_script_function,
            )

            parser = ArgumentParser()

            with load_script("path/to/script.py") as module:
                run_add_arguments_function(module, parser)

            with load_script("some.python.module") as module:
                run_add_arguments_function(module, parser)
    """
    func = getattr(module, GITHUB_SCRIPT_PARSER_FUNCTION_NAME, None)
    if func:
        func(parser)
