# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from dataclasses import dataclass

from pontos.models import Model, StrEnum


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AccessVector(StrEnum):
    NETWORK = "NETWORK"
    ADJACENT_NETWORK = "ADJACENT_NETWORK"
    LOCAL = "LOCAL"


class AccessComplexity(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Authentication(StrEnum):
    MULTIPLE = "MULTIPLE"
    SINGLE = "SINGLE"
    NONE = "NONE"


class Impact(StrEnum):
    NONE = "NONE"
    PARTIAL = "PARTIAL"
    COMPLETE = "COMPLETE"


class Exploitability(StrEnum):
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


class ReportConfidence(StrEnum):
    UNCONFIRMED = "UNCONFIRMED"
    UNCORROBORATED = "UNCORROBORATED"
    CONFIRMED = "CONFIRMED"
    NOT_DEFINED = "NOT_DEFINED"


class CollateralDamagePotential(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    LOW_MEDIUM = "LOW_MEDIUM"
    MEDIUM_HIGH = "MEDIUM_HIGH"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


class TargetDistribution(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
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
    access_vector: AccessVector | None = None
    access_complexity: AccessComplexity | None = None
    authentication: Authentication | None = None
    confidentiality_impact: Impact | None = None
    integrity_impact: Impact | None = None
    availability_impact: Impact | None = None
    exploitability: Exploitability | None = None
    remediation_level: RemediationLevel | None = None
    report_confidence: ReportConfidence | None = None
    temporal_score: float | None = None
    collateral_damage_potential: CollateralDamagePotential | None = None
    target_distribution: TargetDistribution | None = None
    confidentiality_requirement: Requirement | None = None
    integrity_requirement: Requirement | None = None
    availability_requirement: Requirement | None = None
    environmental_score: float | None = None
