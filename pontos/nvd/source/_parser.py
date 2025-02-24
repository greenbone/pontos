# SPDX-FileCopyrightText: 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

import shtab


def parse_args(args: Optional[Sequence[str]] = None) -> Namespace:
    parser = ArgumentParser()
    shtab.add_argument_to(parser)
    parser.add_argument("--token", help="API key to use for querying.")
    parser.add_argument(
        "--source-identifier",
        help="Get sources record for this source identifier",
    )
    parser.add_argument(
        "--number", "-n", metavar="N", help="Request only N sources", type=int
    )
    parser.add_argument(
        "--start",
        "-s",
        help="Index of the first source to request.",
        type=int,
        default=0,
    )
    return parser.parse_args(args)
