# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from argparse import Namespace

from pontos.nvd.cve_changes.api import CVEChangesApi

from ._parser import parse_args

__all__ = ("CVEChangesApi",)


async def query_changes(args: Namespace) -> None:
    async with CVEChangesApi(token=args.token) as api:
        async for cve in api.changes(
            cve_id=args.cve_id,
            event_name=args.event_name,
            request_results=args.number,
            start_index=args.start,
        ):
            print(cve)


def main() -> None:
    try:
        args = parse_args()
        asyncio.run(query_changes(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
