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
This script adds team(s) to a list of repositories of an organization
"""

import asyncio
from argparse import ArgumentParser, FileType, Namespace
from io import TextIOWrapper
from typing import List, Set, Union

from httpx import HTTPStatusError

from pontos.github.api import GitHubAsyncRESTApi
from pontos.github.models.base import Permission


def permission_type(value: Union[str, Permission]) -> Permission:
    return value if isinstance(value, Permission) else Permission[value.upper()]


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--teams", nargs="+", help="Team(s) to give access to the repositories."
    )
    parser.add_argument(
        "--organization",
        default="greenbone",
        help="GitHub Organization to use. Default: %(default)s.",
    )
    parser.add_argument(
        "--fail-fast",
        "--failfast",
        dest="failfast",
        action="store_true",
        help="Stop on first error instead of continuing.",
    )
    parser.add_argument(
        "--permission",
        type=permission_type,
        help=f"Permission to grant the team(s) on the repositories. Choices: "
        f"{', '.join([f.name for f in Permission])}. Default: %(default)s.",
        default=Permission.PULL.name,
    )

    repo_group = parser.add_mutually_exclusive_group(required=True)
    repo_group.add_argument(
        "--repositories",
        nargs="+",
        help="List of repositories to give the team(s) access to.",
    )
    repo_group.add_argument(
        "--repositories-file",
        dest="file",
        help="File to read a list of repositories from. The file needs to "
        "contain one repository per line. '-' to read from stdin.",
        type=FileType("r"),
    )


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    if args.file:
        file: TextIOWrapper = args.file
        repositories = [line.strip() for line in file.readlines()]
    else:
        repositories: List[str] = args.repositories

    tasks = []
    for team in args.teams:
        for repo in repositories:
            tasks.append(
                asyncio.create_task(
                    api.teams.add_permission(
                        args.organization, team, repo, args.permission
                    )
                )
            )

    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_EXCEPTION
        if args.failfast
        else asyncio.ALL_COMPLETED,
    )
    pending: Set[asyncio.Task]

    # if pending contains tasks an error occurred and fail fast was set.
    # therefore cancel pending tasks.
    for task in pending:
        task.cancel()

    has_error = False

    for task in done | pending:
        try:
            await task
        except HTTPStatusError as e:
            has_error = True
            print(e)
        except asyncio.CancelledError:
            pass

    return 0 if not has_error else 1
