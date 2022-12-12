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

import asyncio
from argparse import ArgumentParser, Namespace

from pontos.nvd.cve.api import *


async def query_cves(args: Namespace) -> None:
    async with CVEApi(token=args.token) as api:
        async for cve in api.cves(
            keywords=args.keywords,
            cpe_name=args.cpe_name,
            cvss_v2_vector=args.cvss_v2_vector,
            cvss_v3_vector=args.cvss_v3_vector,
            source_identifier=args.source_identifier,
        ):
            print(cve)


async def query_cve(args: Namespace) -> None:
    async with CVEApi(token=args.token) as api:
        cve = await api.cve(args.cve_id)
        print(cve)


def cves_main() -> None:
    parser = ArgumentParser()
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

    main(parser, query_cves)


def cve_main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--token", help="API key to use for querying.")
    parser.add_argument("cve_id", metavar="CVE-ID", help="ID of the CVE")

    main(parser, query_cve)


def main(parser: ArgumentParser, func: callable) -> None:
    try:
        args = parser.parse_args()
        asyncio.run(func(args))
    except KeyboardInterrupt:
        pass
