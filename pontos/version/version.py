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

from pathlib import Path
from typing import Union

from .helper import (
    VersionError,
    initialize_default_parser,
)


class VersionCommand:
    """Generic class usable to implement the
    version commands for several programming languages"""

    __quiet = False

    def __init__(
        self, *, version_file_path: Path = None, project_file_path: Path = None
    ):
        # use this for a version file, e.g. used by
        # Greenbone in javascript or python
        self.version_file_path = version_file_path

        # this file should determine the type of
        # programming language used in the repository
        self.project_file_path = project_file_path

        self.parser = initialize_default_parser()

    def _print(self, *args) -> None:
        if not self.__quiet:
            print(*args)

    def get_current_version(self) -> str:
        """Get the current version of this project"""
        # implementme.

    def verify_version(self, version: str) -> None:
        """Verify the current version of this project"""
        # implementme.

    def update_version(
        self, new_version: str, *, develop: bool = False, force: bool = False
    ) -> None:
        """Update the current version of this project"""
        # implementme.

    def print_current_version(self) -> None:
        self._print(self.get_current_version())

    def run(self, args=None) -> Union[int, str]:
        args = self.parser.parse_args(args)

        if not getattr(args, 'command', None):
            self.parser.print_usage()
            return 0

        self.__quiet = args.quiet

        if not self.project_file_path.exists():
            raise VersionError(
                f'Could not find {str(self.project_file_path)} file.'
            )

        try:
            if args.command == 'update':
                self.update_version(
                    args.version, force=args.force, develop=args.develop
                )
            elif args.command == 'show':
                self.print_current_version()
            elif args.command == 'verify':
                self.verify_version(args.version)
        except VersionError as e:
            return str(e)

        return 0
