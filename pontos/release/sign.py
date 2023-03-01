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

import asyncio
import subprocess
from argparse import Namespace
from asyncio.subprocess import Process
from enum import IntEnum
from pathlib import Path
from typing import AsyncContextManager, Iterable, Optional

import httpx
from rich.progress import Progress as RichProgress

from pontos.errors import PontosError
from pontos.git.git import GitError
from pontos.github.api import GitHubAsyncRESTApi
from pontos.helper import AsyncDownloadProgressIterable
from pontos.terminal import Terminal
from pontos.terminal.rich import RichTerminal
from pontos.version.helper import get_last_release_version
from pontos.version.version import Version

from .helper import get_git_repository_name


class SignReturnValue(IntEnum):
    SUCCESS = 0
    TOKEN_MISSING = 1
    NO_PROJECT = 2
    NO_RELEASE_VERSION = 3
    NO_RELEASE = 4
    UPLOAD_ASSET_ERROR = 5
    SIGNATURE_GENERATION_FAILED = 6


class SignatureError(PontosError):
    """
    Error while creating a signature
    """


async def cmd_runner(*args: Iterable[str]) -> Process:
    return await asyncio.create_subprocess_exec(
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class SignCommand:
    def __init__(self, terminal: RichTerminal) -> None:
        self.terminal = terminal

    async def _async_download_progress(
        self,
        rich_progress: RichProgress,
        progress: AsyncDownloadProgressIterable[bytes],
        destination: Path,
    ) -> None:
        with destination.open("wb") as f:
            task_description = f"Downloading [blue]{progress.url}"
            task_id = rich_progress.add_task(
                task_description, total=progress.length
            )
            async for content, percent in progress:
                rich_progress.advance(task_id, percent or 1)
                f.write(content)

            rich_progress.update(task_id, total=1, completed=1)

    async def download_zip(
        self,
        rich_progress: RichProgress,
        github: GitHubAsyncRESTApi,
        destination: Path,
        repo: str,
        git_version: str,
    ) -> Path:
        async with github.releases.download_release_zip(
            repo, git_version
        ) as download:
            await self._async_download_progress(
                rich_progress, download, destination
            )
        return destination

    async def download_tar(
        self,
        rich_progress: RichProgress,
        github: GitHubAsyncRESTApi,
        destination: Path,
        repo: str,
        git_version: str,
    ) -> Path:
        async with github.releases.download_release_tarball(
            repo, git_version
        ) as download:
            await self._async_download_progress(
                rich_progress, download, destination
            )
        return destination

    async def download_asset(
        self,
        rich_progress: RichProgress,
        name: str,
        download_cm: AsyncContextManager[AsyncDownloadProgressIterable[bytes]],
    ) -> Path:
        file_path = Path(name)
        async with download_cm as iterator:
            await self._async_download_progress(
                rich_progress, iterator, file_path
            )
        return file_path

    async def sign_file(
        self, file_path: Path, signing_key: str, passphrase: Optional[str]
    ) -> None:
        self.terminal.info(f"Signing {file_path}")

        if passphrase:
            process = await cmd_runner(
                "gpg",
                "--pinentry-mode",
                "loopback",
                "--default-key",
                signing_key,
                "--yes",
                "--detach-sign",
                "--passphrase",
                passphrase,
                "--armor",
                file_path,
            )
        else:
            process = await cmd_runner(
                "gpg",
                "--default-key",
                signing_key,
                "--yes",
                "--detach-sign",
                "--armor",
                file_path,
            )

        _, stderr = await process.communicate()
        if process.returncode:
            raise SignatureError(
                f"Could not create signature for {file_path}. "
                f"{stderr.decode(errors='replace')}"
            )

    async def run(
        self,
        *,
        token: str,
        dry_run: Optional[bool] = False,
        project: Optional[str],
        space: str,
        git_tag_prefix: Optional[str],
        release_version: Optional[Version],
        signing_key: str,
        passphrase: str,
    ) -> SignReturnValue:
        if not token and not dry_run:
            # dry run doesn't upload assets. therefore a token MAY NOT be
            # required # for public repositories.
            self.terminal.error(
                "Token is missing. The GitHub token is required to upload "
                "signature files."
            )
            return SignReturnValue.TOKEN_MISSING

        try:
            project = (
                project if project is not None else get_git_repository_name()
            )
        except GitError:
            self.terminal.error("Could not determine project. {e}")
            return SignReturnValue.NO_PROJECT

        try:
            release_version = (
                release_version
                if release_version is not None
                else get_last_release_version(git_tag_prefix)
            )
        except PontosError as e:
            self.terminal.error(f"Could not determine release version. {e}")
            return SignReturnValue.NO_RELEASE_VERSION

        if not release_version:
            return SignReturnValue.NO_RELEASE_VERSION

        git_version: str = f"{git_tag_prefix}{release_version}"
        repo = f"{space}/{project}"

        async with GitHubAsyncRESTApi(token=token) as github:
            if not await github.releases.exists(repo, git_version):
                self.terminal.error(
                    f"Release version {git_version} does not exist."
                )
                return SignReturnValue.NO_RELEASE

            tasks = []

            zip_destination = Path(f"{project}-{release_version}.zip")
            tarball_destination = Path(f"{project}-{release_version}.tar.gz")

            with self.terminal.progress() as rich_progress:
                tasks.append(
                    asyncio.create_task(
                        self.download_zip(
                            rich_progress,
                            github,
                            zip_destination,
                            repo,
                            git_version,
                        )
                    )
                )
                tasks.append(
                    asyncio.create_task(
                        self.download_tar(
                            rich_progress,
                            github,
                            tarball_destination,
                            repo,
                            git_version,
                        )
                    )
                )

                # pylint: disable=line-too-long
                async for name, download_cm in github.releases.download_release_assets(
                    repo,
                    git_version,
                ):
                    tasks.append(
                        asyncio.create_task(
                            self.download_asset(
                                rich_progress, name, download_cm
                            )
                        )
                    )

                file_paths = await asyncio.gather(*tasks)

            tasks = [
                asyncio.create_task(
                    self.sign_file(file_path, signing_key, passphrase)
                )
                for file_path in file_paths
            ]

            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_EXCEPTION
            )

            has_error = False
            for task in done:
                try:
                    await task
                except (asyncio.CancelledError, asyncio.InvalidStateError):
                    pass
                except SignatureError as e:
                    self.terminal.error(e)
                    has_error = True

            for task in pending:
                # we had an error
                try:
                    task.cancel()
                    await task
                except asyncio.CancelledError:
                    pass

            if has_error:
                return SignReturnValue.SIGNATURE_GENERATION_FAILED

            if dry_run:
                return SignReturnValue.SUCCESS

            upload_files = [
                (Path(f"{str(p)}.asc"), "application/pgp-signature")
                for p in file_paths
            ]
            self.terminal.info(
                f"Uploading assets: {[str(p[0]) for p in upload_files]}"
            )

            try:
                # pylint: disable=line-too-long
                async for uploaded_file in github.releases.upload_release_assets(
                    repo, git_version, upload_files
                ):
                    self.terminal.ok(f"Uploaded: {uploaded_file}")
            except httpx.HTTPStatusError as e:
                self.terminal.error(f"Failed uploading asset {e}.")
                return SignReturnValue.UPLOAD_ASSET_ERROR

        return SignReturnValue.SUCCESS


def sign(
    terminal: Terminal,
    args: Namespace,
    *,
    token: str,
    **_kwargs,
) -> IntEnum:
    return asyncio.run(
        SignCommand(terminal).run(
            token=token,
            dry_run=args.dry_run,
            project=args.project,
            space=args.space,
            git_tag_prefix=args.git_tag_prefix,
            release_version=args.release_version,
            signing_key=args.signing_key,
            passphrase=args.passphrase,
        )
    )
