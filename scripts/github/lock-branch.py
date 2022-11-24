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
