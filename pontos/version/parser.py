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
    parser.add_argument(
        "--quiet", help="don't print messages", action="store_true"
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="additional help",
        dest="command",
    )

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("version", help="version string to compare")
    subparsers.add_parser("show")

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("version", help="version string to use")
    update_parser.add_argument(
        "--force",
        help="don't check if version is already set",
        action="store_true",
    )
    update_parser.add_argument(
        "--develop",
        help="indicates if it is a develop version",
        action="store_true",
    )
    return parser
