# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser, Namespace
from collections.abc import Sequence

import shtab


def parse_args(args: Sequence[str] | None = None) -> Namespace:
    parser = ArgumentParser()
    shtab.add_argument_to(parser)
    parser.add_argument("--token", help="API key to use for querying.")
    parser.add_argument("--cve-id", help="Get changes for a specific CVE")
    parser.add_argument(
        "--event-name", help="Get all CVE associated with a specific event name"
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
