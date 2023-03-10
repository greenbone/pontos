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
from enum import Enum
from typing import List, Optional

from pontos.github.models.base import FileStatus, GitHubModel, Team, User
from pontos.github.models.organization import Repository

__all__ = (
    "AuthorAssociation",
    "AutoMerge",
    "DiffEntry",
    "Label",
    "MergeMethod",
    "Milestone",
    "MilestoneState",
    "PullRequest",
    "PullRequestCommit",
    "PullRequestCommitDetails",
    "PullRequestCommitParent",
    "PullRequestCommitUser",
    "PullRequestCommitVerification",
    "PullRequestRef",
    "PullRequestState",
    "Stats",
    "Tree",
)


@dataclass
class PullRequestCommitUser(GitHubModel):
    """
    User information of a commit

    Attributes:
        name: Name of the user
        email: Email address of the user
        date:
    """

    name: str
    email: str
    date: datetime


@dataclass
class Tree(GitHubModel):
    """
    Git tree information

    Attributes:
        url: URL to the tree
        sha: Git ID of the tree
    """

    url: str
    sha: str


@dataclass
class PullRequestCommitVerification(GitHubModel):
    """
    Verification details of a pull request commit

    Attributes:
        verified: True if the commit is verified
        reason: Details of the verification
        signature: Signature of the verification
        payload: Payload of the verification
    """

    verified: bool
    reason: str
    signature: Optional[str] = None
    payload: Optional[str] = None


@dataclass
class PullRequestCommitDetails(GitHubModel):
    """
    Detailed information of a pull request commit

    Attributes:
        comment_count: Number of comments
        message: Commit message
        tree: Commit tree
        url: URL to the pull request commit
        verification: Verification details of the pull request commit
        author: Author of the pull request commit
        committer: Committer of the pull request commit
    """

    comment_count: int
    message: str
    tree: Tree
    url: str
    verification: PullRequestCommitVerification
    author: Optional[PullRequestCommitUser] = None
    committer: Optional[PullRequestCommitUser] = None


@dataclass
class PullRequestCommitParent(GitHubModel):
    """
    Pull request parent commit information

    Attributes:
        url: URL to the parent commit
        sha: Git commit ID of the parent commit
        html_url: URL to the web page of the parent commit
    """

    url: str
    sha: str
    html_url: Optional[str] = None


@dataclass
class Stats(GitHubModel):
    """
    Pull request commit stats

    Attributes:
        additions: Number of additions
        deletions: Number of deletions
        total: Total number of changes
    """

    additions: int
    deletions: int
    total: int


@dataclass
class DiffEntry(GitHubModel):
    """
    Diff information of a pull request commit

    Attributes:
        additions: Number of additions
        blob_url: URL to the binary blob
        changes: Number of changes
        contents_url: URL to the contents
        deletions: Number of deletions
        filename: Corresponding file name
        raw_url: URL to the raw content
        sha: Git commit ID of the change
        status: File status
        patch: Patch of the diff
        previous_filename: Previous file name
    """

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
    """
    Pull request commit

    Attributes:
        url: URL to the pull request commit
        sha: Git commit ID
        node_id: Node ID of the pull request commit
        html_url: URL to the web page of the pull request commit
        comments_url: URL to the pull request comments
        commit: Git commit object
        author: Author of the pull request commit
        stats: File stats of the pull request commit
        files: Diff information about the files in pull request commit
        committer: Committer of the pull request
        parents: List of parent commits
    """

    url: str
    sha: str
    node_id: str
    html_url: str
    comments_url: str
    commit: PullRequestCommitDetails
    author: User
    stats: Optional[Stats] = None
    files: List[DiffEntry] = field(default_factory=list)
    committer: Optional[User] = None
    parents: List[PullRequestCommitParent] = field(default_factory=list)


@dataclass
class Label(GitHubModel):
    """
    Pull request label

    Attributes:
        id: ID of the label
        node_id: Node ID of the label
        url: URL to the label
        name: Name of the label
        color: Color code of the label
        default: True if it is a default label
        description: Description of the label
    """

    id: int
    node_id: str
    url: str
    name: str
    color: str
    default: bool
    description: Optional[str] = None


