# Copyright (C) 2021 Greenbone Networks GmbH
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

from pathlib import Path
import subprocess

from .helper import VersionError, strip_version
from .version import VersionCommand

# This class is used for Python Version command(s)
class GoVersionCommand(VersionCommand):
    def __init__(self, *, project_file_path: Path = None) -> None:
        if not project_file_path:
            project_file_path = Path.cwd() / 'go.mod'

        if not project_file_path.exists():
            raise VersionError(f'{str(project_file_path)} file not found.')

        self.shell_cmd_runner = lambda x: subprocess.run(
            x,
            shell=True,
            check=True,
            errors="utf-8",  # use utf-8 encoding for error output
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        super().__init__(
            project_file_path=project_file_path,
        )

    def get_current_version(self) -> str:
        """Get the current version of this project"""
        try:
            proc = self.shell_cmd_runner(
                'git describe --tags `git rev-list --tags --max-count=1`'
            )
            version_str = strip_version(proc.stdout)
            return version_str if version_str is not None else ""
        except subprocess.CalledProcessError:
            self._print(
                'No version tag found. Maybe this '
                'module has not been released at all.'
            )

    def verify_version(self, version_str: str) -> None:
        """Verify the current version of this project"""
        self._print(
            'Golang does not provide a file containing the version. '
            f'Thus {version_str} can not be verified.'
        )

    def update_version(
        self, new_version: str, *, develop: bool = False, force: bool = False
    ) -> None:
        """Update the current version of this project"""
        _ = (new_version, develop, force)
        self._print('Updating the version of a go module is not possible.')
