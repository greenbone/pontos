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
from enum import IntEnum
from pathlib import Path

import httpx

from pontos import changelog
from pontos.git import Git
from pontos.github.api import GitHubRESTApi
from pontos.terminal import Terminal

from .helper import (
    commit_files,
    find_signing_key,
    get_current_version,
    get_git_repository_name,
    get_next_dev_version,
    update_version,
)

RELEASE_TEXT_FILE = ".release.md"


class ReleaseReturnValue(IntEnum):
    SUCCESS = 0
    TOKEN_MISSING = 1
    NO_RELEASE_VERSION = 2
    CREATE_RELEASE_ERROR = 3
    UPDATE_VERSION_ERROR = 4


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

    project: str = (
        args.project if args.project is not None else get_git_repository_name()
    )
    space: str = args.space
    git_signing_key: str = (
        args.git_signing_key
        if args.git_signing_key is not None
        else find_signing_key(terminal)
    )
    git_remote_name: str = (
        args.git_remote_name if args.git_remote_name is not None else ""
    )
    git_tag_prefix: str = args.git_tag_prefix
    release_version: str = (
        args.release_version
        if args.release_version is not None
        else get_current_version(terminal)
    )
    if not release_version:
        terminal.error("No release version available.")
        return ReleaseReturnValue.NO_RELEASE_VERSION

    next_version: str = (
        args.next_version
        if args.next_version is not None
        else get_next_dev_version(release_version)
    )

    terminal.info("Pushing changes")

    git = Git()
    git.push(follow_tags=True, remote=git_remote_name)

    terminal.info(f"Creating release for v{release_version}")
    changelog_text: str = Path(RELEASE_TEXT_FILE).read_text(encoding="utf-8")

    github = GitHubRESTApi(token=token)

    git_version = f"{git_tag_prefix}{release_version}"
    repo = f"{space}/{project}"

    try:
        github.create_release(
            repo,
            git_version,
            name=f"{project} {release_version}",
            body=changelog_text,
        )
    except httpx.HTTPError as e:
        terminal.error(str(e))
        return ReleaseReturnValue.CREATE_RELEASE_ERROR

    Path(RELEASE_TEXT_FILE).unlink()

    commit_msg = (
        f"Automatic adjustments after release\n\n"
        f"* Update to version {next_version}\n"
    )

    # set to new version add skeleton
    changelog_bool = False
    if not args.conventional_commits:
        change_log_path = Path.cwd() / "CHANGELOG.md"
        if args.changelog:
            tmp_path = Path.cwd() / Path(args.changelog)
            if tmp_path.is_file():
                change_log_path = tmp_path
            else:
                terminal.warning(f"{tmp_path} is not a file.")

        updated = changelog.add_skeleton(
            markdown=change_log_path.read_text(encoding="utf-8"),
            new_version=release_version,
            project_name=project,
            git_tag_prefix=git_tag_prefix,
            git_space=space,
        )
        change_log_path.write_text(updated, encoding="utf-8")
        changelog_bool = True

        commit_msg += f"* Add empty changelog after {release_version}"

    executed, filename = update_version(terminal, next_version, develop=True)
    if not executed:
        return ReleaseReturnValue.UPDATE_VERSION_ERROR

    commit_files(
        git,
        filename=filename,
        commit_msg=commit_msg,
        git_signing_key=git_signing_key,
        changelog=changelog_bool,
    )

    # pushing the new tag
    git.push(follow_tags=True, remote=git_remote_name)

    return ReleaseReturnValue.SUCCESS
