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
    parser.add_argument("artifact", help="ID of the artifact to download")
    parser.add_argument(
        "--file",
        help="File to write the artifact to. Default: %(default)s",
        default="out.file",
        type=Path,
    )


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    with args.file.open("wb") as f, Progress() as rich_progress:
        task_id = rich_progress.add_task(
            f"[red]Downloading Artifact {args.artifact}... ", total=None
        )
        async with api.artifacts.download(
            args.repository, args.artifact
        ) as download:
            async for content, progress in download:
                rich_progress.advance(task_id, progress or 1)
                f.write(content)

            rich_progress.update(task_id, total=1, completed=1)
