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
This script locks a branch in a repo of an organization via branch protection
"""

from argparse import ArgumentParser, BooleanOptionalAction, Namespace

from pontos.github.api import GitHubAsyncRESTApi
from pontos.github.api.branch import update_from_applied_settings


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("repository", help="org/repo combination")
    parser.add_argument("branch", help="branch to use")
    parser.add_argument(
        "--allow",
        action=BooleanOptionalAction,
        help="Allow/disallow admin users to bypass the branch protection rules",
    )


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    branch_protection = await api.branches.protection_rules(
        args.repository, args.branch
    )
    if args.allow:
        enforce_admins = False
    else:
        enforce_admins = True

    kwargs = update_from_applied_settings(
        branch_protection, enforce_admins=enforce_admins
    )
    await api.branches.update_protection_rules(
        args.repository,
        args.branch,
        **kwargs,
    )
    if args.allow:
        print(
            f"Allowed admins to bypass the branch protection rules for branch "
            f"{args.branch} in {args.repository} now."
        )
    else:
        print(
            f"Admin users are not allowed to bypass the branch protection "
            f"rules for branch {args.branch} in {args.repository} now."
        )
    return 0
