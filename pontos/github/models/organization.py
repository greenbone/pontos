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

from pontos.github.models.base import GitHubModel, User

__all__ = (
    "GitIgnoreTemplate",
    "InvitationRole",
    "LicenseType",
    "MemberFilter",
    "MemberRole",
    "MergeCommitMessage",
    "MergeCommitTitle",
    "Organization",
    "Repository",
    "RepositoryType",
    "SecurityAndAnalysisStatus",
    "SquashMergeCommitMessage",
    "SquashMergeCommitTitle",
)


class MergeCommitTitle(Enum):
    PR_TITLE = "PR_TITLE"
    MERGE_MESSAGE = "MERGE_MESSAGE"


class MergeCommitMessage(Enum):
    PR_BODY = "PR_BODY"
    PR_TITLE = "PR_TITLE"
    BLANK = "BLANK"


class SquashMergeCommitTitle(Enum):
    PR_TITLE = "PR_TITLE"
    COMMIT_OR_PR_TITLE = "COMMIT_OR_PR_TITLE"


class SquashMergeCommitMessage(Enum):
    PR_BODY = "PR_BODY"
    COMMIT_MESSAGES = "COMMIT_MESSAGES"
    BLANK = "BLANK"


class RepositoryType(Enum):
    ALL = "all"
    PUBLIC = "public"
    PRIVATE = "private"
    FORKS = "forks"
    SOURCES = "sources"
    MEMBER = "member"
    INTERNAL = "internal"


@dataclass
class License(GitHubModel):
    key: str
    name: str
    node_id: str
    url: Optional[str] = None
    spdx_id: Optional[str] = None
    html_url: Optional[str] = None


@dataclass
class RepositoryPermissions(GitHubModel):
    admin: bool
    push: bool
    pull: bool
    maintain: Optional[bool] = None
    triage: Optional[bool] = None


@dataclass
class Organization(GitHubModel):
    avatar_url: str
    events_url: str
    followers_url: str
    following_url: str
    gists_url: str
    html_url: str
    id: int
    login: str
    node_id: str
    organizations_url: str
    received_events_url: str
    repos_url: str
    site_admin: bool
    starred_url: str
    subscriptions_url: str
    type: str
    url: str
    email: Optional[str] = None
    gravatar_id: Optional[str] = None
    name: Optional[str] = None
    starred_at: Optional[datetime] = None


@dataclass
class CodeOfConduct(GitHubModel):
    url: str
    key: str
    name: str
    html_url: str


class SecurityAndAnalysisStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


@dataclass
class SecurityAndAnalysisType(GitHubModel):
    status: SecurityAndAnalysisStatus


@dataclass
class SecurityAndAnalysis(GitHubModel):
    advanced_security: SecurityAndAnalysisType
    secret_scanning: SecurityAndAnalysisType
    secret_scanning_push_protection: SecurityAndAnalysisType


@dataclass
class Repository(GitHubModel):
    archive_url: str
    assignees_url: str
    blobs_url: str
    branches_url: str
    collaborators_url: str
    comments_url: str
    commits_url: str
    compare_url: str
    contents_url: str
    contributors_url: str
    deployments_url: str
    downloads_url: str
    events_url: str
    fork: bool
    forks_url: str
    full_name: str
    git_commits_url: str
    git_refs_url: str
    git_tags_url: str
    hooks_url: str
    html_url: str
    id: int
    issue_comment_url: str
    issue_events_url: str
    issues_url: str
    keys_url: str
    labels_url: str
    languages_url: str
    merges_url: str
    milestones_url: str
    name: str
    node_id: str
    notifications_url: str
    owner: User
    private: bool
    pulls_url: str
    releases_url: str
    stargazers_url: str
    statuses_url: str
    subscribers_url: str
    subscription_url: str
    tags_url: str
    teams_url: str
    trees_url: str
    url: str
    allow_auto_merge: Optional[bool] = None
    allow_forking: Optional[bool] = None
    allow_merge_commit: Optional[bool] = None
    allow_rebase_merge: Optional[bool] = None
    allow_squash_merge: Optional[bool] = None
    allow_update_branch: Optional[bool] = None
    anonymous_access_enabled: Optional[bool] = None
    archived: Optional[bool] = None
    clone_url: Optional[str] = None
    code_of_conduct: Optional[CodeOfConduct] = None
    created_at: Optional[datetime] = None
    default_branch: Optional[str] = None
    delete_branch_on_merge: Optional[bool] = None
    description: Optional[str] = None
    disabled: Optional[bool] = None
    forks_count: Optional[int] = None
    forks: Optional[int] = None
    git_url: Optional[str] = None
    has_discussions: Optional[bool] = None
    has_downloads: Optional[bool] = None
    has_issues: Optional[bool] = None
    has_pages: Optional[bool] = None
    has_projects: Optional[bool] = None
    has_wiki: Optional[bool] = None
    homepage: Optional[str] = None
    is_template: Optional[bool] = None
    language: Optional[str] = None
    license: Optional[License] = None
    merge_commit_title: Optional[MergeCommitTitle] = None
    merge_commit_message: Optional[MergeCommitMessage] = None
    mirror_url: Optional[str] = None
    network_count: Optional[int] = None
    open_issues_count: Optional[int] = None
    open_issues: Optional[int] = None
    organization: Optional[Organization] = None
    permissions: Optional[RepositoryPermissions] = None
    pushed_at: Optional[datetime] = None
    security_and_analysis: Optional[SecurityAndAnalysis] = None
    size: Optional[int] = None
    ssh_url: Optional[str] = None
    stargazers_count: Optional[int] = None
    subscribers_count: Optional[int] = None
    svn_url: Optional[str] = None
    squash_merge_commit_message: Optional[SquashMergeCommitMessage] = None
    squash_merge_commit_title: Optional[SquashMergeCommitTitle] = None
    temp_clone_token: Optional[str] = None
    topics: Optional[List[str]] = field(default_factory=list)
    updated_at: Optional[datetime] = None
    use_squash_pr_title_as_default: Optional[bool] = None
    visibility: Optional[str] = None
    watchers_count: Optional[int] = None
    watchers: Optional[int] = None
    web_commit_signoff_required: Optional[bool] = None


