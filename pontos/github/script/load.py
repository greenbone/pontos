# Copyright (C) 2022 Greenbone Networks GmbH
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

import asyncio
import importlib
import os
from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Generator, Union

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

            with load_module("path/to/script.py") as module:
                module.func()
    """
    path = Path(script)
    module_name = path.stem

    with add_sys_path(path.parent.absolute()), ensure_unload_module(
        module_name
    ):
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
        async with GitHubAsyncRESTApi(token, timeout=timeout) as api:
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
    Run a GitHub script add_script_arguments function

    Args:
        module: Module containing the GitHub script add_script_arguments
            function
        parser: An ArgumentParser to add additional CLI arguments
    """
    func = getattr(module, GITHUB_SCRIPT_PARSER_FUNCTION_NAME, None)
    if func:
        func(parser)
