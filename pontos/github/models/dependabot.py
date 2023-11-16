# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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
    State of the GitHub Dependabot Security Alert
    """

    AUTO_DISMISSED = "auto_dismissed"
    DISMISSED = "dismissed"
    FIXED = "fixed"
    OPEN = "open"


class DismissedReason(StrEnum):
    """
    Reason phrase for a dismissed Dependabot alert
    """

    FIX_STARTED = "fix_started"
    INACCURATE = "inaccurate"
    NO_BANDWIDTH = "no_bandwidth"
    NOT_USED = "not_used"
    TOLERABLE_RISK = "tolerable_risk"


class DependencyScope(StrEnum):
    """
    The execution scope of the vulnerable dependency
    """

    DEVELOPMENT = "development"
    RUNTIME = "runtime"


class Severity(StrEnum):
    """
    The severity of the vulnerability
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IdentifierType(StrEnum):
    """
    The type of advisory identifier
    """

    CVE = "CVE"
    GHSA = "GHSA"


@dataclass
class VulnerablePackage(GitHubModel):
    """
    Details about a vulnerable Package

    Attributes:
        ecosystem: The package's language or package management ecosystem
        name: The unique package name within its ecosystem
    """

    ecosystem: str
    name: str


@dataclass
class PatchedVersion(GitHubModel):
    """
    Details pertaining to the package version that patches a vulnerability

    Attributes:
        identifier: The package version that patches the vulnerability
    """

    identifier: str


@dataclass
class Vulnerability(GitHubModel):
    """
    Details pertaining to one vulnerable version range for the advisory

    Attributes:
        package: Details about the vulnerable package
        severity: The severity of the vulnerability
        vulnerable_version_range: Conditions that identify vulnerable versions
            of this vulnerability's package
        first_patched_version: The package version that patches this
            vulnerability
    """

    package: VulnerablePackage
    severity: Severity
    vulnerable_version_range: str
    first_patched_version: Optional[PatchedVersion] = None


@dataclass
class Dependency(GitHubModel):
    """
    Details for the vulnerable dependency

    Attributes:
        package: Details about the vulnerable package
        manifest_path: The full path to the dependency manifest file, relative
            to the root of the repository
        scope: The execution scope of the vulnerable dependency
    """

    package: VulnerablePackage
    manifest_path: str
    scope: Optional[DependencyScope] = None


@dataclass
class CVSS(GitHubModel):
    """
    Details for the advisory pertaining to the Common Vulnerability Scoring
    System (CVSS)

    Attributes:
        score: The overall CVSS score of the advisory
        vector_string: The full CVSS vector string for the advisory
    """

    score: float
    vector_string: Optional[str] = None


@dataclass
class CWE(GitHubModel):
    """
    Details for the advisory pertaining to Common Weakness Enumeration (CWE)

    Attributes:
        cwe_id: The unique CWE ID
        name: The short, plain text name of the CWE
    """

    cwe_id: str
    name: str


@dataclass
class Identifier(GitHubModel):
    """
    An advisory identifier

    Attributes:
        type: The type of advisory identifier
        value: The value of the advisory identifier
    """

    type: IdentifierType
    value: str


@dataclass
class Reference(GitHubModel):
    """
    A link to additional advisory information

    Attributes:
        url: URL for the additional advisory information
    """

    url: str


@dataclass
class SecurityAdvisory(GitHubModel):
    """
    Details for the GitHub Security Advisory

    Attributes:
        ghsa_id: The unique GitHub Security Advisory ID assigned to the advisory
        cve_id: The unique CVE ID assigned to the advisory
        summary: A short, plain text summary of the advisory
        description: A long-form Markdown-supported description of the advisory
        vulnerabilities: Vulnerable version range information for the advisory
        severity: The severity of the advisory
        cvss: The overall CVSS score of the advisory
        cwes: CWE weaknesses assigned to the advisory
        identifiers: Values that identify this advisory among security
            information sources
        references: Links to additional advisory information
        published_at: The time that the advisory was published
        updated_at: The time that the advisory was last modified
        withdrawn_at: The time that the advisory was withdrawn
    """

    ghsa_id: str
    summary: str
    description: str
    vulnerabilities: list[Vulnerability]
    severity: Severity
    cvss: CVSS
    cwes: list[CWE]
    identifiers: list[Identifier]
    references: list[Reference]
    published_at: datetime
    updated_at: datetime
    cve_id: Optional[str] = None
    withdrawn_at: Optional[datetime] = None


@dataclass
class DependabotAlert(GitHubModel):
    """
    A GitHub dependabot security alert model

    Attributes:
        number: The security alert number
        state: The state of the Dependabot alert
        dependency: Details for the vulnerable dependency
        security_advisory: Details for the GitHub Security Advisory
        security_vulnerability: Details pertaining to one vulnerable version
            range for the advisory
        url: The REST API URL of the alert resource
        html_url: The GitHub URL of the alert resource
        created_at: The time that the alert was created
        updated_at: The time that the alert was last updated
        dismissed_at: The time that the alert was dismissed
        dismissed_by: User who dismissed the alert
        dismissed_reason: The reason that the alert was dismissed
        dismissed_comment: An optional comment associated with the alert's
            dismissal
        fixed_at: The time that the alert was no longer detected and was
            considered fixed
        auto_dismissed_at: The time that the alert was auto-dismissed
        repository: The GitHub repository containing the alert. It's not
            returned when requesting a specific alert
    """

    number: int
    state: AlertState
    dependency: Dependency
    security_advisory: SecurityAdvisory
    security_vulnerability: Vulnerability
    url: str
    html_url: str
    created_at: datetime
    updated_at: datetime
    repository: Optional[Repository] = None
    dismissed_at: Optional[datetime] = None
    dismissed_by: Optional[User] = None
    dismissed_reason: Optional[DismissedReason] = None
    dismissed_comment: Optional[str] = None
    fixed_at: Optional[datetime] = None
    auto_dismissed_at: Optional[datetime] = None
