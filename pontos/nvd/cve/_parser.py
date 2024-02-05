# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

import shtab


def cves_parser(args: Optional[Sequence[str]] = None) -> Namespace:
    parser = ArgumentParser()
    shtab.add_argument_to(parser)
    parser.add_argument("--token", help="API key to use for querying.")
    parser.add_argument(
        "--keywords",
        nargs="*",
        help="Search for CVEs containing the keyword in their description.",
    )
    parser.add_argument(
        "--cpe-name", help="Get all CVE information associated with the CPE"
    )
    parser.add_argument(
        "--cvss-v2-vector",
        help="Get all CVE information with the CVSSv2 vector",
    )
    parser.add_argument(
        "--cvss-v3-vector",
        help="Get all CVE information with the CVSSv3 vector",
    )
    parser.add_argument(
        "--source-identifier",
        help="Get all CVE information with the source identifier. For example: "
        "cve@mitre.org",
    )
    parser.add_argument(
        "--number", "-n", metavar="N", help="Request only N CVEs", type=int
    )
    parser.add_argument(
        "--start",
        "-s",
        help="Index of the first CVE to request.",
        type=int,
    )
    return parser.parse_args(args)


def cve_parser(args: Optional[Sequence[str]] = None) -> Namespace:
    parser = ArgumentParser()
    shtab.add_argument_to(parser)
    parser.add_argument("--token", help="API key to use for querying.")
    parser.add_argument("cve_id", metavar="CVE-ID", help="ID of the CVE")
    return parser.parse_args(args)
