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

from typing import Any, Optional, Tuple

from packaging.version import InvalidVersion
from packaging.version import Version as PackagingVersion

from .._calculator import VersionCalculator
from ..errors import VersionError
from ..version import Version
from ._scheme import VersioningScheme

__all__ = (
    "PEP440Version",
    "PEP440VersionCalculator",
    "PEP440VersioningScheme",
)


class PEP440Version(Version):
    """
    A class handling PEP 440 based version information
    """

    def __init__(self, version: str) -> None:
        self._version = PackagingVersion(version)

    @property
    def major(self) -> int:
        """The first item of the version"""
        return self._version.major

    @property
    def minor(self) -> int:
        """The second item of :attr:`release` or ``0`` if unavailable."""
        return self._version.minor

    @property
    def patch(self) -> int:
        """The third item of :attr:`release` or ``0`` if unavailable."""
        return self._version.micro

    @property
    def pre(self) -> Optional[Tuple[str, int]]:
        """The pre-release segment of the version."""
        if self.is_dev_release:
            return ("dev", self._version.dev)  # type: ignore
        return self._version.pre

    @property
    def dev(self) -> Optional[int]:
        """The development number of the version."""
        return self._version.dev  # type: ignore

    @property
    def local(self) -> Optional[str]:
        """The local version segment of the version."""
        return self._version.local

    @property
    def is_pre_release(self) -> bool:
        """Whether this version is a pre-release."""
        return self._version.is_prerelease

    @property
    def is_dev_release(self) -> bool:
        """Whether this version is a development release."""
        return self._version.is_devrelease

    @property
    def is_alpha_release(self) -> bool:
        """Whether this version is a alpha release."""
        return self.pre is not None and self.pre[0] == "a"

    @property
    def is_beta_release(self) -> bool:
        """Whether this version is a beta release."""
        return self.pre is not None and self.pre[0] == "b"

    @property
    def is_release_candidate(self) -> bool:
        """Whether this version is a release candidate."""
        return self.pre is not None and self.pre[0] == "rc"

    @classmethod
    def from_string(cls, version: str) -> "Version":
        """
        Create a version from a version string

        Args:
            version: Version string to parse

        Raises:
            VersionError: If the version string is invalid.

        Returns:
            A new version instance
        """
        try:
            return cls(version)
        except InvalidVersion as e:
            raise VersionError(e) from None

    @classmethod
    def from_version(cls, version: "Version") -> "Version":
        """
        Convert a version (if necessary)

        This method can be used to convert version instances from different
        versioning schemes.
        """

        if isinstance(version, cls):
            return version

        if version.is_dev_release:
            return cls.from_string(
                f"{version.major}."
                f"{version.minor}."
                f"{version.patch}"
                f".dev{version.dev}"
                f"{'+' + version.local if version.local else ''}"
            )
        if version.is_pre_release:
            return cls.from_string(
                f"{version.major}."
                f"{version.minor}."
                f"{version.patch}"
                f"-{version.pre[0]}{version.pre[1]}"  # type: ignore
                f"{'+' + version.local if version.local else ''}"
            )

        return cls.from_string(str(version))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            # allow to compare against "current" for now
            return False
        if not isinstance(other, Version):
            raise ValueError(f"Can't compare {type(self)} with {type(other)}")
        if not isinstance(other, type(self)):
            other = self.from_version(other)
        return self._version == other._version

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, str):
            # allow to compare against "current" for now
            return True
        if not isinstance(other, Version):
            raise ValueError(f"Can't compare {type(self)} with {type(other)}")
        if not isinstance(other, type(self)):
            other = self.from_version(other)
        return self._version != other._version

    def __str__(self) -> str:
        return str(self._version)


class PEP440VersionCalculator(VersionCalculator):
    version_cls = PEP440Version

    """
    A PEP 440 version calculator
    """

    @classmethod
    def next_dev_version(cls, current_version: Version) -> Version:
        """
        Get the next development version from a valid version

        Examples:
            "1.2.3" will return "1.2.4.dev1"
            "1.2.3.dev1" will return "1.2.3.dev2"
        """
        if current_version.is_dev_release:
            return cls.version_from_string(
                f"{current_version.major}."  # type: ignore
                f"{current_version.minor}."
                f"{current_version.patch}."
                f"dev{current_version.dev + 1}"
            )

        if current_version.is_pre_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}"
                f"{current_version.pre[0]}"  # type: ignore
                f"{current_version.pre[1]}+dev1"  # type: ignore
            )

        return cls.version_from_string(
            f"{current_version.major}."
            f"{current_version.minor}."
            f"{current_version.patch + 1}.dev1"
        )

    @classmethod
    def next_alpha_version(cls, current_version: Version) -> Version:
        """
        Get the next alpha version from a valid version

        Examples:
            "1.2.3" will return "1.2.4a1"
            "1.2.3.dev1" will return "1.2.3a1"
        """
        if current_version.is_dev_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}a1"
            )

        if current_version.is_alpha_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}a"
                f"{current_version.pre[1] + 1}"  # type: ignore
            )

        return cls.version_from_string(
            f"{current_version.major}."
            f"{current_version.minor}."
            f"{current_version.patch + 1}a1"
        )

    @classmethod
    def next_beta_version(cls, current_version: Version) -> Version:
        """
        Get the next beta version from a valid version

        Examples:
            "1.2.3" will return "1.2.4b1"
            "1.2.3.dev1" will return "1.2.3b1"
        """
        if current_version.is_dev_release or current_version.is_alpha_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}b1"
            )

        if current_version.is_beta_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}b"
                f"{current_version.pre[1] + 1}"  # type: ignore
            )
        return cls.version_from_string(
            f"{current_version.major}."
            f"{current_version.minor}."
            f"{current_version.patch + 1}b1"
        )

    @classmethod
    def next_release_candidate_version(
        cls, current_version: Version
    ) -> Version:
        """
        Get the next alpha version from a valid version

        Examples:
            "1.2.3" will return "1.2.4rc1"
            "1.2.3.dev1" will return "1.2.3rc1"
        """
        if (
            current_version.is_dev_release
            or current_version.is_alpha_release
            or current_version.is_beta_release
        ):
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}rc1"
            )

        if current_version.is_release_candidate:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}rc"
                f"{current_version.pre[1] + 1}"  # type: ignore
            )

        return cls.version_from_string(
            f"{current_version.major}."
            f"{current_version.minor}."
            f"{current_version.patch + 1}rc1"
        )


class PEP440VersioningScheme(VersioningScheme):
    """
    PEP 440 versioning scheme
    """

    version_calculator_cls = PEP440VersionCalculator
    version_cls = PEP440Version
