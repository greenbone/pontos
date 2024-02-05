# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
from argparse import Namespace
from typing import Callable

import httpx

from pontos.nvd.cpe.api import CPEApi

from ._parser import cpe_parser, cpes_parser

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
    main(cpe_parser(), query_cpe)


def cpes_main() -> None:
    main(cpes_parser(), query_cpes)


def main(args: Namespace, func: Callable) -> None:
    try:
        asyncio.run(func(args))
    except KeyboardInterrupt:
        pass
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error {e.response.status_code}: {e.response.text}")
