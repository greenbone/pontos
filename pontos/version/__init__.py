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

import sys
from typing import NoReturn

from pontos.version.helper import VersionError, initialize_default_parser
from pontos.version.version import VersionCommand

from .__version__ import __version__
from .cmake import CMakeVersionCommand
from .go import GoVersionCommand
from .javascript import JavaScriptVersionCommand
from .python import PythonVersionCommand

COMMANDS = (
    CMakeVersionCommand,
    GoVersionCommand,
    JavaScriptVersionCommand,
    PythonVersionCommand,
)


def main() -> NoReturn:
    parser = initialize_default_parser()

    found = False
    for cmd in COMMANDS:
        command: VersionCommand = cmd()  # type: ignore
        if command.project_found():
            found = True
            break

    if not found:
        print("No project found.", file=sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if not getattr(args, "command", None):
        parser.print_usage()
        sys.exit(1)

    try:
        if args.command == "update":
            updated = command.update_version(
                args.version, force=args.force, develop=args.develop
            )
            if updated:
                print(
                    f"Updated version from {updated.previous} to {updated.new}."
                )
            else:
                print("Version is already up-to-date.")
        elif args.command == "show":
            print(command.get_current_version())
        elif args.command == "verify":
            command.verify_version(args.version)
    except VersionError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    sys.exit(0)
