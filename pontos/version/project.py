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


from typing import List, Literal, Union

from pontos.version.commands import get_commands
from pontos.version.errors import ProjectError
from pontos.version.version import Version, VersionCommand, VersionUpdate


class Project:
    def __init__(self, commands: List[VersionCommand]) -> None:
        self._commands = commands

    @classmethod
    def gather_project(cls) -> "Project":
        """
        Get the project with the fitting VersionCommands of the current working
        directory

        Raises:
            ProjectError if no fitting VersionCommand could be found
        """
        commands = []
        for cmd in get_commands():
            command = cmd()
            if command.project_found():
                commands.append(command)

        if not commands:
            raise ProjectError("No project settings file found")

        return cls(commands)

    def update_version(
        self, new_version: Version, *, force: bool = False
    ) -> VersionUpdate:
        update = self._commands[0].update_version(new_version, force=force)
        for cmd in self._commands[1:]:
            next_update = cmd.update_version(new_version, force=force)
            update.changed_files.extend(next_update.changed_files)

        return update

    def get_current_version(self) -> Version:
        return self._commands[0].get_current_version()

    def verify_version(
        self, version: Union[Literal["current"], Version]
    ) -> None:
        for cmd in self._commands:
            cmd.verify_version(version)
