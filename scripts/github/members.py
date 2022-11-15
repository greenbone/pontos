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
from pontos.github.models.base import User


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("organization")


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    async for member in api.organizations.members(args.organization):
        print(User.from_dict(member))

    return 0
