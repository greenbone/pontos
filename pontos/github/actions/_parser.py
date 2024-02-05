# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

""" Argument parser for pontos-github-actions """

from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

import shtab

from .cmds import actions_input, actions_output


def split_pairs(value: str):
    if "=" not in value:
        raise ValueError(f"Must contain a 'name=value' pair not '{value}'.")
    return tuple(value.split("=", 1))


def parse_args(args: Optional[Sequence[str]] = None) -> Namespace:
    """
    Parsing args for Pontos GitHub Actions
    """

    parser = ArgumentParser(
        description="Greenbone GitHub Actions API.",
    )
    shtab.add_argument_to(parser)

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
