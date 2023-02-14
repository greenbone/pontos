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
from enum import Enum, IntEnum
from pathlib import Path
from typing import Optional

from pontos.changelog.changelog import ChangelogError, update_changelog
from pontos.changelog.conventional_commits import ChangelogBuilder
from pontos.git import Git
from pontos.terminal import Terminal
from pontos.version.commands import get_current_version, update_version
from pontos.version.errors import VersionError
from pontos.version.helper import (
    calculate_calendar_version,
    get_next_patch_version,
)
from pontos.version.version import VersionUpdate

from .helper import (
    find_signing_key,
    get_git_repository_name,
    get_last_release_version,
)

RELEASE_TEXT_FILE = ".release.md"
DEFAULT_CHANGELOG_FILE = "CHANGELOG.md"


class PrepareReturnValue(IntEnum):
    SUCCESS = 0
    NO_RELEASE_VERSION = 1
    ALREADY_TAKEN = 2
    UPDATE_VERSION_ERROR = 3
    CHANGELOG_ERROR = 4


class ReleaseType(Enum):
    PATCH = "patch"
    CALENDAR = "calendar"
    VERSION = "version"
    # for the future we need
    # MAJOR = "major"
    # MINOR = "minor"
    # PRE_RELEASE = "pre-release"


class PrepareCommand:
    def __init__(self, terminal: Terminal) -> None:
        self.git = Git()
        self.terminal = terminal

    def _get_release_version(
        self, release_type: ReleaseType, release_version: Optional[str]
    ) -> str:
        if release_type == ReleaseType.CALENDAR:
            return calculate_calendar_version(get_current_version())

        if release_type == ReleaseType.PATCH:
            return get_next_patch_version(get_current_version())

        if not release_version:
            raise VersionError(
                "No release version provided. Either use a different release "
                "strategy or provide a release version."
            )
        return release_version

    def _has_tag(self, git_version: str) -> bool:
        git_tags = self.git.list_tags()
        return git_version in git_tags

    def _update_version(self, release_version: str) -> VersionUpdate:
        return update_version(release_version, develop=False)

    def _create_old_changelog(
        self, release_version: str, changelog_file: Optional[Path]
    ) -> str:
        if not changelog_file:
            changelog_file = Path(DEFAULT_CHANGELOG_FILE)

        if not changelog_file.exists():
            raise ChangelogError(
                f"Changelog file {changelog_file} does not exist."
            )

        # Try to get the unreleased section of the specific version
        changelog_text, release_text = update_changelog(
            changelog_file.read_text(encoding="utf-8"),
            release_version,
            git_tag_prefix=self.git_tag_prefix,
            containing_version=release_version,
        )

        if not changelog_text:
            # Try to get unversioned unrelease section
            changelog_text, release_text = update_changelog(
                changelog_file.read_text(encoding="utf-8"),
                release_version,
                git_tag_prefix=self.git_tag_prefix,
            )

        if not changelog_text:
            raise ChangelogError(
                f"No unreleased text found in {changelog_file}"
            )

        changelog_file.write_text(changelog_text, encoding="utf8")

        self.git.add(changelog_file)

        return release_text

    def _create_changelog(self, release_version: str, cc_config: Path) -> str:
        last_release_version = get_last_release_version()
        changelog_builder = ChangelogBuilder(
            terminal=self.terminal,
            current_version=last_release_version,
            next_version=release_version,
            space=self.space,
            project=self.project,
            config=cc_config,
        )

        output_file = changelog_builder.create_changelog_file(
            f"v{release_version}.md"
        )
        self.git.add(output_file)
        return output_file.read_text(encoding="utf-8").replace(
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
        changelog_file: Optional[Path],
        conventional_commits: bool,
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
            changelog_file: A changelog file to use for releases not using
                conventional commits.
            conventional_commits: Create changelog and release description from
                conventional commits.
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
            release_version = self._get_release_version(
                release_type, release_version
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
            updated = self._update_version(release_version)

            self.terminal.ok(f"Updated version to {release_version}")

            for path in updated.changed_files:
                self.git.add(path)
        except VersionError as e:
            self.terminal.error(
                f"Unable to update version to {release_version}. {e}"
            )
            return PrepareReturnValue.UPDATE_VERSION_ERROR

        if conventional_commits:
            release_text = self._create_changelog(release_version, cc_config)
        else:
            release_text = self._create_old_changelog(
                release_version, changelog_file
            )

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
    if args.calendar:
        release_type = ReleaseType.CALENDAR
    elif args.patch:
        release_type = ReleaseType.PATCH
    else:
        release_type = ReleaseType.VERSION

    return cmd.run(
        git_signing_key=args.git_signing_key,
        project=args.project,
        space=args.space,
        release_type=release_type,
        release_version=args.release_version,
        git_tag_prefix=args.git_tag_prefix,
        changelog_file=args.changelog,
        cc_config=args.cc_config,
        conventional_commits=args.conventional_commits,
    )
