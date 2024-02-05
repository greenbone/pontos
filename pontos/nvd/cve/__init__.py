# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
from argparse import Namespace
from typing import Callable

import httpx

from pontos.nvd.cve.api import CVEApi

from ._parser import cve_parser, cves_parser

__all__ = ("CVEApi",)


async def query_cves(args: Namespace) -> None:
    async with CVEApi(token=args.token) as api:
        async for cve in api.cves(
            keywords=args.keywords,
            cpe_name=args.cpe_name,
            cvss_v2_vector=args.cvss_v2_vector,
            cvss_v3_vector=args.cvss_v3_vector,
            source_identifier=args.source_identifier,
            request_results=args.number,
            start_index=args.start,
        ):
            print(cve)


async def query_cve(args: Namespace) -> None:
    async with CVEApi(token=args.token) as api:
        cve = await api.cve(args.cve_id)
        print(cve)


def cves_main() -> None:
    main(cves_parser(), query_cves)


def cve_main() -> None:
    main(cve_parser(), query_cve)


def main(args: Namespace, func: Callable) -> None:
    try:
        asyncio.run(func(args))
    except KeyboardInterrupt:
        pass
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error {e.response.status_code}: {e.response.text}")
