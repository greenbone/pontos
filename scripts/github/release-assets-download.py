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
This script downloads a single artifacts of a given repository
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from rich.progress import Progress

from pontos.github.api import GitHubAsyncRESTApi


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("repository")
    parser.add_argument("tag", help="Release Tag")
    parser.add_argument(
        "--file",
        help="File to write the artifact to. Default: %(default)s",
        default="out.file",
        type=Path,
    )
    parser.add_argument(
        "--type",
        choices=["zip", "tar"],
        help="Download release asset type. Default: %(default)s",
        default="tar",
    )


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    with args.file.open("wb") as f, Progress() as rich_progress:
        task_id = rich_progress.add_task(
            f"[red]Downloading asset for tag {args.tag} as {args.type}... ",
            total=None,
        )
        download_api = (
            api.releases.download_release_tarball
            if args.type == "tar"
            else api.releases.download_release_zip
        )
        async with download_api(args.repository, args.tag) as download:
            async for content, progress in download:
                rich_progress.advance(task_id, progress or 1)
                f.write(content)

            rich_progress.update(task_id, total=1, completed=1)
