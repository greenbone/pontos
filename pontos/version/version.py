# Copyright (C) 2020-2022 Greenbone AG
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
from pathlib import Path
from typing import Literal, Union

from packaging.version import InvalidVersion
from packaging.version import Version as PackagingVersion

from .errors import VersionError


class Version(PackagingVersion):
    """
    A class handling version information
    """


def parse_version(version: str) -> Version:
    """
    Parse a Version from a string

    Args:
        version: Version string to convert into a Version instance

    Raises:
        VersionError if the version string is invalid.
    """
    try:
        return Version(version)
    except InvalidVersion as e:
        raise VersionError(e) from None


@dataclass
class VersionUpdate:
    """
    Represents a version update from a previous version to a new version.

    If previous and new are equal the version was not updated and changed_files
    should be empty.

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

    previous: Version
    new: Version
    changed_files: list[Path] = field(default_factory=list)


class VersionCommand(ABC):
    """Generic class usable to implement the
    version commands for several programming languages"""

    project_file_name: str

    def __init__(self) -> None:
        self.project_file_path = Path.cwd() / self.project_file_name

    @abstractmethod
    def get_current_version(self) -> Version:
        """Get the current version of this project"""

    @abstractmethod
    def verify_version(
        self, version: Union[Literal["current"], Version]
    ) -> None:
        """
        Verify the current version of this project

        Args:
            version: Version to check against the current applied version of
                this project. If version is "current" the command should verify
                if all version information is consistent, for example if the
                version information in several files is the same.
        """

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
