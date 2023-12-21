# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from argparse import ArgumentParser, Namespace

from pontos.github.api import GitHubAsyncRESTApi
from pontos.github.api.branch import update_from_applied_settings


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("repo")
    parser.add_argument("branch")


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    # draft script for updating the branch protections
    branch_protection = await api.branches.protection_rules(
        args.repo, args.branch
    )
    # switch required signatures enabled/disabled
    kwargs = update_from_applied_settings(
        branch_protection,
        required_signatures=not (
            branch_protection.required_signatures
            and branch_protection.required_signatures.enabled
        ),
    )
    await api.branches.update_protection_rules(
        args.repo,
        args.branch,
        **kwargs,
    )
    return 0
