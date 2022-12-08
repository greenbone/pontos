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

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from pontos.models import Model


class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AccessVector(Enum):
    NETWORK = "NETWORK"
    ADJACENT_NETWORK = "ADJACENT_NETWORK"
    LOCAL = "LOCAL"


class AccessComplexity(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Authentication(Enum):
    MULTIPLE = "MULTIPLE"
    SINGLE = "SINGLE"
    NONE = "NONE"


class Impact(Enum):
    NONE = "NONE"
    PARTIAL = "PARTIAL"
    COMPLETE = "COMPLETE"


class Exploitability(Enum):
    UNPROVEN = "UNPROVEN"
    PROOF_OF_CONCEPT = "PROOF_OF_CONCEPT"
    FUNCTIONAL = "FUNCTIONAL"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


class RemediationLevel(Enum):
    OFFICIAL_FIX = "OFFICIAL_FIX"
    TEMPORARY_FIX = "TEMPORARY_FIX"
    WORKAROUND = "WORKAROUND"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_DEFINED = "NOT_DEFINED"


class ReportConfidence(Enum):
    UNCONFIRMED = "UNCONFIRMED"
    UNCORROBORATED = "UNCORROBORATED"
    CONFIRMED = "CONFIRMED"
    NOT_DEFINED = "NOT_DEFINED"


class CollateralDamagePotential(Enum):
    NONE = "NONE"
    LOW = "LOW"
    LOW_MEDIUM = "LOW_MEDIUM"
    MEDIUM_HIGH = "MEDIUM_HIGH"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


class TargetDistribution(Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


class Requirement(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    NOT_DEFINED = "NOT_DEFINED"


@dataclass
class CVSSData(Model):
    version: str
    vector_string: str
    base_score: float
    access_vector: Optional[AccessVector] = None
    access_complexity: Optional[AccessComplexity] = None
    authentication: Optional[Authentication] = None
    confidentiality_impact: Optional[Impact] = None
    integrity_impact: Optional[Impact] = None
    availability_impact: Optional[Impact] = None
    exploitability: Optional[Exploitability] = None
    remediation_level: Optional[RemediationLevel] = None
    report_confidence: Optional[ReportConfidence] = None
    temporal_score: Optional[float] = None
    collateral_damage_potential: Optional[CollateralDamagePotential] = None
    target_distribution: Optional[TargetDistribution] = None
    confidentiality_requirement: Optional[Requirement] = None
    integrity_requirement: Optional[Requirement] = None
    availability_requirement: Optional[Requirement] = None
    environmental_score: Optional[float] = None
