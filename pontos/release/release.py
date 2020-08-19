# -*- coding: utf-8 -*-
# pontos/release/release.py
# Copyright (C) 2020 Greenbone Networks GmbH
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
import shutil
from pathlib import Path
from typing import Callable, Dict, List, Union

import requests
from pontos import version
from pontos import changelog


def build_release_dict(
    release_version: str,
    release_changelog: str,
    name: str = '',
    target_commitish: str = '',  # needed when tag is not there yet
    draft: bool = False,
    prerelease: bool = False,
) -> Dict[str, Union[str, bool]]:
    """
    builds the dict for release post on github, see:
    https://docs.github.com/en/rest/reference/repos#create-a-release
    for more details.
    """
    tag_name = (
        release_version
        if release_version.startswith('v')
        else "v" + release_version
    )
    return {
        'tag_name': tag_name,
        'target_commitish': target_commitish,
        'name': name,
        'body': release_changelog,
        'draft': draft,
        'prerelease': prerelease,
    }


def initialize_default_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Release handling utility.', prog='pontos-release',
    )
    parser.add_argument(
        '--release-version',
        help='Will release changelog as version. Must be PEP 440 compliant',
        required=True,
    )
    parser.add_argument(
        '--next-release-version',
        help='Sets the next PEP 440 compliant version in project definition.',
        required=True,
    )
    parser.add_argument(
        '--project', help='The github project', required=True,
    )
    parser.add_argument(
        '--space', default='greenbone', help='user/team name in github',
    )
    parser.add_argument(
        '--signing-key',
        default='0ED1E580',
        help='The key to sign zip, tarballs of a release. Default %(default)s.',
    )
    parser.add_argument(
        '--git-signing-key',
        help='The key to sign the commits and tag for a release',
    )
    parser.add_argument(
        '--git-remote-name',
        help='The git remote name to push the commits and tag to',
    )

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='additional help',
        dest='command',
    )

    subparsers.add_parser('prepare')
    subparsers.add_parser('release')
    return parser


def parse(args=None):
    parser = initialize_default_parser()
    commandline_arguments = parser.parse_args(args)
    token = (
        os.environ['GITHUB_TOKEN']
        if not args or not 'testcases' in args
        else 'TOKEN'
    )
    user = (
        os.environ['GITHUB_USER']
        if not args or not 'testcases' in args
        else 'USER'
    )
    return (
        commandline_arguments.command,
        commandline_arguments.release_version,
        commandline_arguments.next_release_version,
        commandline_arguments.project,
        commandline_arguments.space,
        commandline_arguments.signing_key,
        commandline_arguments.git_signing_key,
        commandline_arguments.git_remote_name,
        user,
        token,
    )


def update_version(to: str, _version: version) -> (bool, str):
    executed, filename = _version.main(False, args=["--quiet", "update", to])
    if not executed:
        if filename == "":
            print("No project definition found.")
        else:
            print("Unable to update version {} in {}", to, filename)
    return executed, filename


def commit_files(
    filename: str,
    commit_msg: str,
    git_signing_key: str,
    shell_cmd_runner: Callable,
):
    shell_cmd_runner("git add {}".format(filename))
    shell_cmd_runner("git add *__version__.py || echo 'ignoring __version__'")
    shell_cmd_runner("git add CHANGELOG.md")
    shell_cmd_runner(
        "git commit -S{} -m '{}'".format(git_signing_key or '', commit_msg),
    )


def prepare(
    release_version: str,
    nextversion: str,
    project: str,
    space: str,
    signing_key: str,
    git_signing_key: str,
    git_tag_prefix: str,
    shell_cmd_runner: Callable,
    _path: Path,
    _requests: requests,
    _version: version,
    _changelog: changelog,
):
    print("in prepare")
    # guardian
    git_tags = shell_cmd_runner('git tag -l')
    git_version = "{}{}".format(git_tag_prefix, release_version)
    if git_version.encode() in git_tags.stdout.splitlines():
        raise ValueError('git tag {} is already taken.'.format(git_version))
    executed, filename = update_version(release_version, _version)
    if not executed:
        return False
    print("updated version {} to {}".format(filename, release_version))
    change_log_path = _path.cwd() / 'CHANGELOG.md'
    updated, changelog_text = _changelog.update(
        change_log_path.read_text(),
        release_version,
        git_tag_prefix=git_tag_prefix,
    )
    if not updated:
        raise ValueError("No unreleased text found in CHANGELOG.md")
    change_log_path.write_text(updated)
    print("updated CHANGELOG.md")

    print("Committing changes")
    commit_msg = 'automatic release to {}'.format(release_version)
    commit_files(filename, commit_msg, signing_key, shell_cmd_runner)

    if git_signing_key:
        shell_cmd_runner(
            "git tag -u {} {} -m '{}'".format(
                git_signing_key, git_version, commit_msg
            ),
        )
    else:
        shell_cmd_runner(
            "git tag -s {} -m '{}'".format(git_version, commit_msg),
        )

    release_text = _path(".release.txt.md")
    release_text.write_text(changelog_text)
    # set to new version add skeleton
    executed, filename = update_version(nextversion, _version)
    if not executed:
        return False
    updated = _changelog.add_skeleton(
        change_log_path.read_text(),
        release_version,
        project,
        git_tag_prefix=git_tag_prefix,
        git_space=space,
    )
    change_log_path.write_text(updated)
    commit_msg = 'set version {}, add empty changelog after {}'.format(
        nextversion, release_version
    )
    commit_files(filename, commit_msg, signing_key, shell_cmd_runner)
    print(
        "Please verify git tag {}, commit and release text in {}".format(
            git_version, release_text
        )
    )
    print("Afterwards please execute release")
    return True


