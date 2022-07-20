# Copyright (C) 2020-2022 Greenbone Networks GmbH
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
#

from argparse import Namespace
from pathlib import Path

from pontos.github.api import GitHubRESTApi
from pontos.helper import DownloadProgressIterable, shell_cmd_runner
from pontos.terminal import Terminal
from pontos.terminal.terminal import Signs

from .helper import get_current_version, get_project_name, upload_assets


def display_download_progress(
    terminal: Terminal, progress: DownloadProgressIterable
) -> None:
    spinner = ["-", "\\", "|", "/"]
    if progress.length:
        for percent in progress:
            done = int(50 * percent)
            terminal.out(
                f"\r[{'=' * done}{' ' * (50-done)}]", end="", flush=True
            )
    else:
        i = 0
        for _ in progress:
            i = i + 1
            if i == 4:
                i = 0
            terminal.out(f"\r[{spinner[i]}]", end="", flush=True)
    terminal.out(f"\r[{Signs.OK}]{' ' * 50}", end="", flush=True)


def sign(
    terminal: Terminal,
    args: Namespace,
    *,
    token: str,
    **_kwargs,
) -> bool:
    project: str = (
        args.project
        if args.project is not None
        else get_project_name(shell_cmd_runner)
    )
    space: str = args.space
    git_tag_prefix: str = args.git_tag_prefix
    release_version: str = (
        args.release_version
        if args.release_version is not None
        else get_current_version(terminal)
    )
    signing_key: str = args.signing_key

    git_version: str = f"{git_tag_prefix}{release_version}"
    repo = f"{space}/{project}"

    github = GitHubRESTApi(token=token)

    if not github.release_exists(repo, git_version):
        terminal.error(f"Release version {git_version} does not exist.")
        return False

    zip_destination = Path(f"{project}-{release_version}.zip")
    with github.download_release_zip(
        repo, git_version, zip_destination
    ) as zip_progress:
        display_download_progress(terminal, zip_progress)

    tarball_destination = Path(f"{project}-{release_version}.tar.gz")
    with github.download_release_tarball(
        repo, git_version, tarball_destination
    ) as tar_progress:
        display_download_progress(terminal, tar_progress)

    file_paths = [zip_destination, tarball_destination]

    for progress in github.download_release_assets(repo, git_version):
        file_paths.append(progress.destination)
        display_download_progress(terminal, progress)

    for file_path in file_paths:
        terminal.info(f"Signing {file_path}")

        if args.passphrase:
            shell_cmd_runner(
                f"gpg --pinentry-mode loopback --default-key {signing_key}"
                f" --yes --detach-sign --passphrase {args.passphrase}"
                f" --armor {file_path}"
            )
        else:
            shell_cmd_runner(
                f"gpg --default-key {signing_key} --yes --detach-sign --armor "
                f"{file_path}"
            )

    if args.dry_run:
        return True

    github_json = github.release(repo, git_version)
    asset_url = github_json["upload_url"].replace("{?name,label}", "")
    return upload_assets(
        terminal,
        token,
        file_paths,
        asset_url,
    )
