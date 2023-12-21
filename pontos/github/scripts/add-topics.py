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
