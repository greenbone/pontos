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

from pontos.github.models.base import GitHubModel, Team, User
from pontos.github.models.organization import Repository

__all__ = ("PullRequest",)


@dataclass
class CommitUser(GitHubModel):
    name: str
    email: str
    date: str


@dataclass
class Tree(GitHubModel):
    url: str
    sha: str


@dataclass
class CommitVerification(GitHubModel):
    verified: bool
    reason: str
    signature: Optional[str] = None
    payload: Optional[str] = None


@dataclass
class Commit(GitHubModel):
    url: str
    author: CommitUser
    committer: CommitUser
    message: str
    tree: Tree
    comment_count: str
    verification: CommitVerification


@dataclass
class CommitParent(GitHubModel):
    url: str
    sha: str


@dataclass
class PullRequestCommit(GitHubModel):
    url: str
    sha: str
    node_id: str
    html_url: str
    comments_url: str
    commit: Commit
    author: User
    committer: User
    parents: List[CommitParent]


@dataclass
class Label(GitHubModel):
    id: int
    node_id: str
    url: str
    name: str
    description: str
    color: str
    default: bool


@dataclass
class Milestone(GitHubModel):
    url: str
    html_url: str
    labels_url: str
    id: int
    node_id: str
    number: int
    state: str
    title: str
    description: str
    creator: User
    open_issues: int
    closed_issues: int
    created_at: str
    updated_at: str
    closed_at: str
    due_on: str


@dataclass
class PullRequestRef(GitHubModel):
    label: str
    ref: str
    sha: str
    user: User
    repo: Repository


@dataclass
class PullRequest(GitHubModel):
    url: str
    id: int
    node_id: str
    html_url: str
    diff_url: str
    patch_url: str
    issue_url: str
    commits_url: str
    review_comments_url: str
    review_comment_url: str
    comments_url: str
    statuses_url: str
    number: int
    state: str
    locked: bool
    title: str
    user: User
    body: str
    labels: List[Label]
    milestone: Milestone
    active_lock_reason: str
    created_at: str
    updated_at: str
    closed_at: str
    merged_at: str
    merge_commit_sha: str
    assignee: User
    assignees: List[User]
    requested_reviewers: List[User]
    requested_teams: List[Team]
    head: PullRequestRef
    base: PullRequestRef
    author_association: str
    draft: bool
    merged: bool
    mergeable: bool
    rebaseable: bool
    mergeable_state: str
    merged_by: User
    comments: int
    review_comments: int
    maintainer_can_modify: bool
    commits: int
    additions: int
    deletions: int
    changed_files: int
    auto_merge: Optional[bool] = None
