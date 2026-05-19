# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from dataclasses import dataclass, field
from datetime import datetime

from pontos.github.models.base import Event, GitHubModel, User
from pontos.models import StrEnum

__all__ = (
    "Workflow",
    "WorkflowRun",
    "WorkflowRunCommit",
    "WorkflowRunCommitUser",
    "WorkflowRunRepository",
    "WorkflowRunStatus",
    "WorkflowRunWorkflow",
    "WorkflowState",
)


@dataclass
class WorkflowRunCommitUser(GitHubModel):
    """
    User information of a workflow run commit

    Attributes:
        name: Name of the user
        email: Email address of the user
    """

    name: str
    email: str


@dataclass
class WorkflowRunCommit(GitHubModel):
    """
    GitHub workflow run commit reference

    Attributes:
        id: ID of the commit
        tree_id: Tree ID of the commit
        message: Message of the commit
        timestamp: Timestamp of the commit
        author: Author of the commit
        committer: Committer of the commit
    """

    id: str
    tree_id: str
    message: str
    timestamp: datetime
    author: WorkflowRunCommitUser | None = None
    committer: WorkflowRunCommitUser | None = None


class WorkflowState(StrEnum):
    """
    State of a workflow

    Attributes:
        ACTIVE: Workflow is active
        DELETED: Workflow is deleted
        DISABLED_FORK: Workflow is disabled because it is run from a fork
        DISABLED_INACTIVITY: Workflow is disabled because if inactivity
        DISABLED_MANUALLY: Workflow is disabled manually
    """

    ACTIVE = "active"
    DELETED = "deleted"
    DISABLED_FORK = "disabled_fork"
    DISABLED_INACTIVITY = "disabled_inactivity"
    DISABLED_MANUALLY = "disabled_manually"


@dataclass
class Workflow(GitHubModel):
    """
    GitHub workflow

    Attributes:
        id: ID of the workflow
        node_id: Node ID of the workflow
        name: Name of the workflow
        path: Path of the workflow file
        state: State of the workflow
        created_at: Creation date
        updated_at: Last modification date
        url: URL to the workflow
        html_url: URL to the web page of the workflow
        badge_url: URL to the workflow status badge
        deleted_at: Deletion date of the workflow
    """

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
    deleted_at: datetime | None = None


@dataclass
class WorkflowRunRepository(GitHubModel):
    """
    GitHub workflow run repository

    Attributes:
        id: ID of the repository
        url: URL to the repository
        name: Name of the repository
        node_id: Node ID of the repository
        full_name: Full name of the repository
        owner: Owner of the repository
        private: True if the repository is private
        html_url: URL to the web page of the repository
        description: Description of the repository
        fork: True if the repository is a fork
        archive_url: URL to the archive of the repository
        assignees_url: URL to the assignees
        blobs_url: URL to the binary blobs
        branches_url: URL to the branches
        collaborators_url: URL to the collaborators
        comments_url: URL to the comments
        commits_url: URL to commits
        compare_url: URL to compare
        contents_url: URL to the contents
        contributors_url: URL to the contributors
        deployments_url: URL to deployments
        downloads_url: URL to downloads
        events_url: URL to the events
        forks_url: URL to the forks of the repository
        git_commits_url: URL to the commits of the repository
        git_refs_url: URL to the git refs
        git_tags_url: URL to the git tags
        git_url: Git clone URL
        issue_comment_url: URL to the issue comments
        issue_events_url: URL to the issue events
        issues_url: URL to the issues
        keys_url: URL to the keys
        labels_url: URL to the labels
        languages_url: URL to the languages
        merges_url: URL to the merges
        milestones_url: URL to the milestones
        notifications_url: URL to the notifications
        pulls_url: URL to the pull requests
        releases_url: URL to releases
        ssh_url: Git clone URL using ssh
        stargazers_url: URL to the stargazers
        statuses_url: URL to the statuses
        subscribers_url: URL to the subscribers
        subscription_url: URL to subscribe to the repository
        tags_url: URL to the tags
        teams_url: URL to the teams
        trees_url: URL to the trees
        hooks_url: URL to the hooks
    """

    id: int
    url: str
    name: str
    node_id: str
    full_name: str | None = None
    owner: User | None = None
    private: bool | None = None
    html_url: str | None = None
    description: str | None = None
    fork: bool | None = None
    archive_url: str | None = None
    assignees_url: str | None = None
    blobs_url: str | None = None
    branches_url: str | None = None
    collaborators_url: str | None = None
    comments_url: str | None = None
    commits_url: str | None = None
    compare_url: str | None = None
    contents_url: str | None = None
    contributors_url: str | None = None
    deployments_url: str | None = None
    downloads_url: str | None = None
    events_url: str | None = None
    forks_url: str | None = None
    git_commits_url: str | None = None
    git_refs_url: str | None = None
    git_tags_url: str | None = None
    git_url: str | None = None
    issue_comment_url: str | None = None
    issue_events_url: str | None = None
    issues_url: str | None = None
    keys_url: str | None = None
    labels_url: str | None = None
    languages_url: str | None = None
    merges_url: str | None = None
    milestones_url: str | None = None
    notifications_url: str | None = None
    pulls_url: str | None = None
    releases_url: str | None = None
    ssh_url: str | None = None
    stargazers_url: str | None = None
    statuses_url: str | None = None
    subscribers_url: str | None = None
    subscription_url: str | None = None
    tags_url: str | None = None
    teams_url: str | None = None
    trees_url: str | None = None
    hooks_url: str | None = None


