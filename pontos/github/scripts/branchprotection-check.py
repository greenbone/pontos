# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from argparse import ArgumentParser, Namespace

from pontos.github.api import GitHubAsyncRESTApi


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("repo")
    parser.add_argument("branch")


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    # draft script for checking the branch protection
    branch_protection = await api.branches.protection_rules(
        args.repo, args.branch
    )
    if branch_protection:
        print(
            f"Branch protection enabled for the '{args.branch}' branch of the '{args.repo}' repository."
        )
        return 0
    else:
        print(
            f"Branch protection NOT enabled for the '{args.branch}' branch of the '{args.repo}' repository."
        )
        return 1
