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

from argparse import Namespace
from enum import IntEnum, auto
from pathlib import Path
from typing import Optional

from pontos.changelog.conventional_commits import ChangelogBuilder
from pontos.errors import PontosError
from pontos.git import Git
from pontos.terminal import Terminal
from pontos.version.commands import gather_project
from pontos.version.errors import VersionError
from pontos.version.version import VersionCommand

from .helper import (
    ReleaseType,
    find_signing_key,
    get_git_repository_name,
    get_last_release_version,
)

RELEASE_TEXT_FILE = ".release.md"
DEFAULT_CHANGELOG_FILE = "CHANGELOG.md"


class PrepareReturnValue(IntEnum):
    SUCCESS = 0
    PROJECT_SETTINGS_NOT_FOUND = auto()
    NO_RELEASE_VERSION = auto()
    ALREADY_TAKEN = auto()
    UPDATE_VERSION_ERROR = auto()
    CHANGELOG_ERROR = auto()


class PrepareCommand:
    def __init__(self, terminal: Terminal) -> None:
        self.git = Git()
        self.terminal = terminal

    def _get_release_version(
        self,
        command: VersionCommand,
        release_type: ReleaseType,
        release_version: Optional[str],
    ) -> str:
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

        if not release_version:
            raise VersionError(
                "No release version provided. Either use a different release "
                "strategy or provide a release version."
            )
        return release_version

    def _has_tag(self, git_version: str) -> bool:
        git_tags = self.git.list_tags()
        return git_version in git_tags

    def _create_changelog(self, release_version: str, cc_config: Path) -> str:
        last_release_version = get_last_release_version(self.git_tag_prefix)
        changelog_builder = ChangelogBuilder(
            terminal=self.terminal,
            space=self.space,
            project=self.project,
            config=cc_config,
            git_tag_prefix=self.git_tag_prefix,
        )

        changelog_file = Path("changelog") / f"v{release_version}.md"

        changelog_builder.create_changelog_file(
            changelog_file,
            last_version=last_release_version,
            next_version=release_version,
        )
        self.git.add(changelog_file)
        return changelog_file.read_text(encoding="utf-8").replace(
            "# Changelog\n\n"
            "All notable changes to this project "
            "will be documented in this file.\n\n",
            "",
        )

    def run(
        self,
        *,
        space: str,
        project: Optional[str],
        release_type: ReleaseType,
        release_version: Optional[str],
        git_signing_key: Optional[str],
        git_tag_prefix: Optional[str],
        cc_config: Optional[Path],
    ) -> PrepareReturnValue:
        """
        Prepare a release

        Args:
            space: GitHub username or organization. Required for generating
                links in the changelog.
            project: Name of the project to release. If not set it will be
                gathered via the git remote url.
            release_type: Type of the release to prepare. Defines the release
                version. PATCH increments the bugfix version. CALENDAR creates
                a new CalVer release version. VERSION uses the provided
                release_version.
            release_version: Release version to use if release type is VERSION.
            git_signing_key: A GPG key ID to use for creating signatures.
            git_tag_prefix: An optional prefix to use for creating a git tag
                from the release version.
            cc_config: A path to a settings file for creating conventional
                commits.
        """
        self.git_tag_prefix = git_tag_prefix or ""
        git_signing_key = (
            git_signing_key
            if git_signing_key is not None
            else find_signing_key(self.terminal)
        )
        self.project = (
            project if project is not None else get_git_repository_name()
        )
        self.space = space

        try:
            command = gather_project()
        except PontosError as e:
            self.terminal.error(f"Unable to determine project settings. {e}")
            return PrepareReturnValue.PROJECT_SETTINGS_NOT_FOUND

        try:
            release_version = self._get_release_version(
                command, release_type, release_version
            )
        except VersionError as e:
            self.terminal.error(f"Unable to determine release version. {e}")
            return PrepareReturnValue.NO_RELEASE_VERSION

        if not release_version:
            return PrepareReturnValue.NO_RELEASE_VERSION

        self.terminal.info(f"Preparing the release {release_version}")

        git_version = f"{self.git_tag_prefix}{release_version}"

        if self._has_tag(git_version):
            self.terminal.error(f"Git tag {git_version} already exists.")
            return PrepareReturnValue.ALREADY_TAKEN

        try:
            updated = command.update_version(release_version)

            self.terminal.ok(f"Updated version to {release_version}")

            for path in updated.changed_files:
                self.git.add(path)
        except VersionError as e:
            self.terminal.error(
                f"Unable to update version to {release_version}. {e}"
            )
            return PrepareReturnValue.UPDATE_VERSION_ERROR

        release_text = self._create_changelog(release_version, cc_config)

        self.terminal.info("Committing changes")

        commit_msg = f"Automatic release to {release_version}"

        self.git.commit(
            commit_msg, verify=False, gpg_signing_key=git_signing_key
        )
        self.git.tag(
            git_version, gpg_key_id=git_signing_key, message=commit_msg
        )

        release_text_file = Path(RELEASE_TEXT_FILE)
        release_text_file.write_text(release_text, encoding="utf-8")

        self.terminal.warning(
            f"Please verify git tag {git_version}, "
            f"commit and release text in {release_text_file.absolute()}"
        )
        self.terminal.print("Afterwards please execute release")

        return PrepareReturnValue.SUCCESS


def prepare(
    terminal: Terminal,
    args: Namespace,
    **_kwargs,
) -> IntEnum:
    cmd = PrepareCommand(terminal)
    return cmd.run(
        git_signing_key=args.git_signing_key,
        project=args.project,
        space=args.space,
        release_type=args.release_type,
        release_version=args.release_version,
        git_tag_prefix=args.git_tag_prefix,
        cc_config=args.cc_config,
    )
