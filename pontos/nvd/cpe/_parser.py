# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

import shtab


def cpes_parser(args: Optional[Sequence[str]] = None) -> Namespace:
    parser = ArgumentParser()
    shtab.add_argument_to(parser)
    parser.add_argument("--token", help="API key to use for querying.")
    parser.add_argument(
        "--cpe-match-string",
        help="Search for CPE names that exist in the Official CPE Dictionary.",
    )
    parser.add_argument(
        "--keywords",
        nargs="*",
        help="Search for CPEs containing the keyword in their titles and "
        "references.",
    )
    parser.add_argument(
        "--number", "-n", metavar="N", help="Request only N CPEs", type=int
    )
    parser.add_argument(
        "--start",
        "-s",
        help="Index of the first CPE to request.",
        type=int,
    )
    return parser.parse_args(args)


def cpe_parser(args: Optional[Sequence[str]] = None) -> Namespace:
    parser = ArgumentParser()
    shtab.add_argument_to(parser)
    parser.add_argument("--token", help="API key to use for querying.")
    parser.add_argument(
        "cpe_name_id", metavar="CPE Name ID", help="UUID of the CPE"
    )
    return parser.parse_args(args)
