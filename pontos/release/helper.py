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

from enum import Enum

from pontos.git import Git, GitError
from pontos.terminal import Terminal

DEFAULT_TIMEOUT = 1000
DEFAULT_CHUNK_SIZE = 4096


class ReleaseType(Enum):
    PATCH = "patch"
    CALENDAR = "calendar"
    VERSION = "version"
    MAJOR = "major"
    MINOR = "minor"
    ALPHA = "alpha"
    BETA = "beta"
    RELEASE_CANDIDATE = "release-candidate"


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
