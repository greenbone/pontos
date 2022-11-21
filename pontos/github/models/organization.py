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
from typing import List, Optional

from pontos.github.models.base import GitHubModel, User

__all__ = (
    "License",
    "Repository",
)


@dataclass
class License(GitHubModel):
    key: str
    name: str
    url: str
    spdx_id: str
    node_id: str
    html_url: Optional[str] = None


@dataclass
class Repository(GitHubModel):
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: User
    html_url: str
    description: str
    fork: bool
    url: str
    forks_url: str
    keys_url: str
    collaborators_url: str
    teams_url: str
    hooks_url: str
    issue_events_url: str
    events_url: str
    assignees_url: str
    branches_url: str
    tags_url: str
    blobs_url: str
    git_tags_url: str
    git_refs_url: str
    trees_url: str
    statuses_url: str
    languages_url: str
    stargazers_url: str
    contributors_url: str
    subscribers_url: str
    subscription_url: str
    commits_url: str
    git_commits_url: str
    comments_url: str
    issue_comment_url: str
    contents_url: str
    compare_url: str
    merges_url: str
    archive_url: str
    downloads_url: str
    issues_url: str
    pulls_url: str
    milestones_url: str
    notifications_url: str
    labels_url: str
    releases_url: str
    deployments_url: str
    created_at: str
    updated_at: str
    pushed_at: str
    git_url: str
    ssh_url: str
    clone_url: str
    svn_url: str
    homepage: str
    stargazers_count: int
    watchers_count: int
    language: str
    has_issues: bool
    has_projects: bool
    has_downloads: bool
    has_wiki: bool
    has_pages: bool
    has_discussions: bool
    forks_count: int
    mirror_url: str
    archived: bool
    disabled: bool
    open_issues_count: int
    license: License
    is_template: bool
    topics: List[str]
    visibility: str
    forks: int
    open_issues: int
    watchers: int
    default_branch: str
    allow_forking: Optional[bool] = None
    allow_rebase_merge: Optional[bool] = None
    allow_squash_merge: Optional[bool] = None
    allow_auto_merge: Optional[bool] = None
    delete_branch_on_merge: Optional[bool] = None
    allow_merge_commit: Optional[bool] = None
    web_commit_signoff_required: Optional[bool] = None
    subscribers_count: Optional[int] = None
    network_count: Optional[int] = None
    size: Optional[int] = None