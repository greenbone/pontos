# Copyright (C) 2020-2022 Greenbone AG
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
from dataclasses import dataclass
from enum import IntEnum, auto
from pathlib import Path
from typing import Literal, Optional, SupportsInt, Union

import httpx

from pontos.changelog.conventional_commits import ChangelogBuilder
from pontos.errors import PontosError
from pontos.git import Git
from pontos.github.actions.core import ActionIO
from pontos.github.api import GitHubAsyncRESTApi
from pontos.release.command import AsyncCommand
from pontos.terminal import Terminal
from pontos.version import Version, VersionError
from pontos.version.helper import get_last_release_version
from pontos.version.project import Project
from pontos.version.schemes import VersioningScheme

from .helper import (
    ReleaseType,
    find_signing_key,
    get_git_repository_name,
    get_next_release_version,
)


@dataclass
class ReleaseInformation:
    last_release_version: Optional[Version]
    release_version: Version
    git_release_tag: str
    next_version: Optional[Version]

    def write_github_output(self):
        with ActionIO.out() as output:
            output.write(
                "last-release-version", self.last_release_version or ""
            )
            output.write("release-version", self.release_version)
            output.write("git-release-tag", self.git_release_tag)
            output.write("next-version", self.next_version or "")


class CreateReleaseReturnValue(IntEnum):
    """
    Possible return values of ReleaseCommand
    """

    SUCCESS = 0
    PROJECT_SETTINGS_NOT_FOUND = auto()
    TOKEN_MISSING = auto()
    NO_LAST_RELEASE_VERSION = auto()
    NO_RELEASE_VERSION = auto()
    ALREADY_TAKEN = auto()
    CREATE_RELEASE_ERROR = auto()
    UPDATE_VERSION_ERROR = auto()
    UPDATE_VERSION_AFTER_RELEASE_ERROR = auto()


