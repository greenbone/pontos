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

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal, Union

from ..schemes import VersioningScheme
from ..version import Version, VersionUpdate


class VersionCommand(ABC):
    """Generic class usable to implement the
    version commands for several programming languages"""

    project_file_name: str

    def __init__(self, versioning_scheme: VersioningScheme) -> None:
        self.project_file_path = Path.cwd() / self.project_file_name
        self.versioning_scheme = versioning_scheme

    @abstractmethod
    def get_current_version(self) -> Version:
        """Get the current version of this project"""

    @abstractmethod
    def verify_version(
        self, version: Union[Literal["current"], Version, None]
    ) -> None:
        """
        Verify the current version of this project

        Args:
            version: Version to check against the current applied version of
                this project. If version is None or "current" the command should
                verify if all version information is consistent, for example if
                the version information in several files is the same.
        """

    @abstractmethod
    def update_version(
        self, new_version: Version, *, force: bool = False
    ) -> VersionUpdate:
        """
        Update the current version of this project

        Args:
            new_version: Use this version in the update
            force: Force updating the version even if the current version is the
                same as the new version

        Returns:
            The version update including the changed files
        """

    def project_found(self) -> bool:
        """
        Returns True if a command has detected a corresponding project
        """
        return self.project_file_path.exists()
