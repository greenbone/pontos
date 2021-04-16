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
from typing import Callable, Dict, List, Union, Tuple

import requests

from pontos import version
from pontos import changelog

RELEASE_TEXT_FILE = ".release.txt.md"


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
        description='Release handling utility.',
        prog='pontos-release',
    )
    parser.add_argument(
        '--project',
        help='The github project',
        required=True,
    )
    parser.add_argument(
        '--space',
        default='greenbone',
        help='user/team name in github',
    )

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='additional help',
        dest='command',
    )

    prepare_parser = subparsers.add_parser('prepare')
    prepare_parser.set_defaults(func=prepare)
    prepare_parser.add_argument(
        '--release-version',
        help='Will release changelog as version. Must be PEP 440 compliant',
        required=True,
    )
    prepare_parser.add_argument(
        '--next-version',
        help='Sets the next PEP 440 compliant version in project definition '
        'after the release',
        required=True,
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
        help='Will release changelog as version. Must be PEP 440 compliant',
        required=True,
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

    sign_parser = subparsers.add_parser('sign')
    sign_parser.set_defaults(func=sign)
    sign_parser.add_argument(
        '--signing-key',
        default='0ED1E580',
        help='The key to sign zip, tarballs of a release. Default %(default)s.',
    )
    sign_parser.add_argument(
        '--release-version',
        help='Will release changelog as version. Must be PEP 440 compliant',
        required=True,
    )
    sign_parser.add_argument(
        '--git-tag-prefix',
        default='v',
        help='Prefix for git tag versions. Default: %(default)s',
    )
    return parser


def parse(args=None) -> Tuple[str, str, argparse.Namespace]:
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
    return (user, token, commandline_arguments)


def update_version(
    to: str, _version: version, *, develop: bool
) -> Tuple[bool, str]:
    args = ['--quiet']
    args.append('update')
    args.append(to)
    if develop:
        args.append('--develop')
    executed, filename = _version.main(False, args=args)

    if not executed:
        if filename == "":
            print("No project definition found.")
        else:
            print("Unable to update version {} in {}".format(to, filename))

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


def upload_assets(
    username: str,
    token: str,
    pathnames: List[str],
    github_json: Dict,
    path: Path,
    requests_module: requests,
) -> bool:
    print("Uploading assets: {}".format(pathnames))

    asset_url = github_json['upload_url'].replace('{?name,label}', '')
    paths = [path('{}.asc'.format(p)) for p in pathnames]

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'content-type': 'application/octet-stream',
    }
    auth = (username, token)

    for path in paths:
        to_upload = path.read_bytes()
        resp = requests_module.post(
            "{}?name={}".format(asset_url, path.name),
            headers=headers,
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


def prepare(
    shell_cmd_runner: Callable,
    args: argparse.Namespace,
    *,
    path: Path,
    version_module: version,
    changelog_module: changelog,
    **_kwargs,
) -> bool:
    project: str = args.project
    space: str = args.space
    git_tag_prefix: str = args.git_tag_prefix
    git_signing_key: str = args.git_signing_key
    release_version: str = args.release_version
    next_version: str = args.next_version

    print("in prepare")

    # guardian
    git_tags = shell_cmd_runner('git tag -l')
    git_version = "{}{}".format(git_tag_prefix, release_version)
    if git_version.encode() in git_tags.stdout.splitlines():
        raise ValueError('git tag {} is already taken.'.format(git_version))

    executed, filename = update_version(
        release_version, version_module, develop=False
    )
    if not executed:
        return False

    print("updated version {} to {}".format(filename, release_version))

    change_log_path = path.cwd() / 'CHANGELOG.md'
    updated, changelog_text = changelog_module.update(
        change_log_path.read_text(),
        release_version,
        git_tag_prefix=git_tag_prefix,
    )

    if not updated:
        raise ValueError("No unreleased text found in CHANGELOG.md")

    change_log_path.write_text(updated)

    print("Updated CHANGELOG.md")

    print("Committing changes")

    commit_msg = 'automatic release to {}'.format(release_version)
    commit_files(
        filename,
        commit_msg,
        git_signing_key,
        shell_cmd_runner,
    )

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

    release_text = path(RELEASE_TEXT_FILE)
    release_text.write_text(changelog_text)

    # set to new version add skeleton
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
        git_signing_key,
        shell_cmd_runner,
    )

    print(
        f"Please verify git tag {git_version}, "
        f"commit and release text in {str(release_text)}"
    )
    print("Afterwards please execute release")

    return True


def release(
    shell_cmd_runner: Callable,
    args: argparse.Namespace,
    *,
    path: Path,
    username: str,
    token: str,
    requests_module: requests,
    **_kwargs,
) -> bool:
    project: str = args.project
    space: str = args.space
    git_remote_name: str = args.git_remote_name
    git_tag_prefix: str = args.git_tag_prefix
    release_version: str = args.release_version

    changelog_text: str = path(RELEASE_TEXT_FILE).read_text()

    print("Pushing changes")

    if git_remote_name:
        shell_cmd_runner("git push --follow-tags {}".format(git_remote_name))
    else:
        shell_cmd_runner("git push --follow-tags")

    print("Creating release")

    headers = {'Accept': 'application/vnd.github.v3+json'}

    base_url = "https://api.github.com/repos/{}/{}/releases".format(
        space, project
    )
    git_version = f'{git_tag_prefix}{release_version}'
    response = requests_module.post(
        base_url,
        headers=headers,
        auth=(username, token),
        json=build_release_dict(
            git_version,
            changelog_text,
            name="{} {}".format(project, release_version),
        ),
    )
    if response.status_code != 201:
        print("Wrong response status code: {}".format(response.status_code))
        print(json.dumps(response.text, indent=4, sort_keys=True))
        return False

    path(RELEASE_TEXT_FILE).unlink()
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
    def download(url, filename):
        file_path = path(f"/tmp/{filename}")

        with requests_module.get(url, stream=True) as resp, file_path.open(
            mode='wb'
        ) as download_file:
            shutil.copyfileobj(resp.raw, download_file)

        return file_path

    project: str = args.project
    space: str = args.space
    git_tag_prefix: str = args.git_tag_prefix
    release_version: str = args.release_version
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
        print("Wrong response status code: {}".format(response.status_code))
        print(json.dumps(response.text, indent=4, sort_keys=True))
        return False

    github_json = json.loads(response.text)
    zip_path = download(github_json['zipball_url'], git_version + ".zip")
    tar_path = download(github_json['tarball_url'], git_version + ".tar.gz")

    print("Signing {}".format([zip_path, tar_path]))

    gpg_cmd = "gpg --default-key {} --detach-sign --armor {}"
    shell_cmd_runner(gpg_cmd.format(signing_key, zip_path))
    shell_cmd_runner(gpg_cmd.format(signing_key, tar_path))

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
        print(
            f'Could not run command "{e.cmd}". Error was:\n\n{e.stderr}',
            file=sys.stderr,
        )
        sys.exit(1)

    return sys.exit(0) if leave else True


if __name__ == '__main__':
    main()
