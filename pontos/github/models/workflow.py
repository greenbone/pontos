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
from typing import Dict, List, Optional

from pontos.github.models.base import GitHubModel, User

__all__ = ("Workflow", "WorkflowRun")


@dataclass
class CommitUser(GitHubModel):
    name: str
    email: str


@dataclass
class WorkflowRunCommit(GitHubModel):
    id: str
    tree_id: str
    message: str
    timestamp: str
    author: CommitUser
    committer: CommitUser


@dataclass
class Workflow(GitHubModel):
    id: int
    node_id: str
    name: str
    path: str
    state: str
    created_at: str
    updated_at: str
    url: str
    html_url: str
    badge_url: str


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


@dataclass
class WorkflowRun(GitHubModel):
    id: int
    name: str
    node_id: str
    check_suite_id: int
    check_suite_node_id: str
    head_branch: str
    head_sha: str
    run_number: int
    event: str
    status: str
    conclusion: Optional[str]
    workflow_id: int
    url: str
    html_url: str
    pull_requests: List[Dict]
    created_at: str
    updated_at: str
    actor: User
    run_attempt: int
    run_started_at: str
    triggering_actor: User
    jobs_url: str
    logs_url: str
    check_suite_url: str
    artifacts_url: str
    cancel_url: str
    rerun_url: str
    workflow_url: str
    head_commit: WorkflowRunCommit
    repository: WorkflowRunRepository
    head_repository: WorkflowRunRepository