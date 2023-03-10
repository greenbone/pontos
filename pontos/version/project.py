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


from typing import List, Literal, Union

from .commands import VersionCommand, get_commands
from .errors import ProjectError
from .schemes import VersioningScheme
from .version import Version, VersionUpdate

__all__ = ("Project",)


class Project:
    """
    A project for handling versioning

    Example:
        .. code-block:: python

            from pontos.version.scheme import PEP440VersioningScheme
            from pontos.version.project import Project

            project = Project(PEP440VersioningScheme)
    """

    def __init__(self, versioning_scheme: VersioningScheme) -> None:
        """
        Creates a new project instance

        Args:
            versioning_scheme: Scheme for version handling

        Raises:
            ProjectError: If no fitting VersionCommand could be found
        """
        self._versioning_scheme = versioning_scheme
        self._commands = self._gather_commands()

    def _gather_commands(self) -> List[VersionCommand]:
        """
        Initialize the project with the fitting VersionCommands of the current
        working directory

        Raises:
            ProjectError: If no fitting VersionCommand could be found
        """
        commands = []
        for cmd in get_commands():
            command = cmd(versioning_scheme=self._versioning_scheme)
            if command.project_found():
                commands.append(command)

        if not commands:
            raise ProjectError("No project settings file found")

        return commands

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
        update = self._commands[0].update_version(new_version, force=force)
        for cmd in self._commands[1:]:
            next_update = cmd.update_version(new_version, force=force)
            update.changed_files.extend(next_update.changed_files)

        return update

    def get_current_version(self) -> Version:
        """
        Get the current version of the project

        Returns:
            The current version
        """
        return self._commands[0].get_current_version()

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
        for cmd in self._commands:
            cmd.verify_version(version)
