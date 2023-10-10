# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from pontos.github.models.base import GitHubModel, User
from pontos.github.models.organization import Repository


class AlertState(Enum):
    """
    State of a code scanning alert
    """

    OPEN = "open"
    DISMISSED = "dismissed"
    FIXED = "fixed"


class AlertSort(Enum):
    """
    The property by which to sort the alerts
    """

    CREATED = "created"
    UPDATED = "updated"


class DismissedReason(Enum):
    """
    The reason for dismissing or closing the alert
    """

    FALSE_POSITIVE = "false positive"
    WONT_FIX = "won't fix"
    USED_IN_TESTS = "used in tests"


class Severity(Enum):
    """
    The severity of the alert
    """

    NONE = "none"
    NOTE = "note"
    WARNING = "warning"
    ERROR = "error"


class SecuritySeverityLevel(Enum):
    """
    The security severity of the alert
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Classification(Enum):
    """
    A classification of the file. For example to identify it as generated
    """

    SOURCE = "source"
    GENERATED = "generated"
    TEST = "test"
    LIBRARY = "library"


@dataclass
class Rule(GitHubModel):
    """
    A rule used to detect the alert

    Attributes:
        id: A unique identifier for the rule used to detect the alert
        name: The name of the rule used to detect the alert
        severity: The severity of the alert
        security_severity_level: The security severity of the alert
        description: A short description of the rule used to detect the alert
        full_description: description of the rule used to detect the alert
        tags: A set of tags applicable for the rule
        help: Detailed documentation for the rule as GitHub Flavored Markdown
        help_uri: A link to the documentation for the rule used to detect the
            alert
    """

    name: str
    description: str
    id: Optional[str] = None
    full_description: Optional[str] = None
    severity: Optional[Severity] = None
    security_severity_level: Optional[SecuritySeverityLevel] = None
    tags: Optional[list[str]] = None
    help: Optional[str] = None
    help_uri: Optional[str] = None


@dataclass
class Message(GitHubModel):
    """
    Attributes:
        text:
    """

    text: str


@dataclass
class Location(GitHubModel):
    """
    Describes a region within a file for the alert

    Attributes:
        path: The file path in the repository
        start_line: Line number at which the vulnerable code starts in the file
        end_line: Line number at which the vulnerable code ends in the file
        start_column: The column at which the vulnerable code starts within the
            start line
        end_column: The column at which the vulnerable code ends within the end
            line
    """

    path: str
    start_line: int
    end_line: int
    start_column: int
    end_column: int


@dataclass
class Instance(GitHubModel):
    """
    Attributes:
        ref: The full Git reference, formatted as `refs/heads/<branch name>`,
            `refs/pull/<number>/merge`, or `refs/pull/<number>/head`
        analysis_key: Identifies the configuration under which the analysis was
            executed. For example, in GitHub Actions this includes the workflow
            filename and job name
        environment: Identifies the variable values associated with the
            environment in which the analysis that generated this alert instance
            was performed, such as the language that was analyzed
        category: Identifies the configuration under which the analysis was
            executed. Used to distinguish between multiple analyses for the same
            tool and commit, but performed on different languages or different
            parts of the code
        state: State of a code scanning alert
        commit_sha:
        message:
        location: Describes a region within a file for the alert
        html_url:
        classifications: Classifications that have been applied to the file that
            triggered the alert. For example identifying it as documentation, or
            a generated file
    """

    ref: str
    analysis_key: str
    environment: str
    category: str
    state: AlertState
    commit_sha: str
    message: Message
    location: Location
    html_url: Optional[str] = None
    classifications: Optional[list[Classification]] = None


@dataclass
class Tool(GitHubModel):
    """
    A tool used to generate the code scanning analysis

    Attributes:
        name: The name of the tool used to generate the code scanning analysis
        version: The version of the tool used to generate the code scanning
            analysis
        guid: he GUID of the tool used to generate the code scanning analysis,
            if provided in the uploaded SARIF data
    """

    name: str
    version: Optional[str] = None
    guid: Optional[str] = None


@dataclass
class CodeScanningAlert(GitHubModel):
    """
    A GitHub Code Scanning Alert

    Attributes:
        number: The security alert number
        created_at: The time that the alert was created
        updated_at: The time that the alert was last updated
        url: The REST API URL of the alert resource
        html_url: The GitHub URL of the alert resource
        instances_url: The REST API URL for fetching the list of instances for
            an alert
        state: State of a code scanning alert
        fixed_at: The time that the alert was no longer detected and was
            considered fixed
        dismissed_by: A GitHub user who dismissed the alert
        dismissed_at: The time that the alert was dismissed
        dismissed_reason: The reason for dismissing or closing the alert
        dismissed_comment: The dismissal comment associated with the dismissal
            of the alert
        rule: The rule used to detect the alert
        tool: The tool used to generate the code scanning analysis
        most_recent_instance:
        repository: A GitHub repository
    """

    number: int
    created_at: datetime
    url: str
    html_url: str
    instances_url: str
    state: AlertState
    rule: Rule
    tool: Tool
    most_recent_instance: Instance
    repository: Optional[Repository] = None
    updated_at: Optional[datetime] = None
    fixed_at: Optional[datetime] = None
    dismissed_by: Optional[User] = None
    dismissed_at: Optional[datetime] = None
    dismissed_reason: Optional[DismissedReason] = None
    dismissed_comment: Optional[str] = None
