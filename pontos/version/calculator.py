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

from .errors import VersionError
from .version import Version, parse_version


class VersionCalculator:
    def next_patch_version(self, current_version: Version) -> Version:
        """
        Get the next patch version from a valid version

        Examples:
            "1.2.3" will return "1.2.4"
            "1.2.3.dev1" will return "1.2.3"
        """

        if current_version.is_prerelease:
            next_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro}"
            )
        else:
            next_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro + 1}"
            )

        return next_version

    def next_calendar_version(self, current_version: Version) -> Version:
        """
        Find the correct next calendar version by checking latest version and
        the today's date

        Raises:
            VersionError if version is invalid.
        """

        today = datetime.today()
        current_year_short = today.year % 100

        if current_version.major < current_year_short or (
            current_version.major == current_year_short
            and current_version.minor < today.month
        ):
            return parse_version(f"{current_year_short}.{today.month}.0")

        if (
            current_version.major == today.year % 100
            and current_version.minor == today.month
        ):
            if current_version.dev is None:
                release_version = parse_version(
                    f"{current_year_short}.{today.month}."
                    f"{current_version.micro + 1}"
                )
            else:
                release_version = parse_version(
                    f"{current_year_short}.{today.month}."
                    f"{current_version.micro}"
                )
            return release_version
        else:
            raise VersionError(
                f"'{current_version}' is higher than "
                f"'{current_year_short}.{today.month}'."
            )

    def next_minor_version(self, current_version: Version) -> Version:
        """
        Get the next minor version from a valid version

        Examples:
            "1.2.3" will return "1.3.0"
            "1.2.3.dev1" will return "1.3.0"
        """
        return parse_version(
            f"{current_version.major}.{current_version.minor + 1}.0"
        )

    def next_major_version(self, current_version: Version) -> Version:
        """
        Get the next major version from a valid version

        Examples:
            "1.2.3" will return "2.0.0"
            "1.2.3.dev1" will return "2.0.0"
        """
        return parse_version(f"{current_version.major + 1}.0.0")

    def next_dev_version(self, current_version: Version) -> Version:
        """
        Get the next development version from a valid version

        Examples:
            "1.2.3" will return "1.2.4.dev1"
            "1.2.3.dev1" will return "1.2.3.dev2"
        """
        if current_version.is_devrelease:
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro }.dev{current_version.dev + 1}"
            )
        elif current_version.is_prerelease:
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro }{current_version.pre[0]}"
                f"{current_version.pre[1]}+dev1"
            )
        else:
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro + 1 }.dev1"
            )

        return release_version

    def next_alpha_version(self, current_version: Version) -> Version:
        """
        Get the next alpha version from a valid version

        Examples:
            "1.2.3" will return "1.2.4a1"
            "1.2.3.dev1" will return "1.2.3a1"
        """
        if current_version.is_devrelease:
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro }a1"
            )
        elif current_version.is_prerelease and current_version.pre[0] == "a":
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro }a{current_version.pre[1] + 1}"
            )
        else:
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro + 1 }a1"
            )

        return release_version

    def next_beta_version(self, current_version: Version) -> Version:
        """
        Get the next alpha version from a valid version

        Examples:
            "1.2.3" will return "1.2.4b1"
            "1.2.3.dev1" will return "1.2.3b1"
        """
        if current_version.is_devrelease or (
            current_version.is_prerelease and current_version.pre[0] == "a"
        ):
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro }b1"
            )
        elif current_version.is_prerelease and current_version.pre[0] == "b":
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro }b{current_version.pre[1] + 1}"
            )
        else:
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro + 1 }b1"
            )

        return release_version

    def next_release_candidate_version(
        self, current_version: Version
    ) -> Version:
        """
        Get the next alpha version from a valid version

        Examples:
            "1.2.3" will return "1.2.4rc1"
            "1.2.3.dev1" will return "1.2.3rc1"
        """
        if current_version.is_devrelease or (
            current_version.is_prerelease and current_version.pre[0] != "rc"
        ):
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro }rc1"
            )
        elif current_version.is_prerelease and current_version.pre[0] == "rc":
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro }rc{current_version.pre[1] + 1}"
            )
        else:
            release_version = parse_version(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.micro + 1 }rc1"
            )

        return release_version
