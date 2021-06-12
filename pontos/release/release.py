# -*- coding: utf-8 -*-
# pontos/release/release.py
# Copyright (C) 2020 - 2021 Greenbone Networks GmbH
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

import argparse
import sys
import subprocess
import os
import json

from pathlib import Path
from typing import Callable, Tuple

import requests

from pontos.release.helper import (
    build_release_dict,
    commit_files,
    download,
    find_signing_key,
    get_project_name,
    update_version,
    upload_assets,
)
from pontos import version
from pontos.version import (
    calculate_calendar_version,
    get_current_version,
    get_next_dev_version,
)
from pontos import changelog
from pontos.terminal import _set_terminal, error, warning, info, ok, out
from pontos.terminal.terminal import Terminal

RELEASE_TEXT_FILE = ".release.txt.md"


def initialize_default_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Release handling utility.',
        prog='pontos-release',
    )

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='additional help',
        dest='command',
    )

    prepare_parser = subparsers.add_parser('prepare')
    prepare_parser.set_defaults(func=prepare)
    version_group = prepare_parser.add_mutually_exclusive_group(required=True)
    version_group.add_argument(
        '--release-version',
        help='Will release changelog as version. Must be PEP 440 compliant',
    )
    version_group.add_argument(
        '--calendar',
        help=(
            'Automatically calculate calendar release version, from current'
            ' version and date.'
        ),
        action='store_true',
    )

    prepare_parser.add_argument(
        '--git-signing-key',
        help='The key to sign the commits and tag for a release',
    )
    prepare_parser.add_argument(
        '--git-tag-prefix',
        default='v',
        help='Prefix for git tag versions. Default: %(default)s',
    )

    release_parser = subparsers.add_parser('release')
    release_parser.set_defaults(func=release)
    release_parser.add_argument(
        '--release-version',
        help=(
            'Will release changelog as version. Must be PEP 440 compliant. '
            'default: lookup version in project definition.'
        ),
    )

    release_parser.add_argument(
        '--next-version',
        help=(
            'Sets the next PEP 440 compliant version in project definition '
            'after the release. default: set to next dev version',
        ),
    )

    release_parser.add_argument(
        '--git-remote-name',
        help='The git remote name to push the commits and tag to',
    )
    release_parser.add_argument(
        '--git-tag-prefix',
        default='v',
        help='Prefix for git tag versions. Default: %(default)s',
    )
    release_parser.add_argument(
        '--git-signing-key',
        help='The key to sign the commits and tag for a release',
    )
    release_parser.add_argument(
        '--project',
        help='The github project',
    )
    release_parser.add_argument(
        '--space',
        default='greenbone',
        help='user/team name in github',
    )

    sign_parser = subparsers.add_parser('sign')
    sign_parser.set_defaults(func=sign)
    sign_parser.add_argument(
        '--signing-key',
        default='0ED1E580',
        help='The key to sign zip, tarballs of a release. Default %(default)s.',
    )
    sign_parser.add_argument(
        '--release-version',
        help='Will release changelog as version. Must be PEP 440 compliant.',
    )
    sign_parser.add_argument(
        '--git-tag-prefix',
        default='v',
        help='Prefix for git tag versions. Default: %(default)s',
    )
    sign_parser.add_argument(
        '--project',
        help='The github project',
    )
    sign_parser.add_argument(
        '--space',
        default='greenbone',
        help='user/team name in github',
    )
    return parser


def parse(args=None) -> Tuple[str, str, argparse.Namespace]:
    parser = initialize_default_parser()
    commandline_arguments = parser.parse_args(args)
    token = os.environ['GITHUB_TOKEN'] if not args else 'TOKEN'
    user = os.environ['GITHUB_USER'] if not args else 'USER'
    return (user, token, commandline_arguments)


def prepare(
    shell_cmd_runner: Callable,
    args: argparse.Namespace,
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
        else find_signing_key(shell_cmd_runner)
    )
    calendar: bool = args.calendar

    if calendar:
        release_version: str = calculate_calendar_version()
    else:
        release_version: str = args.release_version

    info(f"Preparing the release {release_version}")

    # guardian
    git_tags = shell_cmd_runner('git tag -l')
    git_version = f"{git_tag_prefix}{release_version}"
    if git_version.encode() in git_tags.stdout.splitlines():
        raise ValueError(f'git tag {git_version} is already taken.')

    executed, filename = update_version(release_version, version_module)
    if not executed:
        return False

    ok(f"updated version  in {filename} to {release_version}")

    change_log_path = path.cwd() / 'CHANGELOG.md'
    updated, changelog_text = changelog_module.update(
        change_log_path.read_text(),
        release_version,
        git_tag_prefix=git_tag_prefix,
    )

    if not updated:
        raise ValueError("No unreleased text found in CHANGELOG.md")

    change_log_path.write_text(updated)

    ok("Updated CHANGELOG.md")

    info("Committing changes")

    commit_msg = f'automatic release to {release_version}'
    commit_files(
        filename,
        commit_msg,
        shell_cmd_runner,
        git_signing_key=git_signing_key,
    )

    if git_signing_key:
        shell_cmd_runner(
            f"git tag -u {git_signing_key} {git_version} -m '{commit_msg}'"
        )
    else:
        shell_cmd_runner(f"git tag {git_version} -m '{commit_msg}'")

    release_text = path(RELEASE_TEXT_FILE)
    release_text.write_text(changelog_text)

    warning(
        f"Please verify git tag {git_version}, "
        f"commit and release text in {str(release_text)}"
    )
    out("Afterwards please execute release")

    return True


