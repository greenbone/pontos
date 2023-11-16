# Copyright (C) 2022 Greenbone AG
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
from typing import List, Optional

from pontos.github.models.base import GitHubModel, User
from pontos.models import StrEnum

__all__ = (
    "Release",
    "ReleaseAsset",
    "ReleaseAssetState",
    "ReleaseReactions",
)


class ReleaseAssetState(StrEnum):
    """
    State of a release asset

    Attributes:
        UPLOADED: Uploaded
        OPEN: Open
    """

    UPLOADED = "uploaded"
    OPEN = "open"


@dataclass
class ReleaseAsset(GitHubModel):
    """
    A GitHub release asset model

    Attributes:
        url: URL of the release asset
        browser_download_url: Direct URL to download the asset from
        id: ID of the asset
        node_id: Node ID of the asset
        name: Name of the asset
        state: State of the asset
        content_type: MIME content type of the asset
        size: Size of the asset
        download_count: Number of downloads
        created_at: Creation date
        updated_at: Upload date
        label: Label of the asset
        uploader: User who uploaded the asset
    """

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
class ReleaseReactions(GitHubModel):
    """
    Reactions to a GitHub release

    Attributes:
        url: URL to the release reactions
        total_count: Total number of reactions
        laugh: Number of user reacted with laugh
        confused: Number of user reacted with confused
        heart: Number of user reacted with heart
        hooray: Number of user reacted with hooray
        eyes: Number of user reacted with eyes
        rocket: Number of user reacted with rocket
    """

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
    """
    A GitHub release model

    Attributes:
        assets_url: URL to the release assets
        created_at: Creation Date
        draft: True if the release is a draft
        html_url: URL to the web page of the release
        id: ID of the release
        node_id: Node ID of the release
        prerelease: True if the release is a pre release
        tag_name: Name of the tag referenced by the release
        target_commitish: Git commit ID of the tag references by the release
        upload_url: URL to upload release assets to
        url: URL of the release
        assets: Information about the release assets
        author: User created the release
        body_html: Body of the release as HTML
        body_text: Body of the release as text
        body: Body of the release
        discussion_url: URL to the release discussion
        mentions_count:
        name: Name of the release
        published_at: Publication date of the release
        reactions: Reaction information
        tarball_url: URL to the tarball archive of the release
        zipball_url: URL to the zip archive of the release
    """

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
    reactions: Optional[ReleaseReactions] = None
    tarball_url: Optional[str] = None
    zipball_url: Optional[str] = None
