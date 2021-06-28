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

import datetime
import json
import subprocess
import sys
import tempfile

from pathlib import Path
from typing import Callable, Dict, List, Tuple, Union
from packaging.version import InvalidVersion, Version

import requests

from pontos import version
from pontos.terminal import error, warning, info, ok, out, overwrite
from pontos.terminal.terminal import Signs
from pontos.version.helper import VersionError
from pontos.version import (
    PontosVersionCommand,
    CMakeVersionCommand,
)

DEFAULT_TIMEOUT = 1000
DEFAULT_CHUNK_SIZE = 4096


def build_release_dict(
    release_version: str,
    release_changelog: str,
    *,
    name: str = '',
    target_commitish: str = '',
    draft: bool = False,
    prerelease: bool = False,
) -> Dict[str, Union[str, bool]]:
    """
    builds the dict for release post on github, see:
    https://docs.github.com/en/rest/reference/repos#create-a-release
    for more details.

    Arguments:
        release_version: The version (str) that will be set
        release_changelog: content of the Changelog (str) for the release
        name: name (str) of the release, e.g. 'pontos 1.0.0'
        target_commitish: needed when tag is not there yet (str)
        draft: If the release is a draft (bool)
        prerelease: If the release is a pre release (bool)

    Returns:
        The dictionary containing the release information.
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


def commit_files(
    filename: str,
    commit_msg: str,
    shell_cmd_runner: Callable,
    *,
    git_signing_key: str = '',
):
    """Add files to staged and commit staged files.

    filename: The filename of file to add and commit
    commit_msg: The commit message for the commit
    shell_cmd_runner: The runner for shell commands
    git_signing_key: The signing key to sign this commit

    Arguments:
        to: The version (str) that will be set
        develop: Wether to set version to develop or not (bool)

    Returns:
       executed: True if successfully executed, False else
       filename: The filename of the project definition
    """

    shell_cmd_runner(f"git add {filename}")
    shell_cmd_runner("git add *__version__.py || echo 'ignoring __version__'")
    shell_cmd_runner("git add CHANGELOG.md")
    if git_signing_key:
        shell_cmd_runner(
            f"git commit -S {git_signing_key} --no-verify -m '{commit_msg}'",
        )
    else:
        shell_cmd_runner(f"git commit --no-verify -m '{commit_msg}'")


def calculate_calendar_version() -> str:
    """find the correct next calendar version by checking latest version and
    the today's date"""

    current_version_str: str = get_current_version()
    current_version = Version(current_version_str)

    today = datetime.date.today()

    if (
        current_version.major < today.year % 100
        or current_version.minor < today.month
    ):
        release_version = Version(
            f'{str(today.year  % 100)}.{str(today.month)}.0'
        )
        return str(release_version)
    elif (
        current_version.major == today.year % 100
        and current_version.minor == today.month
    ):
        if current_version.dev is None:
            release_version = Version(
                f'{str(today.year  % 100)}.{str(today.month)}.'
                f'{str(current_version.micro + 1)}'
            )
        else:
            release_version = Version(
                f'{str(today.year  % 100)}.{str(today.month)}.'
                f'{str(current_version.micro)}'
            )
        return str(release_version)
    else:
        error(
            f"'{str(current_version)}' is higher than "
            f"'{str(today.year  % 100)}.{str(today.month)}'."
        )
        sys.exit(1)


def download(
    url: str,
    filename: str,
    requests_module: requests,
    path: Path,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout: int = DEFAULT_TIMEOUT,
) -> Path:
    """Download file in url to filename

    Arguments:
        url: The url of the file we want to download
        filename: The name of the file to store the download in
        requests_module: the python request module
        path: the python pathlib.Path module

    Returns:
       Path to the downloaded file
    """

    file_path: Path = path(tempfile.gettempdir()) / filename
    response = requests_module.get(url, stream=True, timeout=timeout)
    total_length = response.headers.get('content-length')

    info(f'Downloading {url}')

    if total_length is not None:  # no content length header
        with file_path.open(mode='wb') as download_file:
            dl = 0
            total_length = int(total_length)
            for content in response.iter_content(chunk_size=chunk_size):
                dl += len(content)
                download_file.write(content)
                done = int(50 * dl / total_length)
                overwrite(f"[{'=' * done}{' ' * (50-done)}]")
    else:
        with file_path.open(mode='wb') as download_file:
            spinner = ['-', '\\', '|', '/']
            i = 0
            for content in response.iter_content(chunk_size=chunk_size):
                i = i + 1
                if i == 4:
                    i = 0
                download_file.write(content)
                overwrite(f"[{spinner[i]}]")
    overwrite(f"[{Signs.OK}]{' ' * 50}", new_line=True)

    return file_path


