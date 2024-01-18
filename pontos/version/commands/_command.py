# Copyright (C) 2023 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal, Union

from .._version import Version, VersionUpdate
from ..schemes import VersioningScheme


class VersionCommand(ABC):
    """Generic class usable to implement the
    version commands for several programming languages"""

    project_file_name: str

    def __init__(
        self, versioning_scheme: Union[VersioningScheme, type[VersioningScheme]]
    ) -> None:
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
