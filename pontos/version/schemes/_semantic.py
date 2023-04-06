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

import re
from typing import Any, Optional, Tuple

from semver import VersionInfo

from .._calculator import VersionCalculator
from ..errors import VersionError
from ..version import Version
from ._scheme import VersioningScheme

# Note: This regex currently support any kind of
# word-number combination for pre releases
_PRE_RELEASE_REGEXP = re.compile(
    r"^(?P<name>[a-zA-Z]+)(?P<version>0|[1-9][0-9]*)"
    r"(?:-(?P<extra>[a-zA-Z]+)(?P<extra_version>0|[1-9][0-9]*))?$"
)


class SemanticVersion(Version):
    """
    A Version implementation based on
    `Semantic Versioning<https://semver.org/>`_
    """

    def __init__(
        self,
        version: str,
    ) -> None:
        self._version_info = VersionInfo.parse(version)
        self._parse_build()
        self._parse_pre_release()

    def _parse_pre_release(self) -> None:
        self._dev = None
        self._pre_release = None

        if self._version_info.prerelease:
            match = _PRE_RELEASE_REGEXP.match(self._version_info.prerelease)
            if not match:
                raise VersionError(
                    f"Invalid prerelease {self._version_info.prerelease} in "
                    f"{self._version_info}"
                )

            name = match.group("name")
            version = int(match.group("version"))

            if name == "dev":
                self._dev = version
            else:
                self._pre_release = (
                    name,
                    version,
                )

            extra = match.group("extra")
            if extra == "dev":
                if name == "dev":
                    raise VersionError(
                        f"Invalid prerelease {self._version_info.prerelease} "
                        f"in {self._version_info}"
                    )
                self._dev = int(match.group("extra_version"))

    def _parse_build(self) -> None:
        self._build = None
        if self._version_info.build:
            match = _PRE_RELEASE_REGEXP.match(self._version_info.build)
            if match:
                self._build = (
                    match.group("name"),
                    int(match.group("version")),
                )

    @property
    def pre(self) -> Optional[Tuple[str, int]]:
        """The pre-release segment of the version."""
        return self._pre_release

    @property
    def dev(self) -> Optional[int]:
        """The development number of the version."""
        return self._dev

    @property
    def local(self) -> Optional[Tuple[str, int]]:
        """The local version segment of the version."""
        return self._build

    @property
    def is_pre_release(self) -> bool:
        """
        Whether this version is a pre-release (alpha, beta, release candidate).
        """
        return self._pre_release is not None

    @property
    def is_dev_release(self) -> bool:
        """Whether this version is a development release."""
        return self._dev is not None

    @property
    def is_alpha_release(self) -> bool:
        """Whether this version is a alpha release."""
        return self.is_pre_release and self.pre[0] == "alpha"

    @property
    def is_beta_release(self) -> bool:
        """Whether this version is a beta release."""
        return self.is_pre_release and self.pre[0] == "beta"

    @property
    def is_release_candidate(self) -> bool:
        """Whether this version is a release candidate."""
        return self.is_pre_release and self.pre[0] == "rc"

    @property
    def major(self) -> int:
        """The first item of :attr:`release` or ``0`` if unavailable."""
        return self._version_info.major

    @property
    def minor(self) -> int:
        """The second item of :attr:`release` or ``0`` if unavailable."""
        return self._version_info.minor

    @property
    def patch(self) -> int:
        """The third item of :attr:`release` or ``0`` if unavailable."""
        return self._version_info.patch

    def __eq__(self, other: Any) -> bool:
        if other is None:
            return False
        if isinstance(other, str):
            # allow to compare against "current" for now
            return False
        if not isinstance(other, Version):
            raise ValueError(f"Can't compare {type(self)} with {type(other)}")
        if not isinstance(other, type(self)):
            other = self.from_version(other)

        return (
            self._version_info == other._version_info
            and self._version_info.build == other._version_info.build
        )

    def __ne__(self, other: Any) -> bool:
        if other is None:
            return True
        if isinstance(other, str):
            # allow to compare against "current" for now
            return True
        if not isinstance(other, Version):
            raise ValueError(f"Can't compare {type(self)} with {type(other)}")
        if not isinstance(other, type(self)):
            other = self.from_version(other)

        return (
            self._version_info != other._version_info
            or self._version_info.build != other._version_info.build
        )

    def __str__(self) -> str:
        """A string representation of the version"""
        return str(self._version_info)

    @classmethod
    def from_string(cls, version: str) -> "SemanticVersion":
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
        except ValueError as e:
            raise VersionError(e) from None

    @classmethod
    def from_version(cls, version: "Version") -> "SemanticVersion":
        """
        Convert a version (if necessary)

        This method can be used to convert version instances from different
        versioning schemes.
        """

        if isinstance(version, cls):
            return version

        version_local = (
            f"+{version.local[0]}{version.local[1]}" if version.local else ""
        )
        if version.is_dev_release:
            if not version.pre:
                return cls.from_string(
                    f"{version.major}."
                    f"{version.minor}."
                    f"{version.patch}"
                    f"-dev{version.dev}"
                    f"{version_local}"
                )

            return cls.from_string(
                f"{version.major}."
                f"{version.minor}."
                f"{version.patch}"
                f"-{version.pre[0]}{version.pre[1]}"
                f"-dev{version.dev}"
            )
        if version.is_alpha_release:
            return cls.from_string(
                f"{version.major}."
                f"{version.minor}."
                f"{version.patch}"
                f"-alpha{version.pre[1]}"
                f"{version_local}"
            )
        if version.is_beta_release:
            return cls.from_string(
                f"{version.major}."
                f"{version.minor}."
                f"{version.patch}"
                f"-beta{version.pre[1]}"
                f"{version_local}"
            )
        if version.is_pre_release:
            return cls.from_string(
                f"{version.major}."
                f"{version.minor}."
                f"{version.patch}"
                f"-{version.pre[0]}{version.pre[1]}"
                f"{version_local}"
            )

        return cls.from_string(str(version))


