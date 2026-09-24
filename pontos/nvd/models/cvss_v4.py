# SPDX-FileCopyrightText: 2026 Greenbone AG
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
    ADJACENT = "ADJACENT"
    LOCAL = "LOCAL"
    PHYSICAL = "PHYSICAL"


class ModifiedAttackVector(StrEnum):
    NETWORK = "NETWORK"
    ADJACENT = "ADJACENT"
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


class AttackRequirements(StrEnum):
    NONE = "NONE"
    PRESENT = "PRESENT"


class ModifiedAttackRequirements(StrEnum):
    NONE = "NONE"
    PRESENT = "PRESENT"
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
    PASSIVE = "PASSIVE"
    ACTIVE = "ACTIVE"


class ModifiedUserInteraction(StrEnum):
    NONE = "NONE"
    PASSIVE = "PASSIVE"
    ACTIVE = "ACTIVE"
    NOT_DEFINED = "NOT_DEFINED"


class VulnCiaImpact(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    HIGH = "HIGH"


class ModifiedVulnCiaImpact(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


class SubCiaImpact(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    HIGH = "HIGH"


class ModifiedSubCImpact(StrEnum):
    NEGLIGIBLE = "NEGLIGIBLE"
    LOW = "LOW"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


class ModifiedSubIaImpact(StrEnum):
    NEGLIGIBLE = "NEGLIGIBLE"
    LOW = "LOW"
    HIGH = "HIGH"
    SAFETY = "SAFETY"
    NOT_DEFINED = "NOT_DEFINED"


class ExploitMaturity(StrEnum):
    UNREPORTED = "UNREPORTED"
    PROOF_OF_CONCEPT = "PROOF_OF_CONCEPT"
    ATTACKED = "ATTACKED"
    NOT_DEFINED = "NOT_DEFINED"


class CiaRequirement(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


class Safety(StrEnum):
    NEGLIGIBLE = "NEGLIGIBLE"
    PRESENT = "PRESENT"
    NOT_DEFINED = "NOT_DEFINED"


class Automatability(StrEnum):
    NO = "NO"
    YES = "YES"
    NOT_DEFINED = "NOT_DEFINED"


class Recovery(StrEnum):
    AUTOMATIC = "AUTOMATIC"
    USER = "USER"
    IRRECOVERABLE = "IRRECOVERABLE"
    NOT_DEFINED = "NOT_DEFINED"


class ValueDensity(StrEnum):
    DIFFUSE = "DIFFUSE"
    CONCENTRATED = "CONCENTRATED"
    NOT_DEFINED = "NOT_DEFINED"


class VulnerabilityResponseEffort(StrEnum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


class ProviderUrgency(StrEnum):
    CLEAR = "CLEAR"
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"
    NOT_DEFINED = "NOT_DEFINED"


@dataclass
class CVSSData(Model):
    version: str
    vector_string: str
    base_score: float
    base_severity: Severity
    attack_vector: AttackVector | None = None
    attack_complexity: AttackComplexity | None = None
    attack_requirements: AttackRequirements | None = None
    privileges_required: PrivilegesRequired | None = None
    user_interaction: UserInteraction | None = None
    vuln_confidentiality_impact: VulnCiaImpact | None = None
    vuln_integrity_impact: VulnCiaImpact | None = None
    vuln_availability_impact: VulnCiaImpact | None = None
    sub_confidentiality_impact: SubCiaImpact | None = None
    sub_integrity_impact: SubCiaImpact | None = None
    sub_availability_impact: SubCiaImpact | None = None
    exploit_maturity: ExploitMaturity | None = None
    confidentiality_requirement: CiaRequirement | None = None
    integrity_requirement: CiaRequirement | None = None
    availability_requirement: CiaRequirement | None = None
    modified_attack_vector: ModifiedAttackVector | None = None
    modified_attack_complexity: ModifiedAttackComplexity | None = None
    modified_attack_requirements: ModifiedAttackRequirements | None = None
    modified_privileges_required: ModifiedPrivilegesRequired | None = None
    modified_user_interaction: ModifiedUserInteraction | None = None
    modified_vuln_integrity_impact: ModifiedVulnCiaImpact | None = None
    modified_vuln_availability_impact: ModifiedVulnCiaImpact | None = None
    modified_vuln_confidentiality_impact: ModifiedVulnCiaImpact | None = None
    modified_sub_integrity_impact: ModifiedSubCImpact | None = None
    modified_sub_availability_impact: ModifiedSubIaImpact | None = None
    modified_sub_confidentiality_impact: ModifiedSubIaImpact | None = None
    safety: Safety | None = None
    automatable: Automatability | None = None
    recovery: Recovery | None = None
    value_density: ValueDensity | None = None
    vulnerability_response_effort: VulnerabilityResponseEffort | None = None
    provider_urgency: ProviderUrgency | None = None