def release(
    shell_cmd_runner: Callable,
    args: argparse.Namespace,
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

    info("Creating release")
    changelog_text: str = path(RELEASE_TEXT_FILE).read_text()

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

    # set to new version add skeleton
    change_log_path = path.cwd() / 'CHANGELOG.md'

    executed, filename = update_version(
        next_version, version_module, develop=True
    )
    if not executed:
        return False

    updated = changelog_module.add_skeleton(
        markdown=change_log_path.read_text(),
        new_version=release_version,
        project_name=project,
        git_tag_prefix=git_tag_prefix,
        git_space=space,
    )
    change_log_path.write_text(updated)

    commit_msg = (
        f'* Update to version {next_version}\n'
        f'* Add empty changelog after {release_version}'
    )
    commit_files(
        filename,
        commit_msg,
        shell_cmd_runner,
        git_signing_key=git_signing_key,
    )

    shell_cmd_runner(f"git push --follow-tags {git_remote_name}")

    return True


def sign(
    shell_cmd_runner: Callable,
    args: argparse.Namespace,
    *,
    path: Path,
    username: str,
    token: str,
    requests_module: requests,
    **_kwargs,
) -> bool:

    project: str = (
        args.project
        if args.project is not None
        else get_project_name(shell_cmd_runner)
    )
    space: str = args.space
    git_tag_prefix: str = args.git_tag_prefix
    release_version: str = (
        args.release_version
        if args.release_version is not None
        else get_current_version()
    )
    signing_key: str = args.signing_key

    headers = {'Accept': 'application/vnd.github.v3+json'}

    git_version: str = f'{git_tag_prefix}{release_version}'

    base_url = (
        f"https://api.github.com/repos/{space}/{project}"
        f"/releases/tags/{git_version}"
    )

    response = requests_module.get(
        base_url,
        headers=headers,
    )
    if response.status_code != 200:
        error(f"Wrong response status code: {response.status_code}")
        out(json.dumps(response.text, indent=4, sort_keys=True))
        return False

    github_json = json.loads(response.text)
    zip_path = download(
        github_json['zipball_url'],
        f"{git_version}.zip",
        path=path,
        requests_module=requests_module,
    )
    tar_path = download(
        github_json['tarball_url'],
        f"{git_version}.tar.gz",
        path=path,
        requests_module=requests_module,
    )

    info(f"Signing {[zip_path, tar_path]}")

    shell_cmd_runner(
        f"gpg --default-key {signing_key} --detach-sign --armor {zip_path}"
    )
    shell_cmd_runner(
        f"gpg --default-key {signing_key} --detach-sign --armor {tar_path}"
    )

    return upload_assets(
        username,
        token,
        [zip_path, tar_path],
        github_json,
        path=path,
        requests_module=requests_module,
    )


def main(
    shell_cmd_runner=lambda x: subprocess.run(
        x,
        shell=True,
        check=True,
        errors="utf-8",  # use utf-8 encoding for error output
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ),
    _path: Path = Path,
    _requests: requests = requests,
    _version: version = version,
    _changelog: changelog = changelog,
    leave: bool = True,
    args=None,
):
    username, token, parsed_args = parse(args)
    term = Terminal()
    _set_terminal(term)

    term.bold_info(f'pontos-release => {parsed_args.func.__name__}')

    with term.indent():
        try:
            if not parsed_args.func(
                shell_cmd_runner,
                parsed_args,
                path=_path,
                username=username,
                token=token,
                changelog_module=_changelog,
                requests_module=_requests,
                version_module=_version,
            ):
                return sys.exit(1) if leave else False
        except subprocess.CalledProcessError as e:
            error(f'Could not run command "{e.cmd}". Error was:\n\n{e.stderr}')
            sys.exit(1)

    return sys.exit(0) if leave else True


if __name__ == '__main__':
    main()
