# Copyright (C) 2020-2022 Greenbone Networks GmbH
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

import datetime
import sys
from pathlib import Path
from typing import Optional, Tuple

from packaging.version import InvalidVersion, Version

from pontos.git import Git, GitError
from pontos.terminal import Terminal
from pontos.version import COMMANDS
from pontos.version.helper import VersionError

DEFAULT_TIMEOUT = 1000
DEFAULT_CHUNK_SIZE = 4096

DEFAULT_PYTHON_VERSION_FILE = "*__version__.py"
DEFAULT_GO_VERSION_FILE = Path("version.go")


def commit_files(
    git: Git,
    filename: str,
    commit_msg: str,
    *,
    git_signing_key: str = "",
    changelog: bool = False,
) -> None:
    """Add files to staged and commit staged files.

    Args:
        git: A Git instance
        filename: The filename of file to add and commit
        commit_msg: The commit message for the commit
        git_signing_key: The signing key to sign this commit
        changelog: Add CHANGELOG.md file

    """
    git.add(filename)

    try:
        if list(Path.cwd().glob(DEFAULT_PYTHON_VERSION_FILE)):
            git.add(DEFAULT_PYTHON_VERSION_FILE)
        if DEFAULT_GO_VERSION_FILE.exists():
            git.add(DEFAULT_GO_VERSION_FILE)
    except GitError:
        pass

    if changelog:
        git.add("CHANGELOG.md")
    if git_signing_key:
        git.commit(commit_msg, verify=False, gpg_signing_key=git_signing_key)
    else:
        git.commit(commit_msg, verify=False)


def calculate_calendar_version(terminal: Terminal) -> str:
    """find the correct next calendar version by checking latest version and
    the today's date"""

    current_version_str: str = get_current_version(terminal)
    current_version = Version(current_version_str)

    today = datetime.date.today()

    if (
        current_version.major < today.year % 100
        or current_version.minor < today.month
    ):
        release_version = Version(
            f"{str(today.year  % 100)}.{str(today.month)}.0"
        )
        return str(release_version)
    elif (
        current_version.major == today.year % 100
        and current_version.minor == today.month
    ):
        if current_version.dev is None:
            release_version = Version(
                f"{str(today.year  % 100)}.{str(today.month)}."
                f"{str(current_version.micro + 1)}"
            )
        else:
            release_version = Version(
                f"{str(today.year  % 100)}.{str(today.month)}."
                f"{str(current_version.micro)}"
            )
        return str(release_version)
    else:
        terminal.error(
            f"'{str(current_version)}' is higher than "
            f"'{str(today.year  % 100)}.{str(today.month)}'."
        )
        sys.exit(1)


def get_current_version(terminal: Terminal) -> Optional[str]:
    """Get the current Version from a pyproject.toml or
    a CMakeLists.txt file"""

    for cmd in COMMANDS:
        command = cmd()
        if command.project_found():
            terminal.ok("Found project definition file.")
            return command.get_current_version()

    terminal.error("No project settings file found")
    return None


def get_last_release_version() -> Optional[str]:
    """Get the last released Version from git.

    Returns:
        Last released git-tag if tags were found
        or None
    """

    git_interface = Git()
    tag_list = git_interface.list_tags()
    return tag_list[-1] if tag_list else None


def get_next_patch_version(terminal: Terminal) -> str:
    """find the correct next patch version by checking latest version"""

    current_version_str: str = get_current_version(terminal)
    current_version = Version(current_version_str)

    if current_version.dev is not None:
        release_version = Version(
            f"{str(current_version.major)}."
            f"{str(current_version.minor)}."
            f"{str(current_version.micro)}"
        )
    else:
        release_version = Version(
            f"{str(current_version.major)}."
            f"{str(current_version.minor)}."
            f"{str(current_version.micro + 1)}"
        )

    return str(release_version)


def get_next_dev_version(release_version: str) -> str:
    """Get the next dev Version from a valid version"""
    # will be a dev1 version
    try:
        release_version_obj = Version(release_version)
        next_version_obj = Version(
            f"{str(release_version_obj.major)}."
            f"{str(release_version_obj.minor)}."
            f"{str(release_version_obj.micro + 1)}"
        )
        return str(next_version_obj)
    except InvalidVersion as e:
        raise (VersionError(e)) from None


def get_git_repository_name(
    remote: str = "origin",
) -> str:
    """Get the git repository name

    Arguments:
        remote: the remote to look up the name (str) default: origin

    Returns:
        project name
    """

    ret = Git().remote_url(remote)
    return ret.rsplit("/", maxsplit=1)[-1].replace(".git", "").strip()


def find_signing_key(terminal: Terminal) -> str:
    """Find the signing key in the config

    Arguments:
        terminal: The terminal for console output

    Returns:
        git signing key or empty string
    """

    try:
        return Git().config("user.signingkey").strip()
    except GitError as e:
        # The command `git config user.signingkey` returns
        # return code 1 if no key is set.
        # So we will return empty string ...
        if e.returncode == 1:
            terminal.warning("No signing key found.")
        return ""


def update_version(
    terminal: Terminal, to: str, *, develop: bool = False
) -> Tuple[bool, Optional[str]]:
    """Use pontos-version to update the version.

    Arguments:
        to: The version (str) that will be set
        develop: Wether to set version to develop or not (bool)

    Returns:
       executed: True if successfully executed, False else
       filename: The filename of the project definition
    """
    project_file = None
    for cmd in COMMANDS:
        command = cmd()
        project_file = command.project_file_found()
        if project_file:
            break

    if not project_file:
        terminal.error("No project definition found.")
        return False, None

    try:
        command.update_version(new_version=to, develop=develop)
        return True, project_file.name
    except VersionError:
        terminal.error(f"Unable to update version {to} in {project_file}")
        return False, None
