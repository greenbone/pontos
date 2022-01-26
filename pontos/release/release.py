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
#

from argparse import Namespace
import json

from pathlib import Path
from typing import Callable

import requests

from pontos import changelog
from pontos.terminal import error, warning, info
from pontos import version

from .helper import (
    build_release_dict,
    commit_files,
    find_signing_key,
    get_current_version,
    get_next_dev_version,
    get_project_name,
    update_version,
)

RELEASE_TEXT_FILE = ".release.md"


def release(
    shell_cmd_runner: Callable,
    args: Namespace,
    *,
    path: Path,
    version_module: version,
    username: str,
    token: str,
    requests_module: requests,
    changelog_module: changelog,
    **_kwargs,
) -> bool:
    project: str = (
        args.project
        if args.project is not None
        else get_project_name(shell_cmd_runner)
    )
    space: str = args.space
    git_signing_key: str = (
        args.git_signing_key
        if args.git_signing_key is not None
        else find_signing_key(shell_cmd_runner)
    )
    git_remote_name: str = (
        args.git_remote_name if args.git_remote_name is not None else ''
    )
    git_tag_prefix: str = args.git_tag_prefix
    release_version: str = (
        args.release_version
        if args.release_version is not None
        else get_current_version()
    )
    next_version: str = (
        args.next_version
        if args.next_version is not None
        else get_next_dev_version(release_version)
    )

    info("Pushing changes")

    shell_cmd_runner(f"git push --follow-tags {git_remote_name}")

    info(f"Creating release for v{release_version}")
    changelog_text: str = path(RELEASE_TEXT_FILE).read_text(encoding='utf-8')

    headers = {'Accept': 'application/vnd.github.v3+json'}

    base_url = f"https://api.github.com/repos/{space}/{project}/releases"
    git_version = f'{git_tag_prefix}{release_version}'
    response = requests_module.post(
        base_url,
        headers=headers,
        auth=(username, token),
        json=build_release_dict(
            git_version,
            changelog_text,
            name=f"{project} {release_version}",
        ),
    )
    if response.status_code != 201:
        error(f"Wrong response status code: {response.status_code}")
        error(json.dumps(response.text, indent=4, sort_keys=True))
        return False

    path(RELEASE_TEXT_FILE).unlink()

    commit_msg = (
        f'Automatic adjustments after release\n\n'
        f'* Update to version {next_version}\n'
    )

    # set to new version add skeleton
    changelog_bool = True
    if not args.conventional_commits:
        change_log_path = path.cwd() / 'CHANGELOG.md'
        if args.changelog:
            tmp_path = path.cwd() / Path(args.changelog)
            if tmp_path.is_file():
                change_log_path = tmp_path
            else:
                warning(f"{tmp_path} is not a file.")

        updated = changelog_module.add_skeleton(
            markdown=change_log_path.read_text(encoding='utf-8'),
            new_version=release_version,
            project_name=project,
            git_tag_prefix=git_tag_prefix,
            git_space=space,
        )
        change_log_path.write_text(updated, encoding='utf-8')
        changelog_bool = False

        commit_msg += f'* Add empty changelog after {release_version}'

    executed, filename = update_version(
        next_version, version_module, develop=True
    )
    if not executed:
        return False

    commit_files(
        filename,
        commit_msg,
        shell_cmd_runner,
        git_signing_key=git_signing_key,
        changelog=changelog_bool,
    )

    # pushing the new tag
    shell_cmd_runner(f"git push --follow-tags {git_remote_name}")

    return True
