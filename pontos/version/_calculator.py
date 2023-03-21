# Copyright (C) 2023 Greenbone AG
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
from datetime import datetime
from typing import Type

from pontos.version.errors import VersionError

from .version import Version


class VersionCalculator(ABC):
    """
    An abstract base class for calculating a next version from a version
    """

    version_cls: Type[Version]

    @classmethod
    def version_from_string(cls, version: str) -> Version:
        """
        Create a version from a version string

        Args:
            version: Version string to parse

        Raises:
            VersionError: If the version string is invalid.

        Returns:
            A new version instance
        """
        return cls.version_cls.from_string(version)

    @classmethod
    def next_calendar_version(cls, current_version: Version) -> Version:
        """
        Find the correct next calendar version by checking latest version and
        the today's date

        Raises:
            VersionError: If version is invalid.
        """
        today = datetime.today()
        current_year_short = today.year % 100

        if current_version.major < current_year_short or (
            current_version.major == current_year_short
            and current_version.minor < today.month
        ):
            return cls.version_from_string(
                f"{current_year_short}.{today.month}.0"
            )

        if (
            current_version.major == today.year % 100
            and current_version.minor == today.month
        ):
            if current_version.dev is None:
                release_version = cls.version_from_string(
                    f"{current_year_short}.{today.month}."
                    f"{current_version.patch + 1}"
                )
            else:
                release_version = cls.version_from_string(
                    f"{current_year_short}.{today.month}."
                    f"{current_version.patch}"
                )
            return release_version
        else:
            raise VersionError(
                f"'{current_version}' is higher than "
                f"'{current_year_short}.{today.month}'."
            )

    @classmethod
    def next_major_version(cls, current_version: Version) -> Version:
        """
        Get the next major version from a valid version

        Examples:
            "1.2.3" will return "2.0.0"
            "1.2.3.dev1" will return "1.2.3"
            "1.2.3-alpha1" will return "1.2.3"
            "1.0.0" will return "2.0.0"
            "1.0.0-a1" will return "1.0.0"
            "1.0.0.dev1" will return "1.0.0"
            "0.5.0-a1" will return "1.0.0"
            "0.5.0.dev1" will return "1.0.0"
        """
        if (
            (current_version.is_pre_release or current_version.is_dev_release)
            and current_version.patch == 0
            and current_version.minor == 0
        ):
            return cls.version_from_string(
                f"{current_version.major}.{current_version.minor}."
                f"{current_version.patch}"
            )
        return cls.version_from_string(f"{current_version.major + 1}.0.0")

    @classmethod
    def next_minor_version(cls, current_version: Version) -> Version:
        """
        Get the next minor version from a valid version

        Examples:
            "1.2.3" will return "1.3.0"
            "1.2.3.dev1" will return "1.3.0"
            "1.2.3-alpha1" will return "1.3.0"
            "1.0.0" will return "1.1.0"
            "1.0.0-a1" will return "1.0.0"
            "1.0.0.dev1" will return "1.0.0"
            "0.5.0-a1" will return "0.5.0"
            "0.5.0.dev1" will return "0.5.0"
        """
        if (
            current_version.is_pre_release or current_version.is_dev_release
        ) and current_version.patch == 0:
            return cls.version_from_string(
                f"{current_version.major}.{current_version.minor}."
                f"{current_version.patch}"
            )
        return cls.version_from_string(
            f"{current_version.major}.{current_version.minor + 1}.0"
        )

    @classmethod
    def next_patch_version(cls, current_version: Version) -> Version:
        """
        Get the next patch version from a valid version

        Examples:
            "1.2.3" will return "1.2.4"
            "1.2.3.dev1" will return "1.2.3"
            "1.2.3-dev1" will return "1.2.3"
            "1.2.3+dev1" will return "1.2.4"
            "1.2.3-alpha1" will return "1.2.3"
            "1.0.0" will return "1.0.1"
            "1.0.0-a1" will return "1.0.0"
            "1.0.0.dev1" will return "1.0.0"
            "0.5.0-a1" will return "0.5.0"
            "0.5.0.dev1" will return "0.5.0"
        """
        if not current_version:
            raise VersionError("No current version passed.")

        if current_version.is_dev_release or current_version.is_pre_release:
            next_version = cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}"
            )
        else:
            next_version = cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch + 1}"
            )

        return next_version

    @staticmethod
    @abstractmethod
    def next_dev_version(current_version: Version) -> Version:
        """
        Get the next development version from a valid version

        Examples:
            "1.2.3" will return "1.2.4-dev1"
            "1.2.3.dev1" will return "1.2.3.dev2"
            "1.2.3-dev1" will return "1.2.3-dev2"
            "1.2.3+dev1" will return "1.2.4-dev1"
            "1.2.3-alpha1" will return "1.2.3-alpha2-dev1"
            "1.0.0" will return "1.0.1-dev1"
            "1.0.0-a1" will return "1.0.0-a2-dev1"
            "1.0.0.dev1" will return "1.0.0.dev2"
            "0.5.0-a1" will return "0.5.0-a2-dev1"
            "0.5.0.dev1" will return "0.5.0.dev2"
        """

    @staticmethod
    @abstractmethod
    def next_alpha_version(current_version: Version) -> Version:
        """
        Get the next alpha version from a valid version

        Examples:
            "1.2.3" will return "1.2.4-alpha1"
            "1.2.3.dev1" will return "1.2.3-alpha1"
            "1.2.3-dev1" will return "1.2.3-alpha1"
            "1.2.3+dev1" will return "1.2.4-alpha1"
            "1.2.3-alpha1" will return "1.2.3-alpha2"
            "1.0.0" will return "1.0.1-alpha1"
            "1.0.0-a1" will return "1.0.1-alpha1"
            "1.0.0.dev1" will return "1.0.0-alpha1"
            "0.5.0-a1" will return "0.5.1-alpha1"
            "0.5.0.dev1" will return "0.5.0-alpha1"
        """

    @staticmethod
    @abstractmethod
    def next_beta_version(current_version: Version) -> Version:
        """
        Get the next beta version from a valid version

        Examples:
            "1.2.3" will return "1.2.4-beta1"
            "1.2.3.dev1" will return "1.2.3-beta1"
            "1.2.3-dev1" will return "1.2.3-beta1"
            "1.2.3+dev1" will return "1.2.4-beta1"
            "1.2.3-alpha1" will return "1.2.3-beta1"
            "1.0.0" will return "1.0.1-beta1"
            "1.0.0-a1" will return "1.0.1-beta1"
            "1.0.0.dev1" will return "1.0.0-beta1"
            "0.5.0-a1" will return "0.5.1-beta1"
            "0.5.0.dev1" will return "0.5.0-beta1"
        """

    @staticmethod
    @abstractmethod
    def next_release_candidate_version(current_version: Version) -> Version:
        """
        Get the next release candidate version from a valid version

        Examples:
            "1.2.3" will return "1.2.4-rc1"
            "1.2.3.dev1" will return "1.2.3-rc1"
            "1.2.3-dev1" will return "1.2.3-rc1"
            "1.2.3+dev1" will return "1.2.4-rc1"
            "1.2.3-alpha1" will return "1.2.3-rc1"
            "1.0.0" will return "1.0.1-rc1"
            "1.0.0-a1" will return "1.0.1-rc1"
            "1.0.0.dev1" will return "1.0.0-rc1"
            "0.5.0-a1" will return "0.5.1-rc1"
            "0.5.0.dev1" will return "0.5.0-rc"
        """
