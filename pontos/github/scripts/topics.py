# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

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
