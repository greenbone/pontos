# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from dataclasses import dataclass

from pontos.models import Model, StrEnum


class Severity(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AttackVector(StrEnum):
    NETWORK = "NETWORK"
    ADJACENT_NETWORK = "ADJACENT_NETWORK"
    LOCAL = "LOCAL"
    PHYSICAL = "PHYSICAL"


class ModifiedAttackVector(StrEnum):
    NETWORK = "NETWORK"
    ADJACENT_NETWORK = "ADJACENT_NETWORK"
    LOCAL = "LOCAL"
    PHYSICAL = "PHYSICAL"
    NOT_DEFINED = "NOT_DEFINED"


class AttackComplexity(StrEnum):
    HIGH = "HIGH"
    LOW = "LOW"


class ModifiedAttackComplexity(StrEnum):
    HIGH = "HIGH"
    LOW = "LOW"
    NOT_DEFINED = "NOT_DEFINED"


class PrivilegesRequired(StrEnum):
    HIGH = "HIGH"
    LOW = "LOW"
    NONE = "NONE"


class ModifiedPrivilegesRequired(StrEnum):
    HIGH = "HIGH"
    LOW = "LOW"
    NONE = "NONE"
    NOT_DEFINED = "NOT_DEFINED"


class UserInteraction(StrEnum):
    NONE = "NONE"
    REQUIRED = "REQUIRED"


class ModifiedUserInteraction(StrEnum):
    NONE = "NONE"
    REQUIRED = "REQUIRED"
    NOT_DEFINED = "NOT_DEFINED"


class Scope(StrEnum):
    UNCHANGED = "UNCHANGED"
    CHANGED = "CHANGED"


class ModifiedScope(StrEnum):
    UNCHANGED = "UNCHANGED"
    CHANGED = "CHANGED"
    NOT_DEFINED = "NOT_DEFINED"


class Impact(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    HIGH = "HIGH"


class ModifiedImpact(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


class ExploitCodeMaturity(StrEnum):
    UNPROVEN = "UNPROVEN"
    PROOF_OF_CONCEPT = "PROOF_OF_CONCEPT"
    FUNCTIONAL = "FUNCTIONAL"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


class RemediationLevel(StrEnum):
    OFFICIAL_FIX = "OFFICIAL_FIX"
    TEMPORARY_FIX = "TEMPORARY_FIX"
    WORKAROUND = "WORKAROUND"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_DEFINED = "NOT_DEFINED"


class Confidence(StrEnum):
    UNKNOWN = "UNKNOWN"
    REASONABLE = "REASONABLE"
    CONFIRMED = "CONFIRMED"
    NOT_DEFINED = "NOT_DEFINED"


class Requirement(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


@dataclass
class CVSSData(Model):
    version: str
    vector_string: str
    base_score: float
    base_severity: Severity
    attack_vector: AttackVector | None = None
    attack_complexity: AttackComplexity | None = None
    privileges_required: PrivilegesRequired | None = None
    user_interaction: UserInteraction | None = None
    scope: Scope | None = None
    confidentiality_impact: Impact | None = None
    integrity_impact: Impact | None = None
    availability_impact: Impact | None = None
    exploit_code_maturity: ExploitCodeMaturity | None = None
    remediation_level: RemediationLevel | None = None
    report_confidence: Confidence | None = None
    temporal_score: float | None = None
    temporal_severity: Severity | None = None
    confidentiality_requirement: Requirement | None = None
    integrity_requirement: Requirement | None = None
    availability_requirement: Requirement | None = None
    modified_attack_vector: ModifiedAttackVector | None = None
    modified_attack_complexity: ModifiedAttackComplexity | None = None
    modified_privileges_required: ModifiedPrivilegesRequired | None = None
    modified_user_interaction: ModifiedUserInteraction | None = None
    modified_scope: ModifiedScope | None = None
    modified_confidentiality_impact: ModifiedImpact | None = None
    modified_integrity_impact: ModifiedImpact | None = None
    modified_availability_impact: ModifiedImpact | None = None
    environmental_score: float | None = None
    environmental_severity: Severity | None = None
