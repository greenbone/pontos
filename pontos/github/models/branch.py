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

from pontos.github.models.base import App, GitHubModel, Team, User

__all__ = ("BranchProtection",)


@dataclass
class DismissalRestrictions(GitHubModel):
    url: str
    users_url: str
    teams_url: str
    users: List[User]
    teams: List[Team]
    apps: List[App]


@dataclass
class BypassPullRequestAllowances(GitHubModel):
    users: List[User]
    teams: List[Team]
    apps: List[App]


@dataclass
class RequiredPullRequestReviews(GitHubModel):
    url: str
    dismiss_stale_reviews: bool
    require_code_owner_reviews: bool
    required_approving_review_count: int
    require_last_push_approval: bool
    dismissal_restrictions: Optional[DismissalRestrictions] = None
    bypass_pull_request_allowances: Optional[BypassPullRequestAllowances] = None


@dataclass
class StatusCheck(GitHubModel):
    context: str
    app_id: Optional[int] = None


@dataclass
class RequiredStatusChecks(GitHubModel):
    url: str
    strict: bool
    checks: List[StatusCheck]
    enforcement_level: Optional[str] = None


@dataclass
class Restrictions(GitHubModel):
    url: str
    users_url: str
    teams_url: str
    apps_url: str
    users: List[User]
    teams: List[Team]
    apps: List[App]


@dataclass
class BranchProtectionFeature(GitHubModel):
    enabled: bool
    url: Optional[str] = None


@dataclass
class BranchProtection(GitHubModel):
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
