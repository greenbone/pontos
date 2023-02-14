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
#

import re
from datetime import datetime

from packaging.version import InvalidVersion, Version

from pontos.version.errors import VersionError


def strip_version(version: str) -> str:
    """
    Strips a leading 'v' from a version string

    E.g. v1.2.3 will be converted to 1.2.3
    """
    if version and version[0] == "v":
        return version[1:]

    return version


def check_develop(version: str) -> bool:
    """
    Checks if the given Version is a develop version

    Returns True if yes, False if not
    """
    return True if Version(version).dev is not None else False


def is_version_pep440_compliant(version: str) -> bool:
    """
    Checks if the provided version is a PEP 440 compliant version string
    """
    return version == safe_version(version)


def safe_version(version: str) -> str:
    """
    Returns the version as a string in `PEP440`_ compliant
    format.

    .. _PEP440:
       https://www.python.org/dev/peps/pep-0440
    """
    try:
        return str(Version(version))
    except InvalidVersion:
        version = version.replace(" ", ".")
        return re.sub("[^A-Za-z0-9.]+", "-", version)


def versions_equal(new_version: str, old_version: str) -> bool:
    """
    Checks if new_version and old_version are equal
    """
    return safe_version(old_version) == safe_version(new_version)


def calculate_calendar_version(current_version_str: str) -> str:
    """find the correct next calendar version by checking latest version and
    the today's date"""

    current_version = Version(current_version_str)

    today = datetime.today()
    current_year_short = today.year % 100

    if current_version.major < current_year_short or (
        current_version.major == current_year_short
        and current_version.minor < today.month
    ):
        release_version = Version(f"{current_year_short}.{today.month}.0")
        return str(release_version)

    if (
        current_version.major == today.year % 100
        and current_version.minor == today.month
    ):
        if current_version.dev is None:
            release_version = Version(
                f"{current_year_short}.{today.month}."
                f"{current_version.micro + 1}"
            )
        else:
            release_version = Version(
                f"{current_year_short}.{today.month}."
                f"{current_version.micro}"
            )
        return str(release_version)
    else:
        raise VersionError(
            f"'{current_version}' is higher than "
            f"'{current_year_short}.{today.month}'."
        )


def get_next_patch_version(release_version: str) -> str:
    """
    Get the next patch version from a valid version

    Examples:
        "1.2.3" will return "1.2.4"
        "1.2.3.dev1" will return "1.2.3"

    Raises:
        VersionError if release_version is invalid.
    """

    try:
        current_version = Version(release_version)

        if current_version.dev is not None:
            next_version = Version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro}"
            )
        else:
            next_version = Version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro + 1}"
            )

        return str(next_version)
    except InvalidVersion as e:
        raise VersionError(e) from None
