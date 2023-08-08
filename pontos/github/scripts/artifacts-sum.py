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
This script prints out all artifacts of a given repository
"""

from argparse import ArgumentParser, Namespace

from rich.console import Console

from pontos.github.api import GitHubAsyncRESTApi


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("repository")


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    count = 0
    expired = 0
    size = 0.0
    async for artifact in api.artifacts.get_all(args.repository):
        count += 1
        if artifact.expired:
            expired += 1
            continue

        size += artifact.size_in_bytes / (1024 * 1024)

    console = Console()
    console.print(f"{count} artifacts.")
    console.print(f"{expired} expired.")
    console.print(f"Size {size:.2f} MiB")

    return 0
