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
from argparse import Namespace
from enum import IntEnum, auto
from pathlib import Path
from typing import Optional

import httpx

from pontos.errors import PontosError
from pontos.git import Git
from pontos.github.api import GitHubAsyncRESTApi
from pontos.release.prepare import RELEASE_TEXT_FILE
from pontos.terminal import Terminal
from pontos.version.commands import gather_project
from pontos.version.errors import VersionError

from .helper import find_signing_key, get_git_repository_name


class ReleaseReturnValue(IntEnum):
    SUCCESS = 0
    PROJECT_SETTINGS_NOT_FOUND = auto()
    TOKEN_MISSING = auto()
    NO_RELEASE_VERSION = auto()
    CREATE_RELEASE_ERROR = auto()
    UPDATE_VERSION_ERROR = auto()


class ReleaseCommand:
    def __init__(self, terminal: Terminal) -> None:
        self.git = Git()
        self.terminal = terminal

    async def _create_release(self, release_version: str, token: str) -> None:
        self.terminal.info(f"Creating release for {release_version}")

        release_file = Path(RELEASE_TEXT_FILE)
        changelog_text = release_file.read_text(encoding="utf-8")

        github = GitHubAsyncRESTApi(token=token)

        git_version = f"{self.git_tag_prefix}{release_version}"
        repo = f"{self.space}/{self.project}"

        await github.releases.create(
            repo,
            git_version,
            name=f"{self.project} {release_version}",
            body=changelog_text,
        )

        release_file.unlink()

    async def run(
        self,
        *,
        token: str,
        space: str,
        project: Optional[str],
        release_version: Optional[str],
        next_version: Optional[str],
        git_signing_key: str,
        git_remote_name: Optional[str],
        git_tag_prefix: Optional[str],
    ) -> ReleaseReturnValue:
        """
        Create a release

        Args:
            token: A token for creating a release on GitHub
            space: GitHub username or organization. Required for generating
                links in the changelog.
            project: Name of the project to release. If not set it will be
                gathered via the git remote url.
            release_version: Optional release version to use. If not set the
                current version will be determined from the project.
            next_version: Optional version to set after the release.
            git_signing_key: A GPG key ID to use for creating signatures.
            git_remote_name: Name of the git remote to use.
            git_tag_prefix: An optional prefix to use for creating a git tag
                from the release version.
        """
        git_signing_key = (
            git_signing_key
            if git_signing_key is not None
            else find_signing_key(self.terminal)
        )
        self.git_tag_prefix = git_tag_prefix or ""
        self.project = (
            project if project is not None else get_git_repository_name()
        )
        self.space = space

        try:
            command = gather_project()
        except PontosError as e:
            self.terminal.error(f"Unable to determine project settings. {e}")
            return ReleaseReturnValue.PROJECT_SETTINGS_NOT_FOUND

        try:
            if not release_version:
                release_version = command.get_current_version()
        except VersionError as e:
            self.terminal.error(f"Unable to determine release version. {e}")
            return ReleaseReturnValue.NO_RELEASE_VERSION

        if not release_version:
            return ReleaseReturnValue.NO_RELEASE_VERSION

        calculator = command.get_version_calculator()

        next_version = (
            next_version
            if next_version is not None
            else calculator.next_patch_version(release_version)
        )

        self.terminal.info("Pushing changes")
        self.git.push(follow_tags=True, remote=git_remote_name)

        try:
            await self._create_release(release_version, token)
        except httpx.HTTPStatusError as e:
            self.terminal.error(str(e))
            return ReleaseReturnValue.CREATE_RELEASE_ERROR

        commit_msg = [
            "Automatic adjustments after release\n",
            f"* Update to version {next_version}",
        ]

        try:
            updated = command.update_version(next_version, develop=True)
        except VersionError as e:
            self.terminal.error(
                f"Error while updating version after release. {e}"
            )
            return ReleaseReturnValue.UPDATE_VERSION_ERROR

        for f in updated.changed_files:
            self.git.add(f)

        self.git.commit(
            "\n".join(commit_msg), verify=False, gpg_signing_key=git_signing_key
        )

        # pushing the new tag
        self.git.push(follow_tags=True, remote=git_remote_name)

        return ReleaseReturnValue.SUCCESS


def release(
    terminal: Terminal,
    args: Namespace,
    *,
    token: str,
    **_kwargs,
) -> IntEnum:
    if not token:
        terminal.error(
            "Token is missing. The GitHub token is required to create a "
            "release."
        )
        return ReleaseReturnValue.TOKEN_MISSING

    cmd = ReleaseCommand(terminal)
    return asyncio.run(
        cmd.run(
            token=token,
            space=args.space,
            project=args.project,
            release_version=args.release_version,
            git_remote_name=args.git_remote_name,
            git_signing_key=args.git_signing_key,
            git_tag_prefix=args.git_tag_prefix,
            next_version=args.next_version,
        )
    )
