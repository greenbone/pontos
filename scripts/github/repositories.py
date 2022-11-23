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
This script prints out all repositories existing in the space of the given
organization
"""

from argparse import ArgumentParser, Namespace
from typing import Union

from pontos.github.api import GitHubAsyncRESTApi
from pontos.github.api.helper import RepositoryType


def repository_type(value: Union[str, RepositoryType]) -> RepositoryType:
    if isinstance(value, RepositoryType):
        return value
    return RepositoryType[value.upper()]


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("organization")

    parser.add_argument(
        "-t",
        "--type",
        type=repository_type,
        help=f"What type of repositories should be printed? Choices: "
        f"{', '.join([f.name for f in RepositoryType])}. Default: %(default)s",
        default=RepositoryType.ALL.name,
    )


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    repo_count = 0
    async for repo in api.organizations.get_repositories(
        args.organization, repository_type=args.type
    ):
        print(repo, "\n")
        repo_count += 1

    print(f"{repo_count} repositories.")
    return 0
