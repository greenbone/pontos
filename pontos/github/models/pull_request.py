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

from pontos.github.models.base import GitHubModel, Team, User
from pontos.github.models.organization import Repository

__all__ = (
    "AuthorAssociation",
    "FileStatus",
    "MergeMethod",
    "MilestoneState",
    "PullRequest",
    "PullRequestCommit",
    "PullRequestState",
)


@dataclass
class CommitUser(GitHubModel):
    name: str
    email: str
    date: datetime


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
    comment_count: int
    message: str
    tree: Tree
    url: str
    verification: CommitVerification
    author: Optional[CommitUser] = None
    committer: Optional[CommitUser] = None


@dataclass
class CommitParent(GitHubModel):
    url: str
    sha: str
    html_url: Optional[str] = None


@dataclass
class Stats(GitHubModel):
    additions: int
    deletions: int
    total: int


class FileStatus(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    RENAMED = "renamed"
    COPIED = "copied"
    CHANGED = "changed"
    UNCHANGED = "unchanged"


@dataclass
class DiffEntry(GitHubModel):
    additions: int
    blob_url: str
    changes: int
    contents_url: str
    deletions: int
    filename: str
    raw_url: str
    sha: str
    status: FileStatus
    patch: Optional[str] = None
    previous_filename: Optional[str] = None


@dataclass
class PullRequestCommit(GitHubModel):
    url: str
    sha: str
    node_id: str
    html_url: str
    comments_url: str
    commit: Commit
    author: User
    stats: Optional[Stats] = None
    files: List[DiffEntry] = field(default_factory=list)
    committer: Optional[User] = None
    parents: List[CommitParent] = field(default_factory=list)


@dataclass
class Label(GitHubModel):
    id: int
    node_id: str
    url: str
    name: str
    color: str
    default: bool
    description: Optional[str] = None


class MilestoneState(Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Milestone(GitHubModel):
    closed_issues: int
    created_at: datetime
    html_url: str
    id: int
    labels_url: str
    node_id: str
    number: int
    open_issues: int
    state: MilestoneState
    title: str
    updated_at: datetime
    url: str
    closed_at: Optional[datetime] = None
    creator: Optional[User] = None
    description: Optional[str] = None
    due_on: Optional[datetime] = None


@dataclass
class PullRequestRef(GitHubModel):
    label: str
    ref: str
    sha: str
    user: User
    repo: Repository


class PullRequestState(Enum):
    OPEN = "open"
    CLOSED = "closed"


class AuthorAssociation(Enum):
    COLLABORATOR = "COLLABORATOR"
    CONTRIBUTOR = "CONTRIBUTOR"
    FIRST_TIMER = "FIRST_TIMER"
    FIRST_TIME_CONTRIBUTOR = "FIRST_TIME_CONTRIBUTOR"
    MANNEQUIN = "MANNEQUIN"
    MEMBER = "MEMBER"
    NONE = "NONE"
    OWNER = "OWNER"


class MergeMethod(Enum):
    MERGE = "merge"
    SQUASH = "squash"
    REBASE = "rebase"


@dataclass
class AutoMerge(GitHubModel):
    enabled_by: User
    merge_method: MergeMethod
    commit_title: str
    commit_message: str


@dataclass
class PullRequest(GitHubModel):
    additions: int
    author_association: AuthorAssociation
    base: PullRequestRef
    changed_files: int
    comments_url: str
    comments: int
    commits_url: str
    commits: int
    created_at: datetime
    deletions: int
    diff_url: str
    head: PullRequestRef
    html_url: str
    id: int
    issue_url: str
    locked: bool
    maintainer_can_modify: bool
    mergeable_state: str
    merged: bool
    node_id: str
    number: int
    patch_url: str
    review_comment_url: str
    review_comments_url: str
    review_comments: int
    state: PullRequestState
    statuses_url: str
    title: str
    updated_at: datetime
    url: str
    user: User
    active_lock_reason: Optional[str] = None
    assignee: Optional[User] = None
    assignees: List[User] = field(default_factory=list)
    auto_merge: Optional[AutoMerge] = None
    body: Optional[str] = None
    closed_at: Optional[datetime] = None
    draft: Optional[bool] = None
    labels: List[Label] = field(default_factory=list)
    merge_commit_sha: Optional[str] = None
    mergeable: Optional[bool] = None
    merged_at: Optional[datetime] = None
    merged_by: Optional[User] = None
    milestone: Optional[Milestone] = None
    rebaseable: Optional[bool] = None
    requested_reviewers: List[User] = field(default_factory=list)
    requested_teams: List[Team] = field(default_factory=list)