# pylint: disable=protected-access
class SemanticVersionCalculator(VersionCalculator):
    version_cls = SemanticVersion

    @classmethod
    def next_dev_version(cls, current_version: Version) -> Version:
        """
        Get the next development version from a valid version
        """
        if current_version.is_dev_release:
            if current_version.pre:
                return cls.version_from_string(
                    f"{current_version.major}."
                    f"{current_version.minor}."
                    f"{current_version.patch}"
                    f"-{current_version.pre[0]}{current_version.pre[1]}"
                    f"-dev{current_version.dev + 1}"
                )
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}"
                f"-dev{current_version.dev + 1}"
            )

        if current_version.is_pre_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}-"
                f"{current_version.pre[0]}{current_version.pre[1] + 1}-dev1"
            )

        return cls.version_from_string(
            f"{current_version.major}."
            f"{current_version.minor}."
            f"{current_version.patch + 1}"
            "-dev1"
        )

    @classmethod
    def next_alpha_version(cls, current_version: Version) -> Version:
        """
        Get the next alpha version from a valid version
        """
        if current_version.is_dev_release:
            if current_version.pre:
                if current_version.pre[0] == "alpha":
                    return cls.version_from_string(
                        f"{current_version.major}."
                        f"{current_version.minor}."
                        f"{current_version.patch}"
                        f"-alpha{current_version.pre[1]}"
                    )
                return cls.version_from_string(
                    f"{current_version.major}."
                    f"{current_version.minor}."
                    f"{current_version.patch + 1}-alpha1"
                )
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}-alpha1"
            )
        if current_version.is_alpha_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}"
                f"-alpha{current_version.pre[1] + 1}"
            )
        return cls.version_from_string(
            f"{current_version.major}."
            f"{current_version.minor}."
            f"{current_version.patch + 1}"
            "-alpha1"
        )

    @classmethod
    def next_beta_version(cls, current_version: Version) -> Version:
        """
        Get the next alpha version from a valid version
        """
        if current_version.is_dev_release and current_version.pre:
            if current_version.pre[0] == "beta":
                return cls.version_from_string(
                    f"{current_version.major}."
                    f"{current_version.minor}."
                    f"{current_version.patch}"
                    f"-beta{current_version.pre[1]}"
                )
            if current_version.pre[0] == "rc":
                return cls.version_from_string(
                    f"{current_version.major}."
                    f"{current_version.minor}."
                    f"{current_version.patch + 1}-beta1"
                )
        if current_version.is_dev_release or current_version.is_alpha_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}"
                "-beta1"
            )
        if current_version.is_beta_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}"
                f"-beta{current_version.pre[1] + 1}"
            )
        return cls.version_from_string(
            f"{current_version.major}."
            f"{current_version.minor}."
            f"{current_version.patch + 1}"
            "-beta1"
        )

    @classmethod
    def next_release_candidate_version(
        cls, current_version: Version
    ) -> Version:
        """
        Get the next release candidate version from a valid version
        """
        if current_version.is_dev_release:
            if current_version.pre and current_version.pre[0] == "rc":
                return cls.version_from_string(
                    f"{current_version.major}."
                    f"{current_version.minor}."
                    f"{current_version.patch}"
                    f"-rc{current_version.pre[1]}"
                )
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}-rc1"
            )
        if current_version.is_alpha_release or current_version.is_beta_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}-rc1"
            )
        if current_version.is_release_candidate:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}"
                f"-rc{current_version.pre[1] + 1}"
            )
        return cls.version_from_string(
            f"{current_version.major}."
            f"{current_version.minor}."
            f"{current_version.patch + 1}"
            "-rc1"
        )


class SemanticVersioningScheme(VersioningScheme):
    version_cls = SemanticVersion
    version_calculator_cls = SemanticVersionCalculator
