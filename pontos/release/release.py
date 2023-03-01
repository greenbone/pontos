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

from pontos.changelog.conventional_commits import ChangelogBuilder
from pontos.errors import PontosError
from pontos.git import Git
from pontos.github.api import GitHubAsyncRESTApi
from pontos.terminal import Terminal
from pontos.version.commands import gather_project
from pontos.version.errors import VersionError
from pontos.version.helper import get_last_release_version
from pontos.version.version import Version, VersionCommand

from .helper import ReleaseType, find_signing_key, get_git_repository_name


class ReleaseReturnValue(IntEnum):
    SUCCESS = 0
    PROJECT_SETTINGS_NOT_FOUND = auto()
    TOKEN_MISSING = auto()
    NO_RELEASE_VERSION = auto()
    ALREADY_TAKEN = auto()
    CREATE_RELEASE_ERROR = auto()
    UPDATE_VERSION_ERROR = auto()
    UPDATE_VERSION_AFTER_RELEASE_ERROR = auto()


class ReleaseCommand:
    def __init__(self, terminal: Terminal) -> None:
        self.git = Git()
        self.terminal = terminal

    def _get_release_version(
        self,
        command: VersionCommand,
        release_type: ReleaseType,
        release_version: Optional[Version],
    ) -> Version:
        current_version = command.get_current_version()
        calculator = command.get_version_calculator()
        if release_type == ReleaseType.CALENDAR:
            return calculator.next_calendar_version(current_version)

        if release_type == ReleaseType.PATCH:
            return calculator.next_patch_version(current_version)

        if release_type == ReleaseType.MINOR:
            return calculator.next_minor_version(current_version)

        if release_type == ReleaseType.MAJOR:
            return calculator.next_major_version(current_version)

        if release_type == ReleaseType.ALPHA:
            return calculator.next_alpha_version(current_version)

        if release_type == ReleaseType.BETA:
            return calculator.next_beta_version(current_version)

        if release_type == ReleaseType.RELEASE_CANDIDATE:
            return calculator.next_release_candidate_version(current_version)

        if not release_version:
            raise VersionError(
                "No release version provided. Either use a different release "
                "strategy or provide a release version."
            )
        return release_version

    def _has_tag(self, git_version: str) -> bool:
        git_tags = self.git.list_tags()
        return git_version in git_tags

    def _create_changelog(
        self, release_version: str, last_release_version: str, cc_config: Path
    ) -> str:
        changelog_builder = ChangelogBuilder(
            space=self.space,
            project=self.project,
            config=cc_config,
            git_tag_prefix=self.git_tag_prefix,
        )

        return changelog_builder.create_changelog(
            last_version=last_release_version,
            next_version=release_version,
        )

    async def _create_release(
        self, release_version: Version, token: str, release_text: str
    ) -> None:
        github = GitHubAsyncRESTApi(token=token)

        git_version = f"{self.git_tag_prefix}{release_version}"
        repo = f"{self.space}/{self.project}"

        await github.releases.create(
            repo,
            git_version,
            name=f"{self.project} {release_version}",
            body=release_text,
            prerelease=release_version.is_prerelease,
        )

    async def run(
        self,
        *,
        token: str,
        space: str,
        project: Optional[str],
        release_type: ReleaseType,
        release_version: Optional[Version],
        next_version: Optional[str],
        git_signing_key: str,
        git_remote_name: Optional[str],
        git_tag_prefix: Optional[str],
        cc_config: Optional[Path],
        local: Optional[bool] = False,
    ) -> ReleaseReturnValue:
        """
        Create a release

        Args:
            token: A token for creating a release on GitHub
            space: GitHub username or organization. Required for generating
                links in the changelog.
            project: Name of the project to release. If not set it will be
                gathered via the git remote url.
            release_type: Type of the release to prepare. Defines the release
                version. PATCH increments the bugfix version. CALENDAR creates
                a new CalVer release version. VERSION uses the provided
                release_version.
            release_version: Optional release version to use. If not set the
                current version will be determined from the project.
            next_version: Optional version to set after the release.
            git_signing_key: A GPG key ID to use for creating signatures.
            git_remote_name: Name of the git remote to use.
            git_tag_prefix: An optional prefix to use for creating a git tag
                from the release version.
            cc_config: A path to a settings file for creating conventional
                commits.
            local: Only create changes locally and don't push changes to
                remote repository. Also don't create a GitHub release.
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
            release_version = self._get_release_version(
                command, release_type, release_version
            )
        except VersionError as e:
            self.terminal.error(f"Unable to determine release version. {e}")
            return ReleaseReturnValue.NO_RELEASE_VERSION

        if not release_version:
            return ReleaseReturnValue.NO_RELEASE_VERSION

        self.terminal.info(f"Preparing the release {release_version}")

        git_version = f"{self.git_tag_prefix}{release_version}"

        if self._has_tag(git_version):
            self.terminal.error(f"Git tag {git_version} already exists.")
            return ReleaseReturnValue.ALREADY_TAKEN

        try:
            updated = command.update_version(release_version)

            self.terminal.ok(f"Updated version to {release_version}")

            for path in updated.changed_files:
                self.terminal.info(f"Adding changes of {path}")
                self.git.add(path)
        except VersionError as e:
            self.terminal.error(
                f"Unable to update version to {release_version}. {e}"
            )
            return ReleaseReturnValue.UPDATE_VERSION_ERROR

        last_release_version = get_last_release_version(
            self.git_tag_prefix,
            ignore_pre_releases=not release_version.is_prerelease,
        )

        self.terminal.info(
            f"Creating changelog for {release_version} since "
            f"{last_release_version}"
        )

        release_text = self._create_changelog(
            release_version, last_release_version, cc_config
        )

        self.terminal.info("Committing changes")

        commit_msg = f"Automatic release to {release_version}"

        self.git.commit(
            commit_msg, verify=False, gpg_signing_key=git_signing_key
        )
        self.git.tag(
            git_version, gpg_key_id=git_signing_key, message=commit_msg
        )

        if not local:
            self.terminal.info("Pushing changes")
            self.git.push(follow_tags=True, remote=git_remote_name)

            try:
                self.terminal.info(f"Creating release for {release_version}")

                await self._create_release(release_version, token, release_text)

                self.terminal.ok(f"Created release {release_version}")
            except httpx.HTTPStatusError as e:
                self.terminal.error(str(e))
                return ReleaseReturnValue.CREATE_RELEASE_ERROR

        calculator = command.get_version_calculator()

        if not next_version:
            next_version = calculator.next_dev_version(release_version)

        try:
            updated = command.update_version(next_version)
            self.terminal.ok(f"Updated version after release to {next_version}")
        except VersionError as e:
            self.terminal.error(
                f"Error while updating version after release. {e}"
            )
            return ReleaseReturnValue.UPDATE_VERSION_AFTER_RELEASE_ERROR

        for f in updated.changed_files:
            self.terminal.info(f"Adding changes of {f}")
            self.git.add(f)

        commit_msg = f"""Automatic adjustments after release

* Update to version {next_version}
"""

        self.terminal.info("Committing changes")
        self.git.commit(
            commit_msg, verify=False, gpg_signing_key=git_signing_key
        )

        if not local:
            self.terminal.info("Pushing changes")
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
            release_type=args.release_type,
            release_version=args.release_version,
            next_version=args.next_version,
            git_remote_name=args.git_remote_name,
            git_signing_key=args.git_signing_key,
            git_tag_prefix=args.git_tag_prefix,
            cc_config=args.cc_config,
            local=args.local,
        )
    )
