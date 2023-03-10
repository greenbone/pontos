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

from pontos.github.models.base import GitHubModel, User

__all__ = (
    "CodeOfConduct",
    "GitIgnoreTemplate",
    "InvitationRole",
    "License",
    "LicenseType",
    "MemberFilter",
    "MemberRole",
    "MergeCommitMessage",
    "MergeCommitTitle",
    "Organization",
    "Repository",
    "RepositoryPermissions",
    "RepositoryType",
    "SecurityAndAnalysis",
    "SecurityAndAnalysisStatus",
    "SecurityAndAnalysisType",
    "SquashMergeCommitMessage",
    "SquashMergeCommitTitle",
)


class MergeCommitTitle(Enum):
    """
    Merge commit title

    Attributes:
        PR_TITLE: Use pull request title
        MERGE_MESSAGE: Use provided merge commit message
    """

    PR_TITLE = "PR_TITLE"
    MERGE_MESSAGE = "MERGE_MESSAGE"


class MergeCommitMessage(Enum):
    """
    Merge commit message setting

    Attributes:
        PR_BODY: Use pull request body
        PR_TITLE: Use pull request title
        BLANK: Leave it blank
    """

    PR_BODY = "PR_BODY"
    PR_TITLE = "PR_TITLE"
    BLANK = "BLANK"


class SquashMergeCommitTitle(Enum):
    """
    Squash merge commit title

    Attributes:
        PR_TITLE: Use pull request title
        COMMIT_OR_PR_TITLE: Use pull request or commit title
    """

    PR_TITLE = "PR_TITLE"
    COMMIT_OR_PR_TITLE = "COMMIT_OR_PR_TITLE"


class SquashMergeCommitMessage(Enum):
    """
    Squash merge commit message setting

    Attributes:
        PR_BODY: Use pull request body
        COMMIT_MESSAGES: Use commit messages
        BLANK: Leave it blank
    """

    PR_BODY = "PR_BODY"
    COMMIT_MESSAGES = "COMMIT_MESSAGES"
    BLANK = "BLANK"


class RepositoryType(Enum):
    """
    A repository type

    Attributes:
        ALL: All repository types
        PUBLIC: Public repository
        PRIVATE: Private repository
        FORKS: Forked repository
        SOURCES:
        MEMBER:
        INTERNAL:
    """

    ALL = "all"
    PUBLIC = "public"
    PRIVATE = "private"
    FORKS = "forks"
    SOURCES = "sources"
    MEMBER = "member"
    INTERNAL = "internal"


@dataclass
class License(GitHubModel):
    """
    Software License

    Attributes:
        key: Key of the license
        name: Name of the license
        node_id: Node ID of the license
        url: URL to the license
        spdx_id: SPDX ID of the license
        html_url: URL to the web page of the license
    """

    key: str
    name: str
    node_id: str
    url: Optional[str] = None
    spdx_id: Optional[str] = None
    html_url: Optional[str] = None


@dataclass
class RepositoryPermissions(GitHubModel):
    """
    GitHub repository permissions

    Attributes:
        admin:
        push:
        pull:
        maintain:
        triage:
    """

    admin: bool
    push: bool
    pull: bool
    maintain: Optional[bool] = None
    triage: Optional[bool] = None


@dataclass
class Organization(GitHubModel):
    """
    A GitHub organization

    Attributes:
        avatar_url: URL to the avatar image
        events_url: URL to the events
        followers_url: URL to the followers
        following_url: URL to users which the organization is following
        gists_url: URL to gists of the organization
        html_url: URL to the web page of the organization
        id: ID of the organization
        login: Login name of the organization
        node_id: Node ID of the organization
        organizations_url: URL to the organization
        received_events_url: URL to the received events
        repos_url: URL to the list of repositories
        site_admin:
        starred_url: URL to the list of starring users
        subscriptions_url:
        type: Type of the organization
        url: URL to the organization
        email: Email address
        gravatar_id: ID of the connected gravatar account
        name: Name of the organization
        starred_at:
    """

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
    """
    Code of Conduct

    Attributes:
        url: URL to the code of conduct
        key: Key of the code of conduct
        name: Name of the code of conduct
        html_url: URL to the web page of the code of conduct
    """

    url: str
    key: str
    name: str
    html_url: str


