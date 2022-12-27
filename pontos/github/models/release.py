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

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pontos.github.models.base import GitHubModel, User

__add__ = (
    "Release",
    "ReleaseAsset",
    "ReleaseAssetState",
)


class ReleaseAssetState(Enum):
    UPLOADED = "uploaded"
    OPEN = "open"


@dataclass
class ReleaseAsset(GitHubModel):
    url: str
    browser_download_url: str
    id: int
    node_id: str
    name: str
    state: ReleaseAssetState
    content_type: str
    size: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    label: Optional[str] = None
    uploader: Optional[User] = None


@dataclass
class Reactions(GitHubModel):
    url: str
    total_count: int
    laugh: int
    confused: int
    heart: int
    hooray: int
    eyes: int
    rocket: int


@dataclass
class Release(GitHubModel):
    assets_url: str
    created_at: datetime
    draft: bool
    html_url: str
    id: int
    node_id: str
    prerelease: bool
    tag_name: str
    target_commitish: str
    upload_url: str
    url: str
    assets: List[ReleaseAsset] = field(default_factory=list)
    author: Optional[User] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    body: Optional[str] = None
    discussion_url: Optional[str] = None
    mentions_count: Optional[int] = None
    name: Optional[str] = None
    published_at: Optional[datetime] = None
    reactions: Optional[Reactions] = None
    tarball_url: Optional[str] = None
    zipball_url: Optional[str] = None
