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
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class UpdatedVersion:
    previous: str
    new: str


class VersionCommand(ABC):
    """Generic class usable to implement the
    version commands for several programming languages"""

    project_file_name: str

    def __init__(self, *, project_file_path: Optional[Path] = None) -> None:
        if project_file_path:
            self.project_file_path = project_file_path
        else:
            self.project_file_path = Path.cwd() / self.project_file_name

    @abstractmethod
    def get_current_version(self) -> str:
        """Get the current version of this project"""

    @abstractmethod
    def verify_version(self, version: str) -> None:
        """Verify the current version of this project"""

    @abstractmethod
    def update_version(
        self, new_version: str, *, develop: bool = False, force: bool = False
    ) -> UpdatedVersion:
        """Update the current version of this project"""

    def project_file_found(self) -> Optional[Path]:
        """
        Returns a path to the project file if a command has detected a
        corresponding project
        """
        return (
            self.project_file_path if self.project_file_path.exists() else None
        )

    def project_found(self) -> bool:
        """
        Returns True if a command has detected a corresponding project
        """
        return bool(self.project_file_found())
