# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional


class Version(ABC):
    """
    An abstract base class for version information

    A version implementation must consider the following constraints:

    * Version strings containing `-dev`, and `.dev` are considered development
      versions.
    * Version strings containing `+dev` are not considered as development
      versions.
    * Development versions are are also pre releases. The following version
      string is a development version and a pre release: `1.2.3-alpha1-dev1`
    * A version must return a pre for development versions for version strings
      containing a pre release version like `1.2.3-alpha1-dev1`
    * A development version has no local part
    * Alpha, Beta, Release Candidate and Development versions are pre releases
    * Alpha, Beta and Release Candidate versions pre must return the following
      names for the first value in the tuple: `alpha`, `beta`, `rc` and `dev`
    """

    def __init__(self, original_version: str) -> None:
        self._parsed_version = original_version

    @property
    def parsed_version(self) -> str:
        """
        Original version string from which the version has been parsed
        """
        return self._parsed_version

    @property
    @abstractmethod
    def major(self) -> int:
        """The first item of the version or ``0`` if unavailable."""

    @property
    @abstractmethod
    def minor(self) -> int:
        """The second item of the version or ``0`` if unavailable."""

    @property
    @abstractmethod
    def patch(self) -> int:
        """The third item of the version or ``0`` if unavailable."""

    @property
    @abstractmethod
    def pre(self) -> Optional[tuple[str, int]]:
        """The pre-release segment of the version."""

    @property
    @abstractmethod
    def dev(self) -> Optional[int]:
        """The development number of the version."""

    @property
    @abstractmethod
    def local(self) -> Optional[tuple[str, int]]:
        """The local version segment of the version."""

    @property
    @abstractmethod
    def is_pre_release(self) -> bool:
        """
        Whether this version is a pre-release (alpha, beta, release candidate).
        """

    @property
    @abstractmethod
    def is_dev_release(self) -> bool:
        """Whether this version is a development release."""

    @property
    @abstractmethod
    def is_alpha_release(self) -> bool:
        """Whether this version is an alpha release."""

    @property
    @abstractmethod
    def is_beta_release(self) -> bool:
        """Whether this version is a beta release."""

    @property
    @abstractmethod
    def is_release_candidate(self) -> bool:
        """Whether this version is a release candidate."""

    @classmethod
    @abstractmethod
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

    @classmethod
    @abstractmethod
    def from_version(cls, version: "Version") -> "Version":
        """
        Convert a version (if necessary)

        This method can be used to convert version instances from different
        versioning schemes.
        """

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __ne__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __gt__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __ge__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __le__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __str__(self) -> str:
        """A string representation of the version"""

    # --- Added for Ruff PLW1641 compliance ---
    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError  # pragma: no cover


    def __repr__(self) -> str:
        """A representation of the Version"""
        return f"<{self.__class__.__name__}('{self}')>"


ParseVersionFuncType = Callable[[str], Version]


@dataclass
class VersionUpdate:
    """
    Represents a version update from a previous version to a new version.

    If previous and new are equal the version was not updated and changed_files
    should be empty.

    If there is no previous version for example in an initial release previous
    should be None.

    Example:
        .. code-block:: python

            from pathlib import Path
            from python.version import Version, VersionUpdate

            update = VersionUpdate(
                previous=Version("1.2.3"),
                new=Version("2.0.0"),
                changed_files=[Path("package.json"), Path("version.js")],
            )
    """

    previous: Optional[Version]
    new: Version
    changed_files: list[Path] = field(default_factory=list)

    @property
    def is_update(self) -> bool:
        return self.previous != self.new
