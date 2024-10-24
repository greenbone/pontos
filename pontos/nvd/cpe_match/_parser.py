# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

import shtab


def cpe_matches_parse(args: Optional[Sequence[str]] = None) -> Namespace:
    parser = ArgumentParser()
    shtab.add_argument_to(parser)
    parser.add_argument("--token", help="API key to use for querying.")
    parser.add_argument("--cve-id", help="Get matches for a specific CVE")
    parser.add_argument(
        "--number", "-n", metavar="N", help="Request only N matches", type=int
    )
    parser.add_argument(
        "--start",
        "-s",
        help="Index of the first match to request.",
        type=int,
    )
    return parser.parse_args(args)


def cpe_match_parse(args: Optional[Sequence[str]] = None) -> Namespace:
    parser = ArgumentParser()
    shtab.add_argument_to(parser)
    parser.add_argument("--token", help="API key to use for querying.")
    parser.add_argument(
        "--match-criteria-id",
        help="Get the match string with the given matchCriteriaId ",
    )
    return parser.parse_args(args)
