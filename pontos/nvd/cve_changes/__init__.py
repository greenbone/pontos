# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from argparse import ArgumentParser, Namespace

from pontos.nvd.cve_changes.api import CVEChangesApi

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


def parse_args() -> Namespace:
    parser = ArgumentParser()
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
    return parser.parse_args()


def main() -> None:
    try:
        args = parse_args()
        asyncio.run(query_changes(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
