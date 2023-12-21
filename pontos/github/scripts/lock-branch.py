# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
This script locks a branch in a repo of an organization via branch protection
"""

from argparse import ArgumentParser, BooleanOptionalAction, Namespace

from pontos.github.api import GitHubAsyncRESTApi
from pontos.github.api.branch import update_from_applied_settings


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("repository", help="org/repo combination")
    parser.add_argument("branch", help="branch to lock")
    parser.add_argument("--lock", action=BooleanOptionalAction, default=True)


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    branch_protection = await api.branches.protection_rules(
        args.repository, args.branch
    )
    kwargs = update_from_applied_settings(
        branch_protection,
        lock_branch=args.lock,
    )
    await api.branches.update_protection_rules(
        args.repository,
        args.branch,
        **kwargs,
    )
    if args.lock:
        print(f"Locked branch {args.branch} in {args.repository}")
    else:
        print(f"Unlocked branch {args.branch} in {args.repository}")
    return 0
