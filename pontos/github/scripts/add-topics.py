# Copyright (C) 2022 Greenbone AG
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

from pontos.github.api import GitHubAsyncRESTApi


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("organization", help="owner")
    parser.add_argument("repository", nargs="*", help="repo")
    parser.add_argument("--topics", nargs="*", help="new topics to set")


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    for repository in args.repository:
        topics = set(
            await api.repositories.topics(f"{args.organization}/{repository}")
        )
        topics = topics.union(args.topics)
        print(topics)
        topics = await api.repositories.update_topics(
            f"{args.organization}/{repository}", topics
        )

        print(f"{args.organization}/{repository}: ", end="")
        for topic in topics:
            print(f"{topic} ", end="")
        print()

    return 0