class SecurityAndAnalysisStatus(Enum):
    """
    Security and analysis status

    Attributes:
        ENABLED: enabled
        DISABLED: disabled
    """

    ENABLED = "enabled"
    DISABLED = "disabled"


@dataclass
class SecurityAndAnalysisType(GitHubModel):
    """
    Security and analysis type

    Attributes:
        status:
    """

    status: SecurityAndAnalysisStatus


@dataclass
class SecurityAndAnalysis(GitHubModel):
    """
    Security and analysis

    Attributes:
        advanced_security: Status of GitHub Advanced Security is used
        secret_scanning: Status of Secret Scanning is used
        secret_scanning_push_protection: Status of Secret Scanning Push
            Protection is used
    """

    advanced_security: SecurityAndAnalysisType
    secret_scanning: SecurityAndAnalysisType
    secret_scanning_push_protection: SecurityAndAnalysisType


@dataclass
class Repository(GitHubModel):
    """
    A GitHub repository model

    Attributes:
        archive_url:
        assignees_url:
        blobs_url:
        branches_url:
        collaborators_url:
        comments_url:
        commits_url:
        compare_url:
        contents_url:
        contributors_url:
        deployments_url:
        downloads_url:
        events_url:
        fork:
        forks_url:
        full_name:
        git_commits_url:
        git_refs_url:
        git_tags_url:
        hooks_url:
        html_url:
        id:
        issue_comment_url:
        issue_events_url:
        issues_url:
        keys_url:
        labels_url:
        languages_url:
        merges_url:
        milestones_url:
        name:
        node_id:
        notifications_url:
        owner:
        private:
        pulls_url:
        releases_url:
        stargazers_url:
        statuses_url:
        subscribers_url:
        subscription_url:
        tags_url:
        teams_url:
        trees_url:
        url:
        allow_auto_merge:
        allow_forking:
        allow_merge_commit:
        allow_rebase_merge:
        allow_squash_merge:
        allow_update_branch:
        anonymous_access_enabled:
        archived:
        clone_url:
        code_of_conduct:
        created_at:
        default_branch:
        delete_branch_on_merge:
        description:
        disabled:
        forks_count:
        forks:
        git_url:
        has_discussions:
        has_downloads:
        has_issues:
        has_pages:
        has_projects:
        has_wiki:
        homepage:
        is_template:
        language:
        license:
        merge_commit_title:
        merge_commit_message:
        mirror_url:
        network_count:
        open_issues_count:
        open_issues:
        organization:
        permissions:
        pushed_at:
        security_and_analysis:
        size:
        ssh_url:
        stargazers_count:
        subscribers_count:
        svn_url:
        squash_merge_commit_message:
        squash_merge_commit_title:
        temp_clone_token:
        topics:
        updated_at: Last modification date
        use_squash_pr_title_as_default:
        visibility:
        watchers_count:
        watchers:
        web_commit_signoff_required:
    """

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
    topics: Optional[List[str]] = field(default_factory=list[str])
    updated_at: Optional[datetime] = None
    use_squash_pr_title_as_default: Optional[bool] = None
    visibility: Optional[str] = None
    watchers_count: Optional[int] = None
    watchers: Optional[int] = None
    web_commit_signoff_required: Optional[bool] = None


class MemberFilter(Enum):
    """
    A member filter

    Attributes:
        TWO_FA_DISABLED: Members with 2 factor authentication disabled
        ALL: All members
    """

    TWO_FA_DISABLED = "2fa_disabled"
    ALL = "all"


