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

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal, Type, Union

from packaging.version import InvalidVersion
from packaging.version import Version as PackagingVersion

from .errors import VersionError


class Version(PackagingVersion):
    """
    A class handling version information
    """


def parse_version(version: str) -> Version:
    try:
        return Version(version)
    except InvalidVersion as e:
        raise VersionError(e) from None


@dataclass
class VersionUpdate:
    previous: Version
    new: Version
    changed_files: list[Path] = field(default_factory=list)


class VersionCalculator:
    def next_patch_version(self, current_version: Version) -> Version:
        """
        Get the next patch version from a valid version

        Examples:
            "1.2.3" will return "1.2.4"
            "1.2.3.dev1" will return "1.2.3"

        Raises:
            VersionError if version is invalid.
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
        return parse_version(
            f"{current_version.major}.{current_version.minor +1}.0"
        )

    def next_major_version(self, current_version: Version) -> Version:
        return parse_version(f"{current_version.major + 1}.0.0")

    def next_dev_version(self, current_version: Version) -> Version:
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


class VersionCommand(ABC):
    """Generic class usable to implement the
    version commands for several programming languages"""

    project_file_name: str
    version_calculator_class: Type[VersionCalculator] = VersionCalculator

    def __init__(self) -> None:
        self.project_file_path = Path.cwd() / self.project_file_name

    @abstractmethod
    def get_current_version(self) -> Version:
        """Get the current version of this project"""

    @abstractmethod
    def verify_version(
        self, version: Union[Literal["current"], Version]
    ) -> None:
        """Verify the current version of this project"""

    @abstractmethod
    def update_version(
        self, new_version: Version, *, force: bool = False
    ) -> VersionUpdate:
        """Update the current version of this project"""

    def project_found(self) -> bool:
        """
        Returns True if a command has detected a corresponding project
        """
        return self.project_file_path.exists()

    def get_version_calculator(self) -> VersionCalculator:
        return self.version_calculator_class()
