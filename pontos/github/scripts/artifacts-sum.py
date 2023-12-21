# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
This script prints out all artifacts of a given repository
"""

from argparse import ArgumentParser, Namespace

from rich.console import Console

from pontos.github.api import GitHubAsyncRESTApi


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("repository")


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    count = 0
    expired = 0
    size = 0.0
    async for artifact in api.artifacts.get_all(args.repository):
        count += 1
        if artifact.expired:
            expired += 1
            continue

        size += artifact.size_in_bytes / (1024 * 1024)

    console = Console()
    console.print(f"{count} artifacts.")
    console.print(f"{expired} expired.")
    console.print(f"Size {size:.2f} MiB")

    return 0
