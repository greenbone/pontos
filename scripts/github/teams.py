# Copyright (C) 2022 Greenbone Networks GmbH
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