class MemberFilter(Enum):
    TWO_FA_DISABLED = "2fa_disabled"
    ALL = "all"


class MemberRole(Enum):
    ALL = "all"
    ADMIN = "admin"
    MEMBER = "member"


class InvitationRole(Enum):
    ADMIN = "admin"
    DIRECT_MEMBER = "direct_member"
    BILLING_MANAGER = "billing_manager"


class GitIgnoreTemplate(Enum):
    """
    Just a small part of the available gitignore templates at
    https://github.com/github/gitignore
    """

    C = "C"
    CPP = "C++"
    CMAKE = "CMake"
    GO = "Go"
    JAVA = "Java"
    MAVEN = "Maven"
    NODE = "Node"
    PYTHON = "Python"
    RUST = "Rust"


class LicenseType(Enum):
    ACADEMIC_FREE_LICENSE_3_0 = "afl-3.0"
    APACHE_LICENSE_2_0 = "apache-2.0"
    ARTISTIC_LICENSE_2_0 = "artistic-2.0"
    BOOST_SOFTWARE_LICENSE_1_0 = "bsl-1.0"
    BSD_2_CLAUSE_SIMPLIFIED_LICENSE = "bsd-2-clause"
    BSD_3_CLAUSE_NEW_OR_REVISED_LICENSE = "bsd-3-clause"
    BSD_3_CLAUSE_CLEAR_LICENSE = "bsd-3-clause-clear"
    CREATIVE_COMMONS_LICENSE_FAMILY = "cc"
    CREATIVE_COMMONS_ZERO_1_0_UNIVERSAL = "cc0-1.0"
    CREATIVE_COMMONS_ATTRIBUTION_4_0 = "cc-by-4.0"
    CREATIVE_COMMONS_ATTRIBUTION_SHARE_ALIKE_4_0 = "cc-by-sa-4.0"
    DO_WHAT_THE_F_CK_YOU_WANT_TO_PUBLIC_LICENSE = "wtfpl"
    EDUCATIONAL_COMMUNITY_LICENSE_2_0 = "ecl-2.0"
    ECLIPSE_PUBLIC_LICENSE_1_0 = "epl-1.0"
    ECLIPSE_PUBLIC_LICENSE_2_0 = "epl-2.0"
    EUROPEAN_UNION_PUBLIC_LICENSE_1_1 = "eupl-1.1"
    GNU_AFFERO_GENERAL_PUBLIC_LICENSE_3_0 = "agpl-3.0"
    GNU_GENERAL_PUBLIC_LICENSE_FAMILY = "gpl"
    GNU_GENERAL_PUBLIC_LICENSE_2_0 = "gpl-2.0"
    GNU_GENERAL_PUBLIC_LICENSE_3_0 = "gpl-3.0"
    GNU_LESSER_GENERAL_PUBLIC_LICENSE_FAMILY = "lgpl"
    GNU_LESSER_GENERAL_PUBLIC_LICENSE_2_1 = "lgpl-2.1"
    GNU_LESSER_GENERAL_PUBLIC_LICENSE_3_0 = "lgpl-3.0"
    ISC = "isc"
    LATEX_PROJECT_PUBLIC_LICENSE_1_3C_L = "ppl-1.3c"
    MICROSOFT_PUBLIC_LICENSE = "ms-pl"
    MIT = "mit"
    MOZILLA_PUBLIC_LICENSE_2_0 = "mpl-2.0"
    OPEN_SOFTWARE_LICENSE_3_0 = "osl-3.0"
    POSTGRESQL_LICENSE = "postgresql"
    SIL_OPEN_FONT_LICENSE_1_1 = "ofl-1.1"
    UNIVERSITY_OF_ILLINOIS_NCSA_OPEN_SOURCE_LICENSE = "ncsa"
    THE_UNLICENSE = "unlicense"
    ZLIB_LICENSE = "zlib"
