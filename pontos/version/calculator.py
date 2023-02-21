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

from datetime import datetime

from packaging.version import InvalidVersion, Version

from .errors import VersionError


class VersionCalculator:
    def next_patch_version(self, version: str) -> str:
        """
        Get the next patch version from a valid version

        Examples:
            "1.2.3" will return "1.2.4"
            "1.2.3.dev1" will return "1.2.3"

        Raises:
            VersionError if version is invalid.
        """

        try:
            current_version = Version(version)

            if current_version.is_prerelease:
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

    def next_calendar_version(self, version: str) -> str:
        """
        Find the correct next calendar version by checking latest version and
        the today's date

        Raises:
            VersionError if version is invalid.
        """

        current_version = Version(version)

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

    def next_minor_version(self, version: str) -> str:
        try:
            current_version = Version(version)
            release_version = Version(
                f"{current_version.major}.{current_version.minor +1}.0"
            )
            return str(release_version)
        except InvalidVersion as e:
            raise VersionError(e) from None

    def next_major_version(self, version: str) -> str:
        try:
            current_version = Version(version)
            release_version = Version(f"{current_version.major + 1}.0.0")
            return str(release_version)
        except InvalidVersion as e:
            raise VersionError(e) from None
