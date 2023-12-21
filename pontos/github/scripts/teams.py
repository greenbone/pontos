# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
This script prints out all teams existing in the space of the given
organization
"""

from argparse import ArgumentParser, Namespace

from rich.console import Console
from rich.table import Table

from pontos.github.api import GitHubAsyncRESTApi


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("organization")


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    table = Table()
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("URL")
    table.add_column("Privacy")

    count = 0
    async for team in api.teams.get_all(args.organization):
        table.add_row(
            team.name,
            team.description,
            f"[link={team.html_url}]{team.html_url}[/link]",
            team.privacy.value,
        )
        count += 1

    console = Console()
    console.print(table)

    print(f"{count} teams.")
    return 0
