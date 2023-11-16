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

from dataclasses import dataclass
from typing import List, Optional

from pontos.models import Model, StrEnum

__all__ = (
    "App",
    "Event",
    "FileStatus",
    "GitHubModel",
    "Permission",
    "SortOrder",
    "Team",
    "TeamPrivacy",
    "TeamRole",
    "User",
)


class FileStatus(StrEnum):
    """
    File status

    Attributes:
        ADDED: File is added
        DELETED: File is deleted
        MODIFIED: File is modified
        RENAMED: File is renamed
        COPIED: File is copied
        CHANGED: File is changed
        UNCHANGED: File is unchanged
    """

    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"
    RENAMED = "renamed"
    COPIED = "copied"
    CHANGED = "changed"
    UNCHANGED = "unchanged"


@dataclass(init=False)
class GitHubModel(Model):
    """
    Base class for all GitHub models
    """


@dataclass
class User(GitHubModel):
    """
    A GitHub user model

    Attributes:
        login: The user login name
        id: The user ID
        node_id: The user node ID
        avatar_url: URL to the avatar image
        gravatar_url: URL to the gravatar avatar image
        html_url: URL to the users public profile
        followers_url: URL to the followers
        following_url: URL to users that the user if following
        gists_url: URL to the user's gists
        starred_url: URL to the starred repositories of the user
        subscriptions_url: URL to the subscriptions
        organizations_url: URL to the user's organizations
        repos_url: URL to the user's repositories
        events_url: URL to the events
        received_events_url: URL to the received events
        type: The user's type
        site_admin: True if the user is a site admin
    """

    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool


class TeamPrivacy(StrEnum):
    """
    Team privacy

    Attributes:
        SECRET: A secret team
        CLOSED: A closed team
    """

    SECRET = "secret"
    CLOSED = "closed"


class TeamRole(StrEnum):
    """
    A user's role withing a team


    Attributes:
        MEMBER: The user is a "normal" member
        MAINTAINER: The user is an admin of the team
    """

    MEMBER = "member"
    MAINTAINER = "maintainer"


class Permission(StrEnum):
    # pylint: disable=line-too-long
    """
    Permissions on a repository/project at GitHub

    https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/repository-roles-for-an-organization

    Attributes:
        PULL: Read permissions
        PUSH: Write permissions
        TRIAGE: Triage permissions
        MAINTAIN: Maintainer permissions
        ADMIN: Admin permissions (full access to the project)
    """

    PULL = "pull"
    PUSH = "push"
    TRIAGE = "triage"
    MAINTAIN = "maintain"
    ADMIN = "admin"


@dataclass
class Team(GitHubModel):
    """
    A GitHub Team model

    Attributes:
        id: ID of the team
        node_id: Node ID of the team
        url: REST API URL for the team
        html_url: Web URL for the team
        name: Name of the team
        slug: Slug of the team name
        description: Description of the team
        privacy: Privacy scope of the team
        permission: Permissions of the teams
        members_url: REST API URL to the members of the team
        repositories_url: REST API URL to the repositories of the team
        parent: An optional parent team
    """

    id: int
    node_id: str
    url: str
    html_url: str
    name: str
    slug: str
    description: str
    privacy: TeamPrivacy
    permission: Permission
    members_url: str
    repositories_url: str
    parent: Optional["Team"] = None


@dataclass
class App(GitHubModel):
    """
    GitHub app

    Attributes:
        id: ID of the app
        slug: Name slug of the app
        node_id: Node ID of the app
        owner: Owner (user) of the app
        name: Name of the app
        description: Description of the app
        external_url: External URL
        html_url: URL to the web page of the app
        created_at: Creation date
        updated_at: Last modification date
        events: List of events
    """

    id: int
    slug: str
    node_id: str
    owner: User
    name: str
    description: str
    external_url: str
    html_url: str
    created_at: str
    updated_at: str
    events: List[str]


class Event(StrEnum):
    """
    A GitHub event type

    https://docs.github.com/de/actions/using-workflows/events-that-trigger-workflows

    Attributes:
        BRANCH_PROTECTION_RULE:
        CHECK_RUN:
        CHECK_SUITE:
        CREATE:
        DELETE:
        DEPLOYMENT:
        DEPLOYMENT_STATUS:
        DISCUSSION:
        DISCUSSION_COMMENT:
        FORK:
        GOLLUM:
        ISSUE_COMMENT:
        ISSUES:
        LABEL:
        MERGE_GROUP:
        MILESTONE:
        PAGE_BUILD:
        PROJECT:
        PROJECT_CARD:
        PROJECT_COLUMN:
        PUBLIC:
        PULL_REQUEST:
        PULL_REQUEST_COMMENT:
        PULL_REQUEST_REVIEW:
        PULL_REQUEST_REVIEW_COMMENT:
        PULL_REQUEST_TARGET:
        PUSH:
        REGISTRY_PACKAGE:
        RELEASE:
        REPOSITORY_DISPATCH:
        SCHEDULE:
        STATUS:
        WATCH:
        WORKFLOW_CALL:
        WORKFLOW_DISPATCH:
        WORKFLOW_RUN:
    """

    BRANCH_PROTECTION_RULE = "branch_protection_rule"
    CHECK_RUN = "check_run"
    CHECK_SUITE = "check_suite"
    CREATE = "create"
    DELETE = "delete"
    DEPLOYMENT = "deployment"
    DEPLOYMENT_STATUS = "deployment_status"
    DISCUSSION = "discussion"
    DISCUSSION_COMMENT = "discussion_comment"
    DYNAMIC = "dynamic"
    FORK = "fork"
    GOLLUM = "gollum"
    ISSUE_COMMENT = "issue_comment"
    ISSUES = "issues"
    LABEL = "label"
    MERGE_GROUP = "merge_group"
    MILESTONE = "milestone"
    PAGE_BUILD = "page_build"
    PROJECT = "project"
    PROJECT_CARD = "project_card"
    PROJECT_COLUMN = "project_column"
    PUBLIC = "public"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_COMMENT = "pull_request_comment"
    PULL_REQUEST_REVIEW = "pull_request_review"
    PULL_REQUEST_REVIEW_COMMENT = "pull_request_review_comment"
    PULL_REQUEST_TARGET = "pull_request_target"
    PUSH = "push"
    REGISTRY_PACKAGE = "registry_package"
    RELEASE = "release"
    REPOSITORY_DISPATCH = "repository_dispatch"
    SCHEDULE = "schedule"
    STATUS = "status"
    WATCH = "watch"
    WORKFLOW_CALL = "workflow_call"
    WORKFLOW_DISPATCH = "workflow_dispatch"
    WORKFLOW_RUN = "workflow_run"


class SortOrder(StrEnum):
    """
    Sort order: asc or desc

    Attributes:
        ASC: Use ascending sort order
        DESC: Use descending sort order
    """

    ASC = "asc"
    DESC = "desc"
