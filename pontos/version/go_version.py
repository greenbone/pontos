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
from typing import Union
from packaging import version

from .helper import (
    VersionError,
    initialize_default_parser,
)

# This class is used for Python Version command(s)
class GoVersionCommand:
    def __init__(self, *, go_mod_path: Path = None) -> None:
        self.go_mod_path = go_mod_path
        if not self.go_mod_path:
            self.go_mod_path = Path.cwd() / 'go.mod'

        if not self.go_mod_path.exists():
            raise VersionError(f'{str(self.go_mod_path)} file not found.')

        self.shell_cmd_runner = lambda x: subprocess.run(
            x,
            shell=True,
            check=True,
            errors="utf-8",  # use utf-8 encoding for error output
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self._configure_parser()

    def _configure_parser(self):
        self.parser = initialize_default_parser()

    def _print(self, *args) -> None:
        if not self.__quiet:
            print(*args)

    def get_current_version(self) -> str:
        try:
            proc = self.shell_cmd_runner(
                'git describe --tags `git rev-list --tags --max-count=1`'
            )
            return str(version.parse(proc.stdout))
        except subprocess.CalledProcessError:
            self._print(
                'No version tag found. Maybe this '
                'module has not been released at all.'
            )

    def print_current_version(self) -> None:
        version_str = self.get_current_version()
        if version_str:
            self._print(version_str)

    def run(self, args=None) -> Union[int, str]:
        args = self.parser.parse_args(args)

        if not getattr(args, 'command', None):
            self.parser.print_usage()
            return 0

        self.__quiet = args.quiet

        if not self.go_mod_path.exists():
            raise VersionError(f'Could not find {str(self.go_mod_path)} file.')

        try:
            if args.command == 'update':
                self._print(
                    'Updating the version of a go module is not possible.'
                )
            elif args.command == 'show':
                self.print_current_version()
            elif args.command == 'verify':
                self._print(
                    'Golang does not provide a file containing the version. '
                    'Thus nothing needs to be verified.'
                )
        except VersionError as e:
            return str(e)
