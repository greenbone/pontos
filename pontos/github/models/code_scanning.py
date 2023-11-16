# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pontos.github.models.base import GitHubModel, User
from pontos.github.models.organization import Repository
from pontos.models import StrEnum


class AlertState(StrEnum):
    """
    State of a code scanning alert
    """

    OPEN = "open"
    DISMISSED = "dismissed"
    FIXED = "fixed"


class AlertSort(StrEnum):
    """
    The property by which to sort the alerts
    """

    CREATED = "created"
    UPDATED = "updated"


class DismissedReason(StrEnum):
    """
    The reason for dismissing or closing the alert
    """

    FALSE_POSITIVE = "false positive"
    WONT_FIX = "won't fix"
    USED_IN_TESTS = "used in tests"


class Severity(StrEnum):
    """
    The severity of the alert
    """

    NONE = "none"
    NOTE = "note"
    WARNING = "warning"
    ERROR = "error"


class SecuritySeverityLevel(StrEnum):
    """
    The security severity of the alert
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Classification(StrEnum):
    """
    A classification of the file. For example to identify it as generated
    """

    SOURCE = "source"
    GENERATED = "generated"
    TEST = "test"
    LIBRARY = "library"
    DOCUMENTATION = "documentation"


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


@dataclass
class Analysis(GitHubModel):
    """
    Details for a code scanning analyses

    Attributes:
        ref: The full Git reference, formatted as `refs/heads/<branch name>`,
            `refs/pull/<number>/merge`, or `refs/pull/<number>/head`
        commit_sha: The SHA of the commit to which the analysis you are
            uploading relates
        analysis_key: Identifies the configuration under which the analysis was
            executed. For example, in GitHub Actions this includes the workflow
            filename and job name
        environment: Identifies the variable values associated with the
            environment in which this analysis was performed
        category: Identifies the configuration under which the analysis was
            executed. Used to distinguish between multiple analyses for the same
            tool and commit, but performed on different languages or different
            parts of the code
        error: Error generated when processing the analysis
        created_at: The time that the analysis was created
        results_count: The total number of results in the analysis
        rules_count: The total number of rules used in the analysis
        id: Unique identifier for this analysis
        url: The REST API URL of the analysis resource
        sarif_id: An identifier for the upload
        tool: The tool used to generate the code scanning analysis
        deletable:
        warning: Warning generated when processing the analysis
    """

    ref: str
    commit_sha: str
    analysis_key: str
    environment: str
    category: str
    error: str
    created_at: datetime
    results_count: int
    rules_count: int
    id: int
    url: str
    sarif_id: str
    tool: Tool
    deletable: bool
    warning: str


@dataclass
class CodeQLDatabase(GitHubModel):
    """
    A CodeQL database

    Attributes:
        id: The ID of the CodeQL database
        name: The name of the CodeQL database
        language: The language of the CodeQL database
        uploader: A GitHub user
        content_type: The MIME type of the CodeQL database file
        size: The size of the CodeQL database file in bytes
        created_at: The date and time at which the CodeQL database was created
        updated_at: The date and time at which the CodeQL database was last
            updated
        url: The URL at which to download the CodeQL database
        commit_oid: The commit SHA of the repository at the time the CodeQL
            database was created
    """

    id: int
    name: str
    language: str
    uploader: User
    content_type: str
    size: int
    created_at: datetime
    updated_at: datetime
    url: str
    commit_oid: Optional[str] = None


class DefaultSetupState(StrEnum):
    """
    State of a default setup
    """

    CONFIGURED = "configured"
    NOT_CONFIGURED = "not-configured"


class Language(StrEnum):
    """
    Analyzed Language
    """

    C_CPP = "c-cpp"
    CSHARP = "csharp"
    GO = "go"
    JAVA_KOTLIN = "java-kotlin"
    JAVASCRIPT_TYPESCRIPT = "javascript-typescript"
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    RUBY = "ruby"
    TYPESCRIPT = "typescript"
    SWIFT = "swift"


class QuerySuite(StrEnum):
    """
    Used code scanning query suite
    """

    DEFAULT = "default"
    EXTENDED = "extended"


@dataclass
class DefaultSetup(GitHubModel):
    """
    Code scanning default setup configuration

    Attributes:
        state: Code scanning default setup has been configured or not
        languages: Languages to be analyzed
        query_suite: CodeQL query suite to be used
        updated_at: Timestamp of latest configuration update
        schedule: The frequency of the periodic analysis
    """

    state: DefaultSetupState
    languages: list[Language]
    query_suite: QuerySuite
    updated_at: Optional[datetime] = None
    schedule: Optional[str] = None


class SarifProcessingStatus(StrEnum):
    """
    `pending` files have not yet been processed, while `complete` means results
    from the SARIF have been stored. `failed` files have either not been
    processed at all, or could only be partially processed
    """

    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class SarifUploadInformation(GitHubModel):
    """
    Information about the SARIF upload

    Attributes:
        processing_status: Status of the SARIF processing
        analyses_url: The REST API URL for getting the analyses associated with
            the upload
        errors: Any errors that ocurred during processing of the delivery
    """

    processing_status: SarifProcessingStatus
    analyses_url: Optional[str] = None
    errors: Optional[list[str]] = None
