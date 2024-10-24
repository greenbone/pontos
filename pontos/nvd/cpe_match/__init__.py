# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from argparse import Namespace
from typing import Callable

import httpx

from pontos.nvd.cpe_match.api import CPEMatchApi

from ._parser import cpe_match_parse, cpe_matches_parse

__all__ = ("CPEMatchApi",)


async def query_cpe_match(args: Namespace) -> None:
    async with CPEMatchApi(token=args.token) as api:
        cpe_match = await api.cpe_match(args.match_criteria_id)
        print(cpe_match)


async def query_cpe_matches(args: Namespace) -> None:
    async with CPEMatchApi(token=args.token) as api:
        response = api.cpe_matches(
            cve_id=args.cve_id,
            request_results=args.number,
            start_index=args.start,
        )
        async for cpe_match in response:
            print(cpe_match)


def cpe_match_main() -> None:
    main(cpe_match_parse(), query_cpe_match)


def cpe_matches_main() -> None:
    main(cpe_matches_parse(), query_cpe_matches)


def main(args: Namespace, func: Callable) -> None:
    try:
        asyncio.run(func(args))
    except KeyboardInterrupt:
        pass
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error {e.response.status_code}: {e.response.text}")