class MilestoneState(Enum):
    """
    State of a pull request milestone (open, closed)

    Attributes:
        OPEN: Milestone is open
        CLOSED: Milestone is closed
    """

    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Milestone(GitHubModel):
    """
    Pull request milestone

    Attributes:
        closed_issues: Number of closed issues
        created_at: Creation date
        html_url: URL to the web page of the milestone
        id: ID of the milestone
        labels_url: URL to the labels of the milestone
        node_id: Node ID of the milestone
        number: Milestone number
        open_issues: Number of open issues in the milestone
        state: State of the milestone
        title: Title of the milestone
        updated_at: Last modification date
        url: URL of the milestone
        closed_at: Closed date
        creator: Use who created the milestone
        description: Description of the milestone
        due_on: Due date of the milestone
    """

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
    """
    Pull request reference

    Attributes:
        label: Label of the pull request reference
        ref: Pull request reference name
        sha: Git commit ID of pull request reference
        user: User who created the pull request reference
        repo: Corresponding repository
    """

    label: str
    ref: str
    sha: str
    user: User
    repo: Repository


class PullRequestState(Enum):
    """
    Pull request state

    Attributes:
        OPEN: Pull request is open
        CLOSED: Pull request is closed
    """

    OPEN = "open"
    CLOSED = "closed"


class AuthorAssociation(Enum):
    """
    Pull request author association

    Attributes:
        COLLABORATOR: Author is a collaborator
        CONTRIBUTOR: Author is a contributor
        FIRST_TIMER: First time pull request
        FIRST_TIME_CONTRIBUTOR: Author is a first time contributor
        MANNEQUIN: Author is a mannequin
        MEMBER: Author is a member
        NONE: None
        OWNER: Author is owner
    """

    COLLABORATOR = "COLLABORATOR"
    CONTRIBUTOR = "CONTRIBUTOR"
    FIRST_TIMER = "FIRST_TIMER"
    FIRST_TIME_CONTRIBUTOR = "FIRST_TIME_CONTRIBUTOR"
    MANNEQUIN = "MANNEQUIN"
    MEMBER = "MEMBER"
    NONE = "NONE"
    OWNER = "OWNER"


class MergeMethod(Enum):
    """
    The (auto) merge method

    Attributes:
        MERGE: Create a merge commit
        SQUASH: Squash commits into a single commit
        REBASE: Rebase commits onto the target branch
    """

    MERGE = "merge"
    SQUASH = "squash"
    REBASE = "rebase"


@dataclass
class AutoMerge(GitHubModel):
    """
    Auto merge information

    Attributes:
        enabled_by: User who enabled the auto merge
        merge_method: Method that is used for the auto merge
        commit_title: Commit title of the auto merge
        commit_message: Commit message of the auto merge
    """

    enabled_by: User
    merge_method: MergeMethod
    commit_title: str
    commit_message: str


@dataclass
class PullRequest(GitHubModel):
    """
    A GitHub pull request

    Attributes:
        additions: Number of changes
        author_association: Author role
        base: Reference to the source branch
        changed_files: Number of changed files
        comments_url: URL to the pull request comments
        comments: Number of comments
        commits_url: URL to the pull request commits
        commits: Number of commits
        created_at: Creation date
        deletions: Number of deletions
        diff_url: URL to the diff view
        head: Reference to the target branch
        html_url: URL to the web page of the pull request
        id: ID of the pull request
        issue_url: URL to the pull request
        locked: True if the pull request is locked
        maintainer_can_modify: True if the maintainer can modify the pull
            request
        mergeable_state: Mergeable state
        merged: True if the pull request is merged
        node_id: Node ID of the pull request
        number: Pull request number
        patch_url: URL to the diff patch
        review_comment_url:
        review_comments_url: URL to the reviewer comments
        review_comments: Number of reviewer comments
        state: State of the pull request
        statuses_url: URL of the pull request statuses
        title: Pull request title
        updated_at: Last modification date
        url: URL to the pull request
        user: User who created the pull request
        active_lock_reason: Optional[str] = None
        assignee: Assigned user
        assignees: List of assigned users
        auto_merge: True if the pull request should be merged automatically
        body: Body text of the pull request
        closed_at: Date when the pull request was closed
        draft: True if the pull request is a draft
        labels: List of assigned labels
        merge_commit_sha: Git commit ID of the merge commit
        mergeable: True if the pull request is mergeable
        merged_at: Date when the pull request got merged
        merged_by: User who merged the pull request
        milestone: A connected milestone
        rebaseable: True if the pull request is rebaseable
        requested_reviewers: List of users requested as reviewers
        requested_teams: List of teams requested as reviewers
    """

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
