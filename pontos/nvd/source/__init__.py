# SPDX-FileCopyrightText: 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from argparse import Namespace

from pontos.nvd.source.api import SourceApi

from ._parser import parse_args

__all__ = ("SourceApi",)


async def query_changes(args: Namespace) -> None:
    async with SourceApi(token=args.token) as api:
        async for source in api.sources(
            source_identifier=args.source_identifier,
            request_results=args.number,
            start_index=args.start,
        ):
            print(source)


def main() -> None:
    try:
        args = parse_args()
        asyncio.run(query_changes(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
