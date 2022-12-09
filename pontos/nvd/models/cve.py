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

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pontos.models import Model
from pontos.nvd.models.cvss_v2 import CVSSData as CVSSv2Data
from pontos.nvd.models.cvss_v3 import CVSSData as CVSSv3Data

__all__ = ("CVE",)


class CVSSType(Enum):
    PRIMARY = "Primary"
    SECONDARY = "Secondary"


@dataclass
class Description(Model):
    lang: str
    value: str


@dataclass
class CVSSv2Metric(Model):
    source: str
    type: CVSSType
    cvss_data: CVSSv2Data
    base_severity: Optional[str] = None
    exploitability_score: Optional[float] = None
    impact_score: Optional[float] = None
    ac_insuf_info: Optional[bool] = None
    obtain_all_privilege: Optional[bool] = None
    obtain_user_privilege: Optional[bool] = None
    obtain_other_privilege: Optional[bool] = None
    user_interaction_required: Optional[bool] = None


@dataclass
class CVSSv3Metric(Model):
    source: str
    type: CVSSType
    cvss_data: CVSSv3Data
    exploitability_score: Optional[float] = None
    impact_score: Optional[float] = None


@dataclass
class Metrics(Model):
    cvss_metric_v31: List[CVSSv3Metric] = field(default_factory=list)
    cvss_metric_v30: List[CVSSv3Metric] = field(default_factory=list)
    cvss_metric_v2: List[CVSSv2Metric] = field(default_factory=list)


@dataclass
class Reference(Model):
    url: str
    source: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class Weakness(Model):
    source: str
    type: str
    description: List[Description] = field(default_factory=list)


@dataclass
class VendorComment(Model):
    organization: str
    comment: str
    last_modified: datetime


class Operator(Enum):
    AND = "AND"
    OR = "OR"


@dataclass
class CPEMatch(Model):
    vulnerable: bool
    criteria: str
    match_criteria_id: str
    version_start_excluding: Optional[str] = None
    version_start_including: Optional[str] = None
    version_end_excluding: Optional[str] = None
    version_end_including: Optional[str] = None


@dataclass
class Node(Model):
    operator: Operator
    cpe_match: List[CPEMatch]
    negate: Optional[bool] = None


@dataclass
class Configuration(Model):
    nodes: List[Node]
    operator: Optional[Operator] = None
    negate: Optional[bool] = None


@dataclass
class CVE(Model):
    id: str
    source_identifier: str
    published: datetime
    last_modified: datetime
    vuln_status: str
    descriptions: List[Description]
    references: List[Reference]
    weaknesses: List[Weakness] = field(default_factory=list)
    configurations: List[Configuration] = field(default_factory=list)
    vendor_comments: List[VendorComment] = field(default_factory=list)
    metrics: Optional[Metrics] = None
    evaluator_comment: Optional[str] = None
    evaluator_solution: Optional[str] = None
    evaluator_impact: Optional[str] = None
    cisa_exploit_add: Optional[date] = None
    cisa_action_due: Optional[date] = None
    cisa_required_action: Optional[str] = None
    cisa_vulnerability_name: Optional[str] = None
