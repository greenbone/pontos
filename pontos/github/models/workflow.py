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
from typing import Dict, List, Optional

from pontos.github.models.base import Event, GitHubModel, User

__all__ = (
    "Workflow",
    "WorkflowState",
    "WorkflowRun",
    "WorkflowRunStatus",
)


@dataclass
class CommitUser(GitHubModel):
    name: str
    email: str


@dataclass
class WorkflowRunCommit(GitHubModel):
    id: str
    tree_id: str
    message: str
    timestamp: datetime
    author: Optional[CommitUser] = None
    committer: Optional[CommitUser] = None


class WorkflowState(Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    DISABLED_FORK = "disabled_fork"
    DISABLED_INACTIVITY = "disabled_inactivity"
    DISABLED_MANUALLY = "disabled_manually"


@dataclass
class Workflow(GitHubModel):
    id: int
    node_id: str
    name: str
    path: str
    state: WorkflowState
    created_at: datetime
    updated_at: datetime
    url: str
    html_url: str
    badge_url: str
    deleted_at: Optional[datetime] = None


@dataclass
class WorkflowRunRepository(GitHubModel):
    id: int
    url: str
    name: str
    node_id: str
    full_name: Optional[str] = None
    owner: Optional[User] = None
    private: Optional[bool] = None
    html_url: Optional[str] = None
    description: Optional[str] = None
    fork: Optional[bool] = None
    archive_url: Optional[str] = None
    assignees_url: Optional[str] = None
    blobs_url: Optional[str] = None
    branches_url: Optional[str] = None
    collaborators_url: Optional[str] = None
    comments_url: Optional[str] = None
    commits_url: Optional[str] = None
    compare_url: Optional[str] = None
    contents_url: Optional[str] = None
    contributors_url: Optional[str] = None
    deployments_url: Optional[str] = None
    downloads_url: Optional[str] = None
    events_url: Optional[str] = None
    forks_url: Optional[str] = None
    git_commits_url: Optional[str] = None
    git_refs_url: Optional[str] = None
    git_tags_url: Optional[str] = None
    git_url: Optional[str] = None
    issue_comment_url: Optional[str] = None
    issue_events_url: Optional[str] = None
    issues_url: Optional[str] = None
    keys_url: Optional[str] = None
    labels_url: Optional[str] = None
    languages_url: Optional[str] = None
    merges_url: Optional[str] = None
    milestones_url: Optional[str] = None
    notifications_url: Optional[str] = None
    pulls_url: Optional[str] = None
    releases_url: Optional[str] = None
    ssh_url: Optional[str] = None
    stargazers_url: Optional[str] = None
    statuses_url: Optional[str] = None
    subscribers_url: Optional[str] = None
    subscription_url: Optional[str] = None
    tags_url: Optional[str] = None
    teams_url: Optional[str] = None
    trees_url: Optional[str] = None
    hooks_url: Optional[str] = None


class WorkflowRunStatus(Enum):
    ACTION_REQUIRED = "action_required"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILURE = "failure"
    IN_PROGRESS = "in_progress"
    NEUTRAL = "neutral"
    QUEUED = "queued"
    REQUESTED = "requested"
    SKIPPED = "skipped"
    STALE = "stale"
    SUCCESS = "success"
    TIMED_OUT = "timed_out"
    WAITING = "waiting"
    PENDING = "pending"  # not listed in GitHub docs


@dataclass
class WorkflowRunWorkflow(GitHubModel):
    path: str
    sha: str
    ref: Optional[str] = None


@dataclass
class WorkflowRun(GitHubModel):
    artifacts_url: str
    cancel_url: str
    check_suite_url: str
    created_at: datetime
    event: Event
    head_repository: WorkflowRunRepository
    head_sha: str
    html_url: str
    id: int
    jobs_url: str
    logs_url: str
    node_id: str
    repository: WorkflowRunRepository
    rerun_url: str
    run_number: int
    updated_at: datetime
    url: str
    workflow_id: int
    workflow_url: str
    actor: Optional[User] = None
    check_suite_id: Optional[int] = None
    check_suite_node_id: Optional[str] = None
    conclusion: Optional[str] = None
    display_title: Optional[str] = None
    head_branch: Optional[str] = None
    head_commit: Optional[WorkflowRunCommit] = None
    head_repository_id: Optional[int] = None
    name: Optional[str] = None
    path: Optional[str] = None
    previous_attempt_url: Optional[str] = None
    pull_requests: List[Dict] = field(default_factory=list)
    referenced_workflows: List[WorkflowRunWorkflow] = field(
        default_factory=list
    )
    run_attempt: Optional[int] = None
    run_started_at: Optional[datetime] = None
    status: Optional[WorkflowRunStatus] = None
    triggering_actor: Optional[User] = None
