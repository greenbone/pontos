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
        # pylint: disable=line-too-long
        required_signatures=not branch_protection.required_signatures.enabled,
    )
    await api.branches.update_protection_rules(
        args.repo,
        args.branch,
        **kwargs,
    )
    return 0
