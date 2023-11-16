# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from pontos.github.models.base import GitHubModel, User
from pontos.github.models.organization import Repository
from pontos.models import StrEnum


class AlertSort(StrEnum):
    """
    The property by which to sort the alerts
    """

    CREATED = "created"
    UPDATED = "updated"


class AlertState(StrEnum):
    """
    State of the GitHub Secrets Scanning Alert
    """

    OPEN = "open"
    RESOLVED = "resolved"


class Resolution(StrEnum):
    """
    The reason for resolving the alert
    """

    FALSE_POSITIVE = "false_positive"
    WONT_FIX = "wont_fix"
    REVOKED = "revoked"
    USED_IN_TESTS = "used_in_tests"


class LocationType(StrEnum):
    """
    Type of location
    """

    COMMIT = "commit"
    ISSUE_TITLE = "issue_title"
    ISSUE_BODY = "issue_body"
    ISSUE_COMMENT = "issue_comment"


@dataclass
class SecretScanningAlert(GitHubModel):
    """
    A GitHub Secret Scanning Alert

    Attributes:
        number: The security alert number
        url: The REST API URL of the alert resource
        html_url: The GitHub URL of the alert resource
        locations_url: The REST API URL of the code locations for this alert
        state: Sets the state of the secret scanning alert. A `resolution` must
            be provided when the state is set to `resolved`.
        created_at: The time that the alert was created
        updated_at: The time that the alert was last updated
        resolution: Required when the `state` is `resolved`
        resolved_at: The time that the alert was resolved
        resolved_by: A GitHub user who resolved the alert
        secret_type: The type of secret that secret scanning detected
        secret_type_display_name: User-friendly name for the detected secret
        secret: The secret that was detected
        repository: The GitHub repository containing the alert. It's not
            returned when requesting a specific alert
        push_protection_bypassed: Whether push protection was bypassed for the
            detected secret
        push_protection_bypassed_by: A GitHub user who bypassed the push
            protection
        push_protection_bypassed_at: The time that push protection was bypassed
        resolution_comment: The comment that was optionally added when this
            alert was closed
    """

    number: int
    url: str
    html_url: str
    locations_url: str
    state: AlertState
    secret_type: str
    secret_type_display_name: str
    secret: str
    created_at: datetime
    repository: Optional[Repository] = None
    updated_at: Optional[datetime] = None
    resolution: Optional[Resolution] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[User] = None
    push_protection_bypassed: Optional[bool] = None
    push_protection_bypassed_by: Optional[User] = None
    push_protection_bypassed_at: Optional[datetime] = None
    resolution_comment: Optional[str] = None


@dataclass
class CommitLocation(GitHubModel):
    """
    Represents a 'commit' secret scanning location type

    Attributes:
        path: The file path in the repository
        start_line: Line number at which the secret starts in the file
        end_line: Line number at which the secret ends in the file
        start_column: The column at which the secret starts within the start
            line
        end_column: The column at which the secret ends within the end line
        blob_sha: SHA-1 hash ID of the associated blob
        blob_url: The API URL to get the associated blob resource
        commit_sha: SHA-1 hash ID of the associated commit
        commit_url: The API URL to get the associated commit resource
    """

    path: str
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    blob_sha: str
    blob_url: str
    commit_sha: str
    commit_url: str


@dataclass
class IssueTitleLocation(GitHubModel):
    """
    Represents an 'issue_title' secret scanning location type

    Attributes:
        issue_title_url: The API URL to get the issue where the secret was
            detected
    """

    issue_title_url: str


@dataclass
class IssueBodyLocation(GitHubModel):
    """
    Represents an 'issue_body' secret scanning location type

    Attributes:
        issue_body_url: The API URL to get the issue where the secret was
            detected
    """

    issue_body_url: str


@dataclass
class IssueCommentLocation(GitHubModel):
    """
    Represents an 'issue_comment' secret scanning location type

    Attributes:
        issue_comment_url: he API URL to get the issue comment where the secret
            was detected
    """

    issue_comment_url: str


@dataclass
class AlertLocation(GitHubModel):
    """
    Location where the secret was detected

    Attributes:
        type: The location type
        details: Details about the location where the secret was detected
    """

    type: LocationType
    details: Union[
        CommitLocation,
        IssueTitleLocation,
        IssueBodyLocation,
        IssueCommentLocation,
    ]
