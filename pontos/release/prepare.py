# -*- coding: utf-8 -*-
# pontos/release/release.py
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

import sys
from argparse import Namespace
from pathlib import Path

from pontos import changelog, version
from pontos.helper import shell_cmd_runner
from pontos.terminal import Terminal

from .helper import (
    calculate_calendar_version,
    commit_files,
    find_signing_key,
    get_current_version,
    get_next_patch_version,
    get_project_name,
    update_version,
)

RELEASE_TEXT_FILE = ".release.md"


def prepare(
    terminal: Terminal,
    args: Namespace,
    *,
    path: Path,
    version_module: version,
    changelog_module: changelog,
    **_kwargs,
) -> bool:
    git_tag_prefix: str = args.git_tag_prefix
    git_signing_key: str = (
        args.git_signing_key
        if args.git_signing_key is not None
        else find_signing_key(terminal, shell_cmd_runner)
    )
    project: str = (
        args.project
        if args.project is not None
        else get_project_name(shell_cmd_runner)
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

    terminal.info(f"Preparing the release {release_version}")

    # guardian
    git_tags = shell_cmd_runner("git tag -l")
    git_version = f"{git_tag_prefix}{release_version}"
    if git_version.encode() in git_tags.stdout.splitlines():
        terminal.error(f"git tag {git_version} is already taken.")
        sys.exit(1)

    executed, filename = update_version(
        terminal, release_version, version_module
    )
    if not executed:
        return False

    terminal.ok(f"updated version  in {filename} to {release_version}")

    changelog_bool = True
    if args.conventional_commits:
        current_version = get_current_version(terminal)
        output = f"v{release_version}.md"
        cargs = Namespace(
            current_version=current_version,
            next_version=release_version,
            output=output,
            space=space,
            project=project,
            config=args.cc_config,
        )
        changelog_builder = changelog_module.ChangelogBuilder(
            terminal=terminal,
            args=cargs,
        )

        output_file = changelog_builder.create_changelog_file()
        terminal.ok(f"Created changelog {output}")
        commit_msg = f"Changelog created for release to {release_version}"
        commit_files(
            output_file,
            commit_msg,
            shell_cmd_runner,
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
        change_log_path = path.cwd() / "CHANGELOG.md"
        if args.changelog:
            tmp_path = path.cwd() / Path(args.changelog)
            if tmp_path.is_file():
                change_log_path = tmp_path
            else:
                terminal.warning(f"{tmp_path} is not a file.")

        # Try to get the unreleased section of the specific version
        updated, changelog_text = changelog_module.update(
            change_log_path.read_text(encoding="utf-8"),
            release_version,
            git_tag_prefix=git_tag_prefix,
            containing_version=release_version,
        )

        if not updated:
            # Try to get unversioned unrelease section
            updated, changelog_text = changelog_module.update(
                change_log_path.read_text(encoding="utf-8"),
                release_version,
                git_tag_prefix=git_tag_prefix,
            )

        if not updated:
            terminal.error("No unreleased text found in CHANGELOG.md")
            sys.exit(1)

        change_log_path.write_text(updated, encoding="utf-8")

        terminal.ok("Updated CHANGELOG.md")

    terminal.info("Committing changes")

    commit_msg = f"Automatic release to {release_version}"
    commit_files(
        filename,
        commit_msg,
        shell_cmd_runner,
        git_signing_key=git_signing_key,
        changelog=changelog_bool,
    )

    if git_signing_key:
        shell_cmd_runner(
            f"git tag -u {git_signing_key} {git_version} -m '{commit_msg}'"
        )
    else:
        shell_cmd_runner(f"git tag {git_version} -m '{commit_msg}'")

    release_text = path(RELEASE_TEXT_FILE)
    release_text.write_text(changelog_text, encoding="utf-8")

    terminal.warning(
        f"Please verify git tag {git_version}, "
        f"commit and release text in {str(release_text)}"
    )
    terminal.print("Afterwards please execute release")

    return True