class MemberRole(Enum):
    """
    A member role

    Attributes:
        ALL: All roles
        ADMIN: Admin only
        MEMBER: Member only
    """

    ALL = "all"
    ADMIN = "admin"
    MEMBER = "member"


class InvitationRole(Enum):
    """
    A invitation role

    Attributes:
        ADMIN: Admin only
        DIRECT_MEMBER: Direct member only
        BILLING_MANAGER: Billing manager only

    """

    ADMIN = "admin"
    DIRECT_MEMBER = "direct_member"
    BILLING_MANAGER = "billing_manager"


class GitIgnoreTemplate(Enum):
    """
    Just a small part of the available gitignore templates at
    https://github.com/github/gitignore

    Attributes:
        C: Template for C
        CPP: Template for C++
        CMAKE: Template for CMake
        GO: Template for Golang
        JAVA: Template for Java
        MAVEN: Template for maven
        NODE: Template for Nodejs
        PYTHON: Template for Python
        RUST: Template for Rust
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
    """
    License Type

    Attributes:
        ACADEMIC_FREE_LICENSE_3_0: afl-3.0
        APACHE_LICENSE_2_0: apache-2.0
        ARTISTIC_LICENSE_2_0: artistic-2.0
        BOOST_SOFTWARE_LICENSE_1_0: bsl-1.0
        BSD_2_CLAUSE_SIMPLIFIED_LICENSE: bsd-2-clause
        BSD_3_CLAUSE_NEW_OR_REVISED_LICENSE: bsd-3-clause
        BSD_3_CLAUSE_CLEAR_LICENSE: bsd-3-clause-clear
        CREATIVE_COMMONS_LICENSE_FAMILY: cc
        CREATIVE_COMMONS_ZERO_1_0_UNIVERSAL: cc0-1.0
        CREATIVE_COMMONS_ATTRIBUTION_4_0: cc-by-4.0
        CREATIVE_COMMONS_ATTRIBUTION_SHARE_ALIKE_4_0: cc-by-sa-4.0
        DO_WHAT_THE_F_CK_YOU_WANT_TO_PUBLIC_LICENSE: wtfpl
        EDUCATIONAL_COMMUNITY_LICENSE_2_0: ecl-2.0
        ECLIPSE_PUBLIC_LICENSE_1_0: epl-1.0
        ECLIPSE_PUBLIC_LICENSE_2_0: epl-2.0
        EUROPEAN_UNION_PUBLIC_LICENSE_1_1: eupl-1.1
        GNU_AFFERO_GENERAL_PUBLIC_LICENSE_3_0: agpl-3.0
        GNU_GENERAL_PUBLIC_LICENSE_FAMILY: gpl
        GNU_GENERAL_PUBLIC_LICENSE_2_0: gpl-2.0
        GNU_GENERAL_PUBLIC_LICENSE_3_0: gpl-3.0
        GNU_LESSER_GENERAL_PUBLIC_LICENSE_FAMILY: lgpl
        GNU_LESSER_GENERAL_PUBLIC_LICENSE_2_1: lgpl-2.1
        GNU_LESSER_GENERAL_PUBLIC_LICENSE_3_0: lgpl-3.0
        ISC: isc
        LATEX_PROJECT_PUBLIC_LICENSE_1_3C_L: ppl-1.3c
        MICROSOFT_PUBLIC_LICENSE: ms-pl
        MIT: mit
        MOZILLA_PUBLIC_LICENSE_2_0: mpl-2.0
        OPEN_SOFTWARE_LICENSE_3_0: osl-3.0
        POSTGRESQL_LICENSE: postgresql
        SIL_OPEN_FONT_LICENSE_1_1: ofl-1.1
        UNIVERSITY_OF_ILLINOIS_NCSA_OPEN_SOURCE_LICENSE: ncsa
        THE_UNLICENSE: unlicense
        ZLIB_LICENSE: zlib
    """

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
