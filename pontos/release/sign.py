# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
import hashlib
import subprocess
from argparse import Namespace
from asyncio.subprocess import Process
from enum import IntEnum, auto
from os import PathLike
from pathlib import Path
from typing import AsyncContextManager, Optional, SupportsInt, Union

import httpx
from rich.progress import Progress as RichProgress
from rich.progress import TextColumn

from pontos.errors import PontosError
from pontos.github.api import GitHubAsyncRESTApi
from pontos.helper import AsyncDownloadProgressIterable
from pontos.release.command import AsyncCommand
from pontos.terminal import Terminal
from pontos.version import Version
from pontos.version.helper import get_last_release_version
from pontos.version.schemes import VersioningScheme

from .helper import repository_split


class SignReturnValue(IntEnum):
    """
    Possible return values of SignCommand
    """

    SUCCESS = 0
    TOKEN_MISSING = auto()
    NO_RELEASE_VERSION = auto()
    NO_RELEASE = auto()
    UPLOAD_ASSET_ERROR = auto()
    SIGNATURE_GENERATION_FAILED = auto()
    INVALID_REPOSITORY = auto()


class SignatureError(PontosError):
    """
    Error while creating a signature
    """


async def cmd_runner(*args: Union[str, PathLike[str]]) -> Process:
    return await asyncio.create_subprocess_exec(
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class SignCommand(AsyncCommand):
    """
    A CLI command for signing a release

    Args:
        terminal: A Terminal for output
    """

    async def _async_download_progress(
        self,
        rich_progress: RichProgress,
        progress: AsyncDownloadProgressIterable[bytes],
        destination: Path,
    ) -> None:
        with destination.open("wb") as f:
            task_description = f"Downloading [blue]{progress.url}"
            task_id = rich_progress.add_task(
                task_description,
                total=progress.length,
                sha256="",
            )
            sha256 = hashlib.sha256()
            async for content, percent in progress:
                rich_progress.advance(task_id, percent or 1)
                f.write(content)
                sha256.update(content)

            rich_progress.update(
                task_id, total=1, completed=1, sha256=sha256.hexdigest()
            )

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

    async def async_run(  # type: ignore[override]
        self,
        *,
        token: str,
        repository: str,
        versioning_scheme: VersioningScheme,
        signing_key: str,
        passphrase: str,
        dry_run: Optional[bool] = False,
        git_tag_prefix: Optional[str],
        release_version: Optional[Version],
        release_series: Optional[str] = None,
    ) -> SignReturnValue:
        """
        Sign a release

        Args:
            token: A token for creating a release on GitHub
            repository: GitHub repository (owner/name). Overrides space and
                project.
            versioning_scheme: The versioning scheme to use for version parsing
                and calculation
            dry_run: True to not upload the signature files
            git_tag_prefix: An optional prefix to use for handling a git tag
                from the release version.
            release_version: Optional release version to use. If not set the
                current version will be determined from the project.
            signing_key: A GPG key ID to use for creating signatures.
            passphrase: Passphrase for the signing key
            release_series: Optional release series to use.
                For example: "1.2", "2", "23".
        """
        if not token and not dry_run:
            # dry run doesn't upload assets. therefore a token MAY NOT be
            # required # for public repositories.
            self.print_error(
                "Token is missing. The GitHub token is required to upload "
                "signature files."
            )
            return SignReturnValue.TOKEN_MISSING

        self.terminal.info(f"Using versioning scheme {versioning_scheme.name}")

        try:
            _, project = repository_split(repository)
        except ValueError as e:
            self.print_error(str(e))
            return SignReturnValue.INVALID_REPOSITORY

        try:
            release_version = (
                release_version
                if release_version is not None
                else get_last_release_version(
                    versioning_scheme.parse_version,
                    git_tag_prefix=git_tag_prefix,
                    tag_name=(
                        f"{git_tag_prefix}{release_series}.*"
                        if release_series
                        else None
                    ),
                )
            )
        except PontosError as e:
            self.print_error(f"Could not determine release version. {e}")
            return SignReturnValue.NO_RELEASE_VERSION

        if not release_version:
            return SignReturnValue.NO_RELEASE_VERSION

        git_version: str = f"{git_tag_prefix}{release_version}"

        async with GitHubAsyncRESTApi(token=token) as github:
            if not await github.releases.exists(repository, git_version):
                self.print_error(
                    f"Release version {git_version} does not exist."
                )
                return SignReturnValue.NO_RELEASE

            tasks = []

            zip_destination = Path(f"{project}-{release_version}.zip")
            tarball_destination = Path(f"{project}-{release_version}.tar.gz")

            # terminal can be a NullTerminal here too that doesn't have a
            # progress. this needs to be fixed and the type ignore removed
            # afterwards
            with self.terminal.progress(  # type: ignore[attr-defined]
                additional_columns=[
                    TextColumn("[progress.description]{task.fields[sha256]}"),
                ]
            ) as rich_progress:
                tasks.append(
                    asyncio.create_task(
                        self.download_zip(
                            rich_progress,
                            github,
                            zip_destination,
                            repository,
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
                            repository,
                            git_version,
                        )
                    )
                )

                # pylint: disable=line-too-long
                async for (
                    name,
                    download_cm,
                ) in github.releases.download_release_assets(  # noqa: E501
                    repository,
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
                    self.print_error(e)
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
                async for (
                    uploaded_file
                ) in github.releases.upload_release_assets(  # noqa: E501
                    repository, git_version, upload_files
                ):
                    self.terminal.ok(f"Uploaded: {uploaded_file}")
            except httpx.HTTPStatusError as e:
                self.print_error(f"Failed uploading asset {e}.")
                return SignReturnValue.UPLOAD_ASSET_ERROR

        return SignReturnValue.SUCCESS


def sign(
    args: Namespace,
    *,
    terminal: Terminal,
    error_terminal: Terminal,
    token: Optional[str],
    **_kwargs,
) -> SupportsInt:
    return SignCommand(terminal=terminal, error_terminal=error_terminal).run(
        token=token,
        dry_run=args.dry_run,
        repository=args.repository,
        versioning_scheme=args.versioning_scheme,
        git_tag_prefix=args.git_tag_prefix,
        release_version=args.release_version,
        signing_key=args.signing_key,
        passphrase=args.passphrase,
        release_series=args.release_series,
    )
