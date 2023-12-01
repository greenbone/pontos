# Copyright (C) 2022 Greenbone AG
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
from typing import Callable

import httpx

from pontos.nvd.cpe.api import CPEApi

__all__ = ("CPEApi",)


async def query_cpe(args: Namespace) -> None:
    async with CPEApi(token=args.token) as api:
        cpe = await api.cpe(args.cpe_name_id)
        print(cpe)


async def query_cpes(args: Namespace) -> None:
    async with CPEApi(token=args.token) as api:
        response = api.cpes(
            keywords=args.keywords,
            cpe_match_string=args.cpe_match_string,
            request_results=args.number,
            start_index=args.start,
        )
        async for cpe in response:
            print(cpe)


def cpe_main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--token", help="API key to use for querying.")
    parser.add_argument(
        "cpe_name_id", metavar="CPE Name ID", help="UUID of the CPE"
    )

    main(parser, query_cpe)


def cpes_main() -> None:
    parser = ArgumentParser()
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

    main(parser, query_cpes)


def main(parser: ArgumentParser, func: Callable) -> None:
    try:
        args = parser.parse_args()
        asyncio.run(func(args))
    except KeyboardInterrupt:
        pass
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error {e.response.status_code}: {e.response.text}")
