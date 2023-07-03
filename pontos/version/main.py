# Copyright (C) 2020-2022 Greenbone AG
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
from enum import IntEnum, auto
from typing import List, NoReturn, Optional

from pontos.errors import PontosError

from .parser import parse_args
from .project import Project
from .schemes import VersioningScheme


class VersionExitCode(IntEnum):
    SUCCESS = 0
    NO_PROJECT = auto()
    UPDATE_ERROR = auto()
    CURRENT_VERSION_ERROR = auto()
    VERIFY_ERROR = auto()
    NEXT_VERSION_ERROR = auto()


def main(args: Optional[List[str]] = None) -> NoReturn:
    parsed_args = parse_args(args)

    try:
        project = Project(parsed_args.versioning_scheme)
    except PontosError:
        print("No project found.", file=sys.stderr)
        sys.exit(VersionExitCode.NO_PROJECT)

    if parsed_args.command == "update":
        try:
            update = project.update_version(
                parsed_args.version, force=parsed_args.force
            )
        except PontosError as e:
            print(str(e), file=sys.stderr)
            sys.exit(VersionExitCode.UPDATE_ERROR)

        if update.new == update.previous:
            print("Version is already up-to-date.")
        else:
            print(f"Updated version from {update.previous} to {update.new}.")
    elif parsed_args.command == "show":
        try:
            print(str(project.get_current_version()))
        except PontosError as e:
            print(str(e), file=sys.stderr)
            sys.exit(VersionExitCode.CURRENT_VERSION_ERROR)
    elif parsed_args.command == "verify":
        try:
            project.verify_version(parsed_args.version)
        except PontosError as e:
            print(str(e), file=sys.stderr)
            sys.exit(VersionExitCode.VERIFY_ERROR)
    elif parsed_args.command == "next":
        scheme: VersioningScheme = parsed_args.versioning_scheme
        calculator = scheme.calculator()
        try:
            current_version = project.get_current_version()
        except PontosError as e:
            print(str(e), file=sys.stderr)
            sys.exit(VersionExitCode.CURRENT_VERSION_ERROR)

        if parsed_args.type == "dev":
            print(calculator.next_dev_version(current_version))
        elif parsed_args.type == "calendar":
            print(calculator.next_calendar_version(current_version))
        elif parsed_args.type == "alpha":
            print(calculator.next_alpha_version(current_version))
        elif parsed_args.type == "beta":
            print(calculator.next_beta_version(current_version))
        elif parsed_args.type == "rc":
            print(calculator.next_release_candidate_version(current_version))
        elif parsed_args.type == "patch":
            print(calculator.next_patch_version(current_version))
        elif parsed_args.type == "minor":
            print(calculator.next_minor_version(current_version))
        elif parsed_args.type == "major":
            print(calculator.next_major_version(current_version))

    sys.exit(VersionExitCode.SUCCESS)
