# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from dataclasses import dataclass
from typing import List, Optional

from pontos.github.models.base import App, GitHubModel, Team, User

__all__ = (
    "BranchProtection",
    "BranchProtectionFeature",
    "BypassPullRequestAllowances",
    "DismissalRestrictions",
    "Restrictions",
    "RequiredStatusChecks",
    "StatusCheck",
    "RequiredPullRequestReviews",
    "RequiredStatusChecks",
    "BypassPullRequestAllowances",
    "DismissalRestrictions",
)


@dataclass
class DismissalRestrictions(GitHubModel):
    """
    Settings to only allow specific users, teams and apps to dismiss pull
    request reviews

    Attributes:
        url: URL to the dismissal restrictions
        users_url: URL to the users of the dismissal restrictions
        teams_url: URL to the teams of the dismissal restrictions
        users: List of user allowed to dismiss pull request reviews
        teams: List of teams allowed to dismiss pull request reviews
        apps: List of apps allowed to dismiss pull request reviews
    """

    url: str
    users_url: str
    teams_url: str
    users: List[User]
    teams: List[Team]
    apps: List[App]


@dataclass
class BypassPullRequestAllowances(GitHubModel):
    """
    Settings to allow users, teams and apps to bypass pull request reviews

    Attributes:
        user: List of user allowed to bypass required pull request reviews
        teams: List of teams allowed to bypass required pull request reviews
        apps: List of apps allowed to bypass required pull request reviews
    """

    users: List[User]
    teams: List[Team]
    apps: List[App]


@dataclass
class RequiredPullRequestReviews(GitHubModel):
    """
    Requires pull request review settings of a branch protection

    Attributes:
        url: URL to the required pull request reviews
        dismiss_stale_reviews: Dismiss stale reviews
        require_code_owner_reviews: Require reviews by code owners
        required_approving_review_count: Number of approvals required
        require_last_push_approval: Require to approve the last push
        dismissal_restrictions: Restrictions for who can dismiss pull request
            reviews
        bypass_pull_request_allowances: Settings for allowing bypassing the
            required pull request reviews
    """

    url: str
    dismiss_stale_reviews: bool
    require_code_owner_reviews: bool
    required_approving_review_count: int
    require_last_push_approval: bool
    dismissal_restrictions: Optional[DismissalRestrictions] = None
    bypass_pull_request_allowances: Optional[BypassPullRequestAllowances] = None


@dataclass
class StatusCheck(GitHubModel):
    """
    Status check

    Attributes:
        context:
        app: App ID as the source of the status check
    """

    context: str
    app_id: Optional[int] = None


@dataclass
class RequiredStatusChecks(GitHubModel):
    """
    Required status checks settings of a branch protection

    Attributes:
        url: URL to the required status checks
        strict: True to require status checks to pass before merging
        checks: List of status checks
        enforcement_level: Enforcement level of the required status checks
    """

    url: str
    strict: bool
    checks: List[StatusCheck]
    enforcement_level: Optional[str] = None


@dataclass
class Restrictions(GitHubModel):
    """
    Branch protection push restrictions

    Attributes:
        url: URL to the restrictions
        users_url: URL to the users of the restrictions
        teams_url: URL to the teams of the restrictions
        apps_url: URL to the apps of the restrictions
        users: List of restricted users
        teams: List of restricted teams
        apps: List of restricted apps
    """

    url: str
    users_url: str
    teams_url: str
    apps_url: str
    users: List[User]
    teams: List[Team]
    apps: List[App]


@dataclass
class BranchProtectionFeature(GitHubModel):
    """
    GitHub branch protection feature setting

    Attributes:
        enable: True if the feature is enabled
        url: REST API URL to change the feature
    """

    enabled: bool
    url: Optional[str] = None


@dataclass
class BranchProtection(GitHubModel):
    """
    GitHub branch protection information

    Attributes:
        url: URL to the branch protection rules
        required_status_checks: Required status check for the matching branches
        required_pull_request_reviews: Required pull request reviews for the
            matching branches.
        restrictions: Restrictions who can push to the matching branches.
        enforce_admins: Enforce the rules also for user in a admin role.
        required_linear_history: Require a linear history before merging.
            Restricts merging if the matching branch is out of date.
        allow_force_pushes: Allow force pushes to the matching branches.
        allow_deletions: Allow to delete the matching branches.
        block_creations: Restrict pushes that create matching branches.
        required_conversation_resolution: Require conversation resolution before
            merging.
        lock_branch: Mark matching branches as read-only. Users cannot push to
            matching branches.
        allow_fork_syncing: Whether users can pull changes from upstream when
            the matching branch is locked.
        required_signatures: Require git commit signatures.
    """

    url: str
    required_status_checks: Optional[RequiredStatusChecks] = None
    required_pull_request_reviews: Optional[RequiredPullRequestReviews] = None
    restrictions: Optional[Restrictions] = None
    enforce_admins: Optional[BranchProtectionFeature] = None
    required_linear_history: Optional[BranchProtectionFeature] = None
    allow_force_pushes: Optional[BranchProtectionFeature] = None
    allow_deletions: Optional[BranchProtectionFeature] = None
    block_creations: Optional[BranchProtectionFeature] = None
    required_conversation_resolution: Optional[BranchProtectionFeature] = None
    lock_branch: Optional[BranchProtectionFeature] = None
    allow_fork_syncing: Optional[BranchProtectionFeature] = None
    required_signatures: Optional[BranchProtectionFeature] = None
