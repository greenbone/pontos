# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


from typing import List, Literal, Type, Union

from ._errors import ProjectError
from ._version import Version, VersionUpdate
from .commands import VersionCommand, get_commands
from .schemes import VersioningScheme

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

    def __init__(
        self, versioning_scheme: Union[VersioningScheme, Type[VersioningScheme]]
    ) -> None:
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
