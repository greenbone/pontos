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
    parser.add_argument("repository", help="owner/repo")
    parser.add_argument("topics", nargs="*", help="new topics to set")


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    if not args.topics:
        topics = await api.repositories.topics(args.repository)
    else:
        topics = await api.repositories.update_topics(
            args.repository, args.topics
        )

    for topic in topics:
        print(topic)

    return 0
