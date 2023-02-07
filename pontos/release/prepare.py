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
from enum import IntEnum
from pathlib import Path

from pontos import changelog
from pontos.git import Git
from pontos.terminal import Terminal

from .helper import (
    calculate_calendar_version,
    commit_files,
    find_signing_key,
    get_git_repository_name,
    get_last_release_version,
    get_next_patch_version,
    update_version,
)

RELEASE_TEXT_FILE = ".release.md"


class PrepareReturnValue(IntEnum):
    SUCCESS = 0
    NO_RELEASE_VERSION = 1
    ALREADY_TAKEN = 2
    UPDATE_VERSION_ERROR = 3
    NO_UNRELEASED_CHANGELOG = 4


def prepare(
    terminal: Terminal,
    args: Namespace,
    **_kwargs,
) -> IntEnum:
    git_tag_prefix: str = args.git_tag_prefix
    git_signing_key: str = (
        args.git_signing_key
        if args.git_signing_key is not None
        else find_signing_key(terminal)
    )
    project: str = (
        args.project if args.project is not None else get_git_repository_name()
    )
    space: str = args.space
    calendar: bool = args.calendar
    patch: bool = args.patch

    if calendar:
        release_version: str = calculate_calendar_version(terminal)
    elif patch:
        release_version: str = get_next_patch_version(terminal)
    else:
        release_version: str = args.release_version

    if not release_version:
        return PrepareReturnValue.NO_RELEASE_VERSION

    terminal.info(f"Preparing the release {release_version}")

    # guardian
    git = Git()
    git_tags = git.list_tags()
    git_version = f"{git_tag_prefix}{release_version}"
    if git_version in git_tags:
        terminal.error(f"git tag {git_version} is already taken.")
        return PrepareReturnValue.ALREADY_TAKEN

    executed, filename = update_version(terminal, release_version)
    if not executed:
        return PrepareReturnValue.UPDATE_VERSION_ERROR

    terminal.ok(f"updated version in {filename} to {release_version}")

    changelog_bool = True
    if args.conventional_commits:
        last_release_version = get_last_release_version()
        changelog_builder = changelog.ChangelogBuilder(
            terminal=terminal,
            current_version=last_release_version,
            next_version=release_version,
            space=space,
            project=project,
            config=args.cc_config,
        )

        output_file = changelog_builder.create_changelog_file(
            f"v{release_version}.md"
        )
        terminal.ok(f"Created changelog {output_file}")
        commit_msg = f"Changelog created for release to {release_version}"
        commit_files(
            git,
            output_file,
            commit_msg,
            git_signing_key=git_signing_key,
        )
        changelog_bool = False
        # Remove the header for the release text
        changelog_text = output_file.read_text(encoding="utf-8").replace(
            "# Changelog\n\n"
            "All notable changes to this project "
            "will be documented in this file.\n\n",
            "",
        )
    else:
        change_log_path = Path.cwd() / "CHANGELOG.md"
        if args.changelog:
            tmp_path = Path.cwd() / Path(args.changelog)
            if tmp_path.is_file():
                change_log_path = tmp_path
            else:
                terminal.warning(f"{tmp_path} is not a file.")

        # Try to get the unreleased section of the specific version
        updated, changelog_text = changelog.update(
            change_log_path.read_text(encoding="utf-8"),
            release_version,
            git_tag_prefix=git_tag_prefix,
            containing_version=release_version,
        )

        if not updated:
            # Try to get unversioned unrelease section
            updated, changelog_text = changelog.update(
                change_log_path.read_text(encoding="utf-8"),
                release_version,
                git_tag_prefix=git_tag_prefix,
            )

        if not updated:
            terminal.error("No unreleased text found in CHANGELOG.md")
            return PrepareReturnValue.NO_UNRELEASED_CHANGELOG

        change_log_path.write_text(updated, encoding="utf-8")

        terminal.ok("Updated CHANGELOG.md")

    terminal.info("Committing changes")

    commit_msg = f"Automatic release to {release_version}"
    commit_files(
        git,
        filename,
        commit_msg,
        git_signing_key=git_signing_key,
        changelog=changelog_bool,
    )

    git.tag(git_version, gpg_key_id=git_signing_key, message=commit_msg)

    release_text = Path(RELEASE_TEXT_FILE)
    release_text.write_text(changelog_text, encoding="utf-8")

    terminal.warning(
        f"Please verify git tag {git_version}, "
        f"commit and release text in {str(release_text)}"
    )
    terminal.print("Afterwards please execute release")

    return PrepareReturnValue.SUCCESS