class CreateReleaseCommand(AsyncCommand):
    """
    A CLI command for creating a release

    Args:
        terminal: A Terminal for output
    """

    def __init__(self, *, terminal: Terminal, error_terminal: Terminal) -> None:
        super().__init__(terminal=terminal, error_terminal=error_terminal)
        self.git = Git()

    def _has_tag(self, git_version: str) -> bool:
        git_tags = self.git.list_tags()
        return git_version in git_tags

    def _create_changelog(
        self,
        release_version: Version,
        last_release_version: Optional[Version],
        cc_config: Optional[Path],
    ) -> str:
        changelog_builder = ChangelogBuilder(
            space=self.space,
            project=self.project,
            config=cc_config,
            git_tag_prefix=self.git_tag_prefix,
        )

        return changelog_builder.create_changelog(
            last_version=last_release_version.parsed_version
            if last_release_version
            else None,
            next_version=release_version,
        )

    async def _create_release(
        self,
        release_version: Version,
        token: str,
        release_text: str,
        github_pre_release: bool,
    ) -> None:
        github = GitHubAsyncRESTApi(token=token)

        git_version = f"{self.git_tag_prefix}{release_version}"
        repo = f"{self.space}/{self.project}"

        await github.releases.create(
            repo,
            git_version,
            name=f"{self.project} {release_version}",
            body=release_text,
            prerelease=release_version.is_pre_release or github_pre_release,
        )

    async def async_run(  # type: ignore[override]
        self,
        *,
        token: str,
        space: str,
        project_name: Optional[str],
        versioning_scheme: VersioningScheme,
        release_type: ReleaseType,
        release_version: Optional[Version],
        next_version: Union[Version, Literal[False], None],
        git_signing_key: str,
        git_remote_name: Optional[str],
        git_tag_prefix: Optional[str],
        cc_config: Optional[Path],
        local: Optional[bool] = False,
        release_series: Optional[str] = None,
        update_project: bool = True,
        github_pre_release: bool = False,
    ) -> CreateReleaseReturnValue:
        """
        Create a release

        Args:
            token: A token for creating a release on GitHub
            space: GitHub username or organization. Required for generating
                links in the changelog.
            project: Name of the project to release. If not set it will be
                gathered via the git remote url.
            versioning_scheme: The versioning scheme to use for version parsing
                and calculation
            release_type: Type of the release to prepare. Defines the release
                version. PATCH increments the bugfix version. CALENDAR creates
                a new CalVer release version. VERSION uses the provided
                release_version.
            release_version: Optional release version to use. If not set the
                to be released version will be determined from the project.
            next_version: Optional version to set after the release.
                If set to None the next development version will be set.
                If set to False the version will not be changed after the
                release. Default is to update to the next development version.
            git_signing_key: A GPG key ID to use for creating signatures.
            git_remote_name: Name of the git remote to use.
            git_tag_prefix: An optional prefix to use for creating a git tag
                from the release version.
            cc_config: A path to a settings file for creating conventional
                commits.
            local: Only create changes locally and don't push changes to
                remote repository. Also don't create a GitHub release.
            release_series: Optional release series to use.
                For example: "1.2", "2", "23".
            update_project: Update version in project files.
            github_pre_release: Enforce uploading a release as a GitHub pre
                release
        """
        git_signing_key = (
            git_signing_key
            if git_signing_key is not None
            else find_signing_key(self.terminal)
        )
        self.git_tag_prefix = git_tag_prefix or ""
        self.project = (
            project_name
            if project_name is not None
            else get_git_repository_name()
        )
        self.space = space

        self.terminal.info(f"Using versioning scheme {versioning_scheme.name}")

        try:
            last_release_version = get_last_release_version(
                parse_version=versioning_scheme.parse_version,
                git_tag_prefix=self.git_tag_prefix,
                tag_name=f"{self.git_tag_prefix}{release_series}.*"
                if release_series
                else None,
            )
        except PontosError as e:
            last_release_version = None
            self.print_warning(f"Could not determine last release version. {e}")

        if not last_release_version:
            if not release_version:
                self.print_error("Unable to determine last release version.")
                return CreateReleaseReturnValue.NO_LAST_RELEASE_VERSION
            else:
                self.terminal.info(
                    f"Creating the initial release {release_version}"
                )

        else:
            self.terminal.info(f"Last release was {last_release_version}")

        calculator = versioning_scheme.calculator()

        try:
            release_version = get_next_release_version(
                last_release_version=last_release_version,
                calculator=calculator,
                release_type=release_type,
                release_version=release_version,
            )
        except VersionError as e:
            self.print_error(f"Unable to determine release version. {e}")
            return CreateReleaseReturnValue.NO_RELEASE_VERSION

        self.terminal.info(f"Preparing the release {release_version}")

        git_version = f"{self.git_tag_prefix}{release_version}"

        if self._has_tag(git_version):
            self.print_error(f"Git tag {git_version} already exists.")
            return CreateReleaseReturnValue.ALREADY_TAKEN

        if update_project:
            try:
                project = Project(versioning_scheme)
            except PontosError as e:
                self.print_error(f"Unable to determine project settings. {e}")
                return CreateReleaseReturnValue.PROJECT_SETTINGS_NOT_FOUND

            try:
                updated = project.update_version(release_version)

                self.terminal.ok(f"Updated version to {release_version}")

                for path in updated.changed_files:
                    self.terminal.info(f"Adding changes of {path}")
                    self.git.add(path)
            except VersionError as e:
                self.terminal.error(
                    f"Unable to update version to {release_version}. {e}"
                )
                return CreateReleaseReturnValue.UPDATE_VERSION_ERROR

        if last_release_version:
            self.terminal.info(
                f"Creating changelog for {release_version} since "
                f"{last_release_version}"
            )
        else:
            self.terminal.info(
                f"Creating changelog for {release_version} as initial release."
            )

        release_text = self._create_changelog(
            release_version, last_release_version, cc_config
        )

        commit_msg = f"Automatic release to {release_version}"

        # check if files have been modified and create a commit
        status = list(self.git.status())
        if status:
            self.terminal.info("Committing changes")

            self.git.commit(
                commit_msg, verify=False, gpg_signing_key=git_signing_key
            )

        self.terminal.info(f"Creating tag {git_version}")
        self.git.tag(
            git_version, gpg_key_id=git_signing_key, message=commit_msg
        )

        if not local:
            self.terminal.info("Pushing changes")
            self.git.push(follow_tags=True, remote=git_remote_name)

            try:
                self.terminal.info(f"Creating release for {release_version}")

                await self._create_release(
                    release_version,
                    token,
                    release_text,
                    github_pre_release,
                )

                self.terminal.ok(f"Created release {release_version}")
            except httpx.HTTPStatusError as e:
                self.print_error(str(e))
                return CreateReleaseReturnValue.CREATE_RELEASE_ERROR

        if next_version is None:
            next_version = calculator.next_dev_version(release_version)

        if next_version:
            if update_project:
                try:
                    updated = project.update_version(next_version)
                    self.terminal.ok(
                        f"Updated version after release to {next_version}"
                    )
                except VersionError as e:
                    self.print_error(
                        f"Error while updating version after release. {e}"
                    )
                    return (
                        CreateReleaseReturnValue.UPDATE_VERSION_AFTER_RELEASE_ERROR
                    )

                for f in updated.changed_files:
                    self.terminal.info(f"Adding changes of {f}")
                    self.git.add(f)

            # check if files have been modified and create a commit
            status = list(self.git.status())
            if status:
                commit_msg = f"""Automatic adjustments after release

* Update to version {next_version}
"""

                self.terminal.info("Committing changes after release")
                self.git.commit(
                    commit_msg, verify=False, gpg_signing_key=git_signing_key
                )

            if not local:
                self.terminal.info("Pushing changes")
                self.git.push(follow_tags=True, remote=git_remote_name)

        self.release_information = ReleaseInformation(
            last_release_version=last_release_version,
            release_version=release_version,
            git_release_tag=git_version,
            next_version=next_version or None,
        )
        if ActionIO.has_output():
            self.release_information.write_github_output()

        return CreateReleaseReturnValue.SUCCESS


def create_release(
    args: Namespace,
    *,
    token: str,
    terminal: Terminal,
    error_terminal: Terminal,
    **_kwargs,
) -> SupportsInt:
    if not token:
        error_terminal.error(
            "Token is missing. The GitHub token is required to create a "
            "release."
        )
        return CreateReleaseReturnValue.TOKEN_MISSING

    return CreateReleaseCommand(
        terminal=terminal, error_terminal=error_terminal
    ).run(
        token=token,
        space=args.space,
        project_name=args.project,
        versioning_scheme=args.versioning_scheme,
        release_type=args.release_type,
        release_version=args.release_version,
        next_version=args.next_version,
        git_remote_name=args.git_remote_name,
        git_signing_key=args.git_signing_key,
        git_tag_prefix=args.git_tag_prefix,
        cc_config=args.cc_config,
        local=args.local,
        release_series=args.release_series,
        update_project=args.update_project,
        github_pre_release=args.github_pre_release,
    )
