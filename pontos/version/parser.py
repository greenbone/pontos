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

import argparse
from typing import Literal, Union

from pontos.version.version import Version, parse_version


def verify_version_type(version: str) -> Union[Version, Literal["current"]]:
    if version == "current":
        return version

    return parse_version(version)


def initialize_default_parser() -> argparse.ArgumentParser:
    """
    Returns a default argument parser containing:
    - verify
    - show
    - update
    """
    parser = argparse.ArgumentParser(
        description="Version handling utilities.",
        prog="version",
    )
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="Valid subcommands",
        help="Additional help",
        dest="command",
        required=True,
    )

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument(
        "version", help="Version string to compare", type=verify_version_type
    )
    subparsers.add_parser("show")

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument(
        "version", help="Version string to use", type=parse_version
    )
    update_parser.add_argument(
        "--force",
        help="Don't check if version is already set. "
        "This will override existing version information!",
        action="store_true",
    )
    return parser
