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

from pontos.terminal import error, info, out

from .helper import (
    download,
    get_current_version,
    get_project_name,
    upload_assets,
    download_assets,
)


def sign(
    shell_cmd_runner: Callable,
    args: Namespace,
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
        error(
            f"Wrong response status code {response.status_code} for request "
            f"{base_url}"
        )
        out(json.dumps(response.text, indent=4, sort_keys=True))
        return False

    zipball_url = (
        f"https://github.com/{space}/{project}/archive/refs/"
        f"tags/{git_version}.zip"
    )
    github_json = json.loads(response.text)
    zip_path = download(
        zipball_url,
        f"{project}-{release_version}.zip",
        path=path,
        requests_module=requests_module,
    )
    tarball_url = (
        f"https://github.com/{space}/{project}/archive/refs/"
        f"tags/{git_version}.tar.gz"
    )
    tar_path = download(
        tarball_url,
        f"{project}-{release_version}.tar.gz",
        path=path,
        requests_module=requests_module,
    )

    file_paths = [zip_path, tar_path]

    asset_paths = download_assets(
        github_json.get('assets_url'),
        path=path,
        requests_module=requests_module,
    )

    file_paths.extend(asset_paths)

    for file_path in file_paths:
        info(f"Signing {file_path}")

        if args.passphrase:
            shell_cmd_runner(
                f"gpg --pinentry-mode loopback --default-key {signing_key}"
                f" --yes --detach-sign --passphrase {args.passphrase}"
                f" --armor {file_path}"
            )
        else:
            shell_cmd_runner(
                f"gpg --default-key {signing_key} --yes --detach-sign --armor "
                f"{file_path}"
            )

    return upload_assets(
        username,
        token,
        file_paths,
        github_json,
        path=path,
        requests_module=requests_module,
    )
