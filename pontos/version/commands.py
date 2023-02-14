# Copyright (C) 2023 Greenbone Networks GmbH
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

from typing import Optional, Tuple, Type

from .cmake import CMakeVersionCommand
from .errors import VersionError
from .go import GoVersionCommand
from .javascript import JavaScriptVersionCommand
from .python import PythonVersionCommand
from .version import VersionCommand, VersionUpdate

COMMANDS: Tuple[Type[VersionCommand]] = (
    CMakeVersionCommand,
    GoVersionCommand,
    JavaScriptVersionCommand,
    PythonVersionCommand,
)


def get_current_version() -> str:
    """
    Get the current Version for the current project

    Raises:
        VersionError if current version can not be found.
    """

    for cmd in COMMANDS:
        command = cmd()
        if command.project_found():
            return command.get_current_version()

    raise VersionError("No project settings file found")


def update_version(
    new_version: str, *, develop: Optional[bool] = False
) -> VersionUpdate:
    """
    Update the Version for the current project in the relevant files

    Args:
        new_version: The version that will be set for the project
        develop: Add a dev version section to the version string

    Raises:
        VersionError if no project settings (file) can be found.

    Returns:
        Information about the version update
    """
    for cmd in COMMANDS:
        command = cmd()
        if command.project_found():
            return command.update_version(
                new_version=new_version, develop=develop
            )

    raise VersionError("No project settings file found")
