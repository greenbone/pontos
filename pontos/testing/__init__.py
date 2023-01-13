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

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from pontos.git.git import exec_git
from pontos.helper import add_sys_path, ensure_unload_module, unload_module

__all__ = (
    "temp_directory",
    "temp_git_repository",
    "temp_file",
    "temp_python_module",
    "add_sys_path",
    "ensure_unload_module",
    "unload_module",
)


@contextmanager
def temp_directory(
    *, change_into: bool = False, add_to_sys_path: bool = False
) -> Generator[Path, None, None]:
    """
    Context Manager to create a temporary directory

    Args:
        change_into: Set the created temporary as the current working directory.
            The behavior of the current working directory when leaving the
            context manager is undefined.
        add_to_sys_path: Add the created temporary directory to the directories
            for searching for Python modules

    Returns:
        A path to the created temporary directory

    Example:
        .. code-block:: python

            with temp_directory(change_into=True) as tmp:
                new_file = tmp / "test.txt"
    """
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = Path(temp_dir.name)

    if change_into:
        try:
            old_cwd = Path.cwd()
        except FileNotFoundError:
            old_cwd = Path.home()

        os.chdir(dir_path)

    try:
        if add_to_sys_path:
            with add_sys_path(dir_path):
                yield Path(dir_path)
        else:
            yield Path(dir_path)
    finally:
        if change_into:
            try:
                os.chdir(old_cwd)
            finally:
                temp_dir.cleanup()
        else:
            temp_dir.cleanup()


@contextmanager
def temp_git_repository(
    *,
    user_name: str = "Max Mustermann",
    user_email: str = "max.mustermann@example.com",
    branch: str = "main",
) -> Generator[Path, None, None]:
    """
    Context Manager to create a temporary git repository on the filesystem

    Args:
        user_name: User name to configure in the repository.
            Default: Max Mustermann
        user_email: Email address of the user to configure in the repository.
            Default: max.mustermann@example.com
        branch: Branch name to create. Default: main

    Returns:
        A path to the created temporary git repository directory

    Example:
        .. code-block:: python

            with temp_git_repository() as repo:
                new_file = repo / "foo.txt"
                new_file.write_text("Lorem Ipsum")

                exec_git("add", "foo.txt")
    """
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)

    try:
        old_cwd = Path.cwd()
    except FileNotFoundError:
        old_cwd = Path.home()

    os.chdir(temp_path)

    exec_git("init", "-b", branch)
    exec_git("config", "--local", "user.email", user_email)
    exec_git("config", "--local", "user.name", user_name)

    try:
        yield temp_path
    finally:
        try:
            os.chdir(old_cwd)
        finally:
            temp_dir.cleanup()


@contextmanager
def temp_file(
    content: Optional[str] = None,
    *,
    name: str = "test.toml",
    change_into: bool = False,
) -> Generator[Path, None, None]:
    """
    A Context Manager to create a temporary file within a new temporary
    directory. The temporary file and directory are removed when the context is
    exited.

    Args:
        content: Content to write into the temporary file.
        name: Name of the temporary file. "test.toml" by default.
        change_into: Adjust the current working directory to the temporary
            directory.

    Returns:
        A path to the created temporary file

    Example:
        .. code-block:: python

            with temp_file("Lorem Ipsum", name="foo.txt") as fpath:

    """
    with temp_directory(change_into=change_into) as tmp_dir:
        test_file = tmp_dir / name
        if content:
            test_file.write_text(content, encoding="utf8")
        else:
            test_file.touch()

        yield test_file


@contextmanager
def temp_python_module(
    content: str, *, name: str = "foo", change_into: bool = False
) -> Generator[Path, None, None]:
    """
    A Context Manager to create a new Python module in a temporary directory.
    The temporary directory will be added to the module search path and removed
    from the search path when the context is exited. Also it is ensured that
    the module is unloaded if the context is exited.

    Args:
        content: Python code to write into the temporary module.
        name: Name of the new Python module. By default: "foo".
        change_into: Adjust the current working directory to the temporary
            directory.

    Returns:
        A path to the created temporary Python module file

    Example:
        .. code-block:: python

            with temp_python_module(
                "def hello(value):\\n  print(f'Hello {value}')", name="world"
            ) as python_module_path:
                from world import hello
                hello("World")


    """
    with temp_directory(
        add_to_sys_path=True, change_into=change_into
    ) as tmp_dir, ensure_unload_module(name):
        test_file = tmp_dir / f"{name}.py"
        test_file.write_text(content, encoding="utf8")
        yield test_file