def release(
    release_version: str,
    project: str,
    space: str,
    signing_key: str,
    username: str,
    token: str,
    git_tag_prefix: str,
    git_remote_name: str,
    shell_cmd_runner: Callable,
    _path: Path,
    _requests: requests,
    _version: version,
    _changelog: changelog,
):
    auth = (username, token)

    def upload_assets(pathnames: List[str], github_json: str) -> bool:
        print("Uploading assets: {}".format(pathnames))
        asset_url = github_json['upload_url'].replace('{?name,label}', '')
        paths = [_path('{}.asc'.format(p)) for p in pathnames]
        upload_headers = {
            'Accept': 'application/vnd.github.v3+json',
            'content-type': 'application/octet-stream',
        }
        for path in paths:
            to_upload = path.read_bytes()
            resp = _requests.post(
                "{}?name={}".format(asset_url, path.name),
                headers=upload_headers,
                auth=auth,
                data=to_upload,
            )
            if resp.status_code != 201:
                print(
                    "Wrong response status {} while uploading {}".format(
                        resp.status_code, path.name
                    )
                )
                print(json.dumps(resp.text, indent=4, sort_keys=True))
                return False
            else:
                print("uploaded: {}".format(path.name))
        return True

    print("in release")

    def download(url, filename):
        file_path = _path("/tmp/{}".format(filename))
        with _requests.get(url, stream=True) as resp:
            with file_path.open(mode='wb') as download_file:
                shutil.copyfileobj(resp.raw, download_file)
        return file_path

    git_version = "{}{}".format(git_tag_prefix, release_version)
    changelog_text = _path(".release.txt.md").read_text()

    print("Pushing changes")

    if git_remote_name:
        shell_cmd_runner("git push --follow-tags {}".format(git_remote_name))
    else:
        shell_cmd_runner("git push --follow-tags")

    print("Creating release")
    release_info = build_release_dict(git_version, changelog_text)
    headers = {'Accept': 'application/vnd.github.v3+json'}
    base_url = "https://api.github.com/repos/{}/{}/releases".format(
        space, project
    )
    response = _requests.post(
        base_url, headers=headers, auth=auth, json=release_info
    )
    if response.status_code != 201:
        print("Wrong response status code: {}".format(response.status_code))
        print(json.dumps(response.text, indent=4, sort_keys=True))
        return False
    _path(".release.txt.md").unlink()
    github_json = json.loads(response.text)
    zip_path = download(github_json['zipball_url'], git_version + ".zip")
    tar_path = download(github_json['tarball_url'], git_version + ".tar.gz")
    print("Signing {}".format([zip_path, tar_path]))
    gpg_cmd = "gpg --default-key {} --detach-sign --armor {}"
    shell_cmd_runner(gpg_cmd.format(signing_key, zip_path))
    shell_cmd_runner(gpg_cmd.format(signing_key, tar_path))
    return upload_assets([zip_path, tar_path], github_json)


def main(
    git_tag_prefix: str = "v",
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
    def execute(
        command: str,
        release_version: str,
        next_release_version: str,
        project: str,
        space: str,
        signing_key: str,
        git_signing_key: str,
        git_remote_name: str,
        user: str,
        token: str,
    ):
        if command == 'prepare':
            return prepare(
                release_version,
                next_release_version,
                project,
                space,
                signing_key,
                git_signing_key,
                git_tag_prefix,
                shell_cmd_runner,
                _path,
                _requests,
                _version,
                _changelog,
            )
        if command == 'release':
            print("command release")
            return release(
                release_version,
                project,
                space,
                signing_key,
                user,
                token,
                git_tag_prefix,
                git_remote_name,
                shell_cmd_runner,
                _path,
                _requests,
                _version,
                _changelog,
            )

        raise ValueError("Unknown command: {}".format(command))

    values = parse(args)
    if not values:
        return sys.exit(1) if leave else False

    try:
        if not execute(*values):
            return sys.exit(1) if leave else False
    except subprocess.CalledProcessError as e:
        print(
            f'Could not run command "{e.cmd}". Error was:\n\n{e.stderr}',
            file=sys.stderr,
        )
        sys.exit(1)

    return sys.exit(0) if leave else True


if __name__ == '__main__':
    main()
