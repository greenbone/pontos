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
This script prints out all members existing in the space of the given
organization
"""

from argparse import ArgumentParser, Namespace
from typing import Union

from rich.console import Console
from rich.table import Table

from pontos.github.api import GitHubAsyncRESTApi
from pontos.github.api.organizations import MemberFilter, MemberRole


def member_filter_type(value: Union[str, MemberFilter]) -> MemberFilter:
    if isinstance(value, MemberFilter):
        return value
    return MemberFilter[value.upper()]


def member_role_type(value: Union[str, MemberRole]) -> MemberRole:
    if isinstance(value, MemberRole):
        return value
    return MemberRole[value.upper()]


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("organization")

    parser.add_argument(
        "-f",
        "--filter",
        type=member_filter_type,
        help=f"Filter members. Choices: "
        f"{', '.join([f.name for f in MemberFilter])}. Default: %(default)s",
        default=MemberFilter.ALL.name,
    )

    parser.add_argument(
        "-r",
        "--role",
        type=member_role_type,
        help=f"Show only members in specific role. Choices: "
        f"{', '.join([f.name for f in MemberRole])}. Default: %(default)s",
        default=MemberRole.ALL.name,
    )


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    table = Table()
    table.add_column("Name")
    table.add_column("URL")

    member_count = 0
    async for user in api.organizations.members(
        args.organization, member_filter=args.filter, role=args.role
    ):
        table.add_row(
            user.login,
            f"[link={user.html_url}]{user.html_url}[/link]",
        )
        member_count += 1

    console = Console()
    console.print(table)

    print(f"{member_count} members.")
    return 0