class WorkflowRunStatus(StrEnum):
    """
    Status of a workflow run

    Attributes:
        ACTION_REQUIRED: Use action is required
        CANCELLED: The workflow run is canceled
        COMPLETED: The workflow run is completed
        FAILURE: The workflow run failed
        IN_PROGRESS: The workflow run is in progress
        NEUTRAL: Neutral
        QUEUED: The workflow run is queued
        REQUESTED: The workflow run is requested
        SKIPPED: The workflow run is skipped
        STALE: The workflow run is stale
        SUCCESS: The workflow run is finished successfully
        TIMED_OUT: The workflow run has timed out
        WAITING: The workflow run is waiting
        PENDING: The workflow run is pending
    """

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
    """
    GitHub workflow of a workflow run

    Attributes:
        path: Path to the workflow file
        sha: Git commit ID of the workflow file
        ref:
    """

    path: str
    sha: str
    ref: str | None = None


@dataclass
class WorkflowRun(GitHubModel):
    """
    GitHub workflow run

    Attributes:
        artifacts_url: URL to created artifacts within the workflow run
        cancel_url: URL to cancel the workflow run
        check_suite_url: URL to the status checks
        created_at: Creation date of the workflow run
        event: Event that triggered the workflow run
        head_repository:
        head_sha:
        html_url: URL to the web page of the workflow run
        id: ID of the workflow run
        jobs_url: URL to the workflow run jobs
        logs_url: URL to the workflow run logs
        node_id: Node ID of the workflow run
        repository: Corresponding repository of the workflow run
        rerun_url: URL to rerun the workflow
        run_number: Number of the run
        updated_at: Last modification date
        url: URL to the workflow run
        workflow_id: ID of the corresponding workflow
        workflow_url: URL to the corresponding workflow
        actor: User that runs the workflow
        check_suite_id:
        check_suite_node_id:
        conclusion: Conclusion of the workflow run
        display_title: Displayed title of the workflow run
        head_branch:
        head_commit:
        head_repository_id:
        name: Name of the workflow
        path: Path to the workflow file
        previous_attempt_url: URL to the previous workflow run attempt
        pull_requests: List of pull requests
        referenced_workflows: List of references workflows
        run_attempt: Number of the run attempt
        run_started_at: Date the run started at
        status: Status of the workflow run
        triggering_actor: User who triggered the workflow run
    """

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
    actor: User | None = None
    check_suite_id: int | None = None
    check_suite_node_id: str | None = None
    conclusion: str | None = None
    display_title: str | None = None
    head_branch: str | None = None
    head_commit: WorkflowRunCommit | None = None
    head_repository_id: int | None = None
    name: str | None = None
    path: str | None = None
    previous_attempt_url: str | None = None
    pull_requests: list[dict] = field(default_factory=list)
    referenced_workflows: list[WorkflowRunWorkflow] = field(
        default_factory=list
    )
    run_attempt: int | None = None
    run_started_at: datetime | None = None
    status: WorkflowRunStatus | None = None
    triggering_actor: User | None = None
