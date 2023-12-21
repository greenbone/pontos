# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
This script prints out all artifacts of a given repository
"""

from argparse import ArgumentParser, Namespace

from rich.console import Console
from rich.table import Table

from pontos.github.api import GitHubAsyncRESTApi


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("repository")


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    table = Table()
    table.add_column("Name")
    table.add_column("ID")
    table.add_column("URL")
    table.add_column("Updated")
    table.add_column("Expired")
    table.add_column("Size (in KB)", justify="right")

    count = 0
    async for artifact in api.artifacts.get_all(args.repository):
        table.add_row(
            artifact.name,
            str(artifact.id),
            f"[link={artifact.archive_download_url}]"
            f"{artifact.archive_download_url}[/link]",
            str(artifact.updated_at),
            str(artifact.expired),
            f"{artifact.size_in_bytes / 1024:.2f}",
        )
        count += 1

    console = Console()
    console.print(table)

    print(f"{count} artifacts.")
    return 0
