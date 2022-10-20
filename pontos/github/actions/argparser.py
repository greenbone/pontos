# Copyright (C) 2022 Greenbone Networks GmbH
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

""" Argument parser for pontos-github-actions """

from argparse import ArgumentParser, Namespace
from typing import List

from .cmds import actions_input, actions_output


def split_pairs(value: str):
    if not "=" in value:
        raise ValueError(f"Must contain a 'name=value' pair not '{value}'.")
    return tuple(value.split("=", 1))


def parse_args(
    args: List[str] = None,
) -> Namespace:
    """
    Parsing args for Pontos GitHub Actions
    """

    parser = ArgumentParser(
        description="Greenbone GitHub Actions API.",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Don't print messages to the terminal",
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        required=True,
        help="additional help",
        dest="command",
    )

    output_parser = subparsers.add_parser("output", help="Set output variables")
    output_parser.add_argument(
        "output", help="Output as name=value pairs", type=split_pairs, nargs="+"
    )

    output_parser.set_defaults(func=actions_output)

    input_parser = subparsers.add_parser("input", help="Print input variables")
    input_parser.add_argument(
        "input",
        help="Name of the input variable to print",
        nargs="+",
    )
    input_parser.add_argument("--format", choices=["json"])

    input_parser.set_defaults(func=actions_input)

    return parser.parse_args(args)
