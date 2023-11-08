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

_LOCAL_RELEASE_REGEXP = re.compile(
    r"^(?P<name>[a-zA-Z]+)(?P<version>0|[1-9][0-9]*)$"
)
_PRE_RELEASE_NAME = {"a": "alpha", "b": "beta"}


def _pre_release_name(name: str) -> str:
    return _PRE_RELEASE_NAME.get(name, name)


class PEP440Version(Version):
    """
    A class handling PEP 440 based version information
    """

    def __init__(self, version: str) -> None:
        super().__init__(version)
        self._version = PackagingVersion(version)
        self._parse_local()

    def _parse_local(self):
        self._local = None
        if self._version.local:
            match = _LOCAL_RELEASE_REGEXP.match(self._version.local)
            if match:
                self._local = (
                    match.group("name"),
                    int(match.group("version")),
                )

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
        if not self._version.pre:
            return None

        return (_pre_release_name(self._version.pre[0]), self._version.pre[1])

    @property
    def dev(self) -> Optional[int]:
        """The development number of the version."""
        return self._version.dev

    @property
    def local(self) -> Optional[Tuple[str, int]]:
        """The local version segment of the version."""
        return self._local

    @property
    def is_pre_release(self) -> bool:
        """
        Whether this version is a pre-release (alpha, beta, release candidate
        and development).
        """
        return self._version.is_prerelease

    @property
    def is_dev_release(self) -> bool:
        """Whether this version is a development release."""
        return self._version.is_devrelease

    @property
    def is_alpha_release(self) -> bool:
        """Whether this version is a alpha release."""
        return bool(self.is_pre_release and self.pre and self.pre[0] == "alpha")

    @property
    def is_beta_release(self) -> bool:
        """Whether this version is a beta release."""
        return bool(self.is_pre_release and self.pre and self.pre[0] == "beta")

    @property
    def is_release_candidate(self) -> bool:
        """Whether this version is a release candidate."""
        return bool(self.is_pre_release and self.pre and self.pre[0] == "rc")

    @classmethod
    def from_string(cls, version: str) -> "PEP440Version":
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
    def from_version(cls, version: "Version") -> "PEP440Version":
        """
        Convert a version (if necessary)

        This method can be used to convert version instances from different
        versioning schemes.
        """

        if isinstance(version, cls):
            return version

        try:
            # try to parse the original version string
            return cls.from_string(version.parsed_version)
        except VersionError:
            pass

        version_local = (
            f"+{version.local[0]}{version.local[1]}" if version.local else ""
        )
        if version.is_dev_release:
            if not version.pre:
                new_version = cls.from_string(
                    f"{version.major}."
                    f"{version.minor}."
                    f"{version.patch}"
                    f".dev{version.dev}"
                    f"{version_local}"
                )
            else:
                new_version = cls.from_string(
                    f"{version.major}."
                    f"{version.minor}."
                    f"{version.patch}"
                    f"-{version.pre[0]}{version.pre[1]}"
                    f".dev{version.dev}"
                )
        elif version.is_pre_release:
            new_version = cls.from_string(
                f"{version.major}."
                f"{version.minor}."
                f"{version.patch}"
                f"-{version.pre[0]}{version.pre[1]}"  # type: ignore[index]
                f"{version_local}"
            )
        else:
            new_version = cls.from_string(str(version))

        new_version._parsed_version = version.parsed_version
        return new_version

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
        return self._version == other._version

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
        return self._version != other._version

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise ValueError(f"Can't compare {type(self)} with {type(other)}")
        if not isinstance(other, type(self)):
            other = self.from_version(other)
        return self._version > other._version

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise ValueError(f"Can't compare {type(self)} with {type(other)}")
        if not isinstance(other, type(self)):
            other = self.from_version(other)
        return self._version >= other._version

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise ValueError(f"Can't compare {type(self)} with {type(other)}")
        if not isinstance(other, type(self)):
            other = self.from_version(other)
        return self._version < other._version

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise ValueError(f"Can't compare {type(self)} with {type(other)}")
        if not isinstance(other, type(self)):
            other = self.from_version(other)
        return self._version <= other._version

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
            if current_version.pre:
                return cls.version_from_string(
                    f"{current_version.major}."  # type: ignore[operator]
                    f"{current_version.minor}."
                    f"{current_version.patch}"
                    f"-{current_version.pre[0]}{current_version.pre[1]}"  # type: ignore[index] # noqa: E501
                    f".dev{current_version.dev + 1}"  # type: ignore[operator]
                )
            return cls.version_from_string(
                f"{current_version.major}."  # type: ignore[operator]
                f"{current_version.minor}."
                f"{current_version.patch}"
                f".dev{current_version.dev + 1}"  # type: ignore[operator]
            )

        if current_version.is_pre_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}"
                f"{current_version.pre[0]}{current_version.pre[1] + 1}.dev1"  # type: ignore[index] # noqa: E501
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
            if current_version.pre:
                if current_version.pre[0] == "alpha":
                    return cls.version_from_string(
                        f"{current_version.major}."
                        f"{current_version.minor}."
                        f"{current_version.patch}"
                        f"a{current_version.pre[1]}"
                    )
                return cls.version_from_string(
                    f"{current_version.major}."
                    f"{current_version.minor}."
                    f"{current_version.patch + 1}a1"
                )
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}a1"
            )

        if current_version.is_alpha_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}a{current_version.pre[1] + 1}"  # type: ignore[index] # noqa: E501
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
        if current_version.is_dev_release and current_version.pre:
            if current_version.pre[0] == "beta":
                return cls.version_from_string(
                    f"{current_version.major}."
                    f"{current_version.minor}."
                    f"{current_version.patch}"
                    f"b{current_version.pre[1]}"
                )
            if current_version.pre[0] == "rc":
                return cls.version_from_string(
                    f"{current_version.major}."
                    f"{current_version.minor}."
                    f"{current_version.patch + 1}b1"
                )
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
                f"{current_version.patch}"
                f"b{current_version.pre[1] + 1}"  # type: ignore[index]
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
        Get the next release candidate version from a valid version

        Examples:
            "1.2.3" will return "1.2.4rc1"
            "1.2.3.dev1" will return "1.2.3rc1"
        """
        if current_version.is_dev_release:
            if current_version.pre and current_version.pre[0] == "rc":
                return cls.version_from_string(
                    f"{current_version.major}."
                    f"{current_version.minor}."
                    f"{current_version.patch}"
                    f"rc{current_version.pre[1]}"
                )
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}rc1"
            )

        if current_version.is_alpha_release or current_version.is_beta_release:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}rc1"
            )

        if current_version.is_release_candidate:
            return cls.version_from_string(
                f"{current_version.major}."
                f"{current_version.minor}."
                f"{current_version.patch}rc{current_version.pre[1] + 1}"  # type: ignore[index] # noqa: E501
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
    name = "PEP440"
