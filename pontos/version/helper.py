# -*- coding: utf-8 -*-
# Copyright (C) 2021 Greenbone Networks GmbH
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
#

import datetime
from pathlib import Path
import sys

from packaging.version import Version, InvalidVersion

from pontos.version import (
    PontosVersionCommand,
    CMakeVersionCommand,
    VersionError,
)


def get_next_dev_version(release_version: str) -> str:
    """Get the next dev Version from a valid version"""
    # will be a dev1 version
    try:
        release_version_obj = Version(release_version)
        next_version_obj = Version(
            f'{str(release_version_obj.major)}.'
            f'{str(release_version_obj.minor)}.'
            f'{str(release_version_obj.micro + 1)}.dev1'
        )
        return str(next_version_obj)
    except InvalidVersion as e:
        raise (VersionError(e)) from None


def get_current_version() -> str:
    """Get the current Version from a pyproject.toml or
    a CMakeLists.txt file"""

    available_cmds = [
        ('CMakeLists.txt', CMakeVersionCommand),
        ('pyproject.toml', PontosVersionCommand),
    ]
    for file_name, cmd in available_cmds:
        project_definition_path = Path.cwd() / file_name
        if project_definition_path.exists():
            current_version: str = cmd().get_current_version()
            return current_version

    print("No project settings file found")
    sys.exit(1)


def calculate_calendar_version() -> str:
    """find the correct next calendar version by checking latest version and
    the today's date"""

    current_version_str: str = get_current_version()
    current_version = Version(current_version_str)

    today = datetime.date.today()

    if (
        current_version.major < today.year % 100
        or current_version.minor < today.month
    ):
        release_version = Version(
            f'{str(today.year  % 100)}.{str(today.month)}.0'
        )
        return str(release_version)
    elif (
        current_version.major == today.year % 100
        and current_version.minor == today.month
    ):
        if not current_version.dev:
            release_version = Version(
                f'{str(today.year  % 100)}.{str(today.month)}.'
                f'{str(current_version.micro + 1)}'
            )
        else:
            release_version = Version(
                f'{str(today.year  % 100)}.{str(today.month)}.'
                f'{str(current_version.micro)}'
            )
        return str(release_version)
    else:
        print(
            f"'{str(current_version)}' is higher than "
            f"'{str(today.year  % 100)}.{str(today.month)}'."
        )
        sys.exit(1)
