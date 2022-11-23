# Copyright (C) 2022 Greenbone Networks GmbH
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

from dataclasses import dataclass
from typing import List

from pontos.github.models.base import GitHubModel, User

__add__ = (
    "Release",
    "ReleaseAsset",
)


@dataclass
class ReleaseAsset(GitHubModel):
    url: str
    browser_download_url: str
    id: int
    node_id: str
    name: str
    label: str
    state: str
    content_type: str
    size: int
    download_count: int
    created_at: str
    updated_at: str
    uploader: User


@dataclass
class Release(GitHubModel):
    url: str
    html_url: str
    assets_url: str
    upload_url: str
    tarball_url: str
    zipball_url: str
    discussion_url: str
    id: int
    node_id: str
    tag_name: str
    target_commitish: str
    name: str
    body: str
    draft: bool
    prerelease: bool
    created_at: str
    published_at: str
    author: User
    assets: List[ReleaseAsset]