def download_assets(
    assets_url: str,
    path: Path,
    requests_module: requests,
) -> List[str]:
    """Download all .tar.gz and zip assets of a github release"""

    file_paths = []
    if not assets_url:
        return file_paths

    if assets_url:
        assets_response = requests_module.get(assets_url)
        if assets_response.status_code != 200:
            error(
                f"Wrong response status code {assets_response.status_code} for "
                f" request {assets_url}"
            )
            out(json.dumps(assets_response.text, indent=4, sort_keys=True))
        else:
            assets_json = assets_response.json()
            for asset_json in assets_json:
                asset_url: str = asset_json.get('browser_download_url', '')
                name: str = asset_json.get('name', '')
                if name.endswith('.zip') or name.endswith('.tar.gz'):
                    asset_path = download(
                        asset_url,
                        name,
                        path=path,
                        requests_module=requests_module,
                    )
                    file_paths.append(asset_path)

    return file_paths


def get_current_version() -> str:
    """Get the current Version from a pyproject.toml or
    a CMakeLists.txt file"""

    available_cmds = [
        ('CMakeLists.txt', CMakeVersionCommand),
        ('pyproject.toml', PontosVersionCommand),
    ]
    for file_name, cmd in available_cmds:
        project_definition_path = Path.cwd() / file_name
        if project_definition_path.exists():
            ok(f"Found {file_name} project definition file.")
            current_version: str = cmd().get_current_version()
            return current_version

    error("No project settings file found")
    sys.exit(1)


def get_next_patch_version() -> str:
    """find the correct next patch version by checking latest version"""

    current_version_str: str = get_current_version()
    current_version = Version(current_version_str)

    if current_version.dev is not None:
        release_version = Version(
            f'{str(current_version.major)}.'
            f'{str(current_version.minor)}.'
            f'{str(current_version.micro)}'
        )
    else:
        release_version = Version(
            f'{str(current_version.major)}.'
            f'{str(current_version.minor)}.'
            f'{str(current_version.micro + 1)}'
        )

    return str(release_version)


def get_next_dev_version(release_version: str) -> str:
    """Get the next dev Version from a valid version"""
    # will be a dev1 version
    try:
        release_version_obj = Version(release_version)
        next_version_obj = Version(
            f'{str(release_version_obj.major)}.'
            f'{str(release_version_obj.minor)}.'
            f'{str(release_version_obj.micro + 1)}'
        )
        return str(next_version_obj)
    except InvalidVersion as e:
        raise (VersionError(e)) from None


def get_project_name(
    shell_cmd_runner: Callable,
    *,
    remote: str = 'origin',
) -> str:
    """Get the git repository name

    Arguments:
        shell_cmd_runner: The runner for shell commands
        remote: the remote to look up the name (str) default: origin

    Returns:
        project name
    """
    ret = shell_cmd_runner(f'git remote get-url {remote}')
    return ret.stdout.split('/')[-1].replace('.git', '').strip()


def find_signing_key(shell_cmd_runner: Callable) -> str:
    """Find the signing key in the config

    Arguments:
        shell_cmd_runner: The runner for shell commands

    Returns:
        git signing key or empty string
    """

    try:
        proc = shell_cmd_runner('git config user.signingkey')
    except subprocess.CalledProcessError as e:
        # The command `git config user.signingkey` returns
        # return code 1 if no key is set.
        # So we will return empty string ...
        if e.returncode == 1:
            warning("No signing key found.")
        return ''
    # stdout should return "\n" if no key is available
    # and so git_signing_key should
    # return '' if no key is available ...
    return proc.stdout.strip()


def update_version(
    to: str, _version: version, *, develop: bool = False
) -> Tuple[bool, str]:
    """Use pontos-version to update the version.

    Arguments:
        to: The version (str) that will be set
        _version: Version module
        develop: Wether to set version to develop or not (bool)

    Returns:
       executed: True if successfully executed, False else
       filename: The filename of the project definition
    """
    args = ['--quiet']
    args.append('update')
    args.append(to)
    if develop:
        args.append('--develop')
    executed, filename = _version.main(leave=False, args=args)

    if not executed:
        if filename == "":
            error("No project definition found.")
        else:
            error(f"Unable to update version {to} in {filename}")

    return executed, filename


def upload_assets(
    username: str,
    token: str,
    file_paths: List[Path],
    github_json: Dict,
    path: Path,
    requests_module: requests,
) -> bool:
    """Function to upload assets

    Arguments:
        username: The GitHub username to use for the upload
        token: That username's GitHub token
        file_paths: List of paths to asset files
        github_json: The github dictionary, containing relevant information
            for the upload
        path: the python pathlib.Path module
        requests_module: the python request module

    Returns:
        True on success, false else
    """
    info(f"Uploading assets: {[str(p) for p in file_paths]}")

    asset_url = github_json['upload_url'].replace('{?name,label}', '')
    paths = [path(f'{str(p)}.asc') for p in file_paths]

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'content-type': 'application/octet-stream',
    }
    auth = (username, token)

    for file_path in paths:
        to_upload = file_path.read_bytes()
        resp = requests_module.post(
            f"{asset_url}?name={file_path.name}",
            headers=headers,
            auth=auth,
            data=to_upload,
        )

        if resp.status_code != 201:
            error(
                f"Wrong response status {resp.status_code}"
                f" while uploading {file_path.name}"
            )
            out(json.dumps(resp.text, indent=4, sort_keys=True))
            return False
        else:
            ok(f"Uploaded: {file_path.name}")

    return True
