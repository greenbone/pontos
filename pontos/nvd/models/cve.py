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

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from pontos.models import Model, StrEnum
from pontos.nvd.models.cvss_v2 import CVSSData as CVSSv2Data
from pontos.nvd.models.cvss_v3 import CVSSData as CVSSv3Data

__all__ = (
    "Configuration",
    "CPEMatch",
    "CVSSType",
    "CVSSv2Metric",
    "CVSSv3Metric",
    "Description",
    "Metrics",
    "Node",
    "Operator",
    "Reference",
    "VendorComment",
    "Weakness",
    "CVE",
)


class CVSSType(StrEnum):
    """
    The CVSS Type: primary or secondary

    Attributes:
        PRIMARY: A primary CVSS
        SECONDARY: A secondary CVSS
    """

    PRIMARY = "Primary"
    SECONDARY = "Secondary"


@dataclass
class Description(Model):
    """
    A description in a specific language

    Attributes:
        lang: Language of the description
        value: The actual description
    """

    lang: str
    value: str


@dataclass
class CVSSv2Metric(Model):
    """
    A CVSSv3 metric

    Attributes:
        source: The source of the CVSS
        type: The CVSS type
        cvss_data: The actual CVSSv2 data
        base_severity:
        exploitability_score:
        impact_score:
        ac_insuf_info:
        obtain_all_privilege:
        obtain_user_privilege:
        obtain_other_privilege:
        user_interaction_required:
    """

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
    """
    A CVSSv3 metric

    Attributes:
        source: The source of the CVSS
        type: The CVSS type
        cvss_data: The actual CVSSv3 data
        exploitability_score:
        impact_score:
    """

    source: str
    type: CVSSType
    cvss_data: CVSSv3Data
    exploitability_score: Optional[float] = None
    impact_score: Optional[float] = None


@dataclass
class Metrics(Model):
    """
    CVE metrics

    Attributes:
        cvss_metric_v31: A list of CVSSv3.1 metrics
        cvss_metric_v30: A list of CVSSv3.0 metrics
        cvss_metric_v2: A list of CVSSv2 metrics
    """

    cvss_metric_v31: List[CVSSv3Metric] = field(default_factory=list)
    cvss_metric_v30: List[CVSSv3Metric] = field(default_factory=list)
    cvss_metric_v2: List[CVSSv2Metric] = field(default_factory=list)


@dataclass
class Reference(Model):
    """
    A CVE reference

    Attributes:
        url: URL to the reference
        source: Source of the reference
        tags: List of tags for the reference
    """

    url: str
    source: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class Weakness(Model):
    """
    Attributes:
        source:
        type:
        description:
    """

    source: str
    type: str
    description: List[Description] = field(default_factory=list)


@dataclass
class VendorComment(Model):
    """
    A vendor comment

    Attributes:
        organization: Name of the vendor
        comment: The actual comment of the vendor
        last_modified: Last modification date of the comment
    """

    organization: str
    comment: str
    last_modified: datetime


class Operator(StrEnum):
    """
    An operator: AND or OR

    Attributes:
        AND: A and operator
        OR: A or operator
    """

    AND = "AND"
    OR = "OR"


@dataclass
class CPEMatch(Model):
    """
    A CPE match referencing a vulnerable product with a version range

    Attributes:
        vulnerable:
        criteria:
        match_criteria_id:
        version_start_excluding: Matches the CPE excluding the specified version
        version_start_including: Matches the CPE including the specified version
        version_end_excluding: Matches the CPE excluding up to the specified
            version
        version_end_including: Matches the CPE including up to the specified
            version
    """

    vulnerable: bool
    criteria: str
    match_criteria_id: str
    version_start_excluding: Optional[str] = None
    version_start_including: Optional[str] = None
    version_end_excluding: Optional[str] = None
    version_end_including: Optional[str] = None


@dataclass
class Node(Model):
    """
    A CVE configuration node

    Attributes:
        operator: Operator (and/or) for this node
        cpe_match: The CPE match for the node. Despite a cpe match is required
            int NISTs API spec the data seems to contain nodes without matches.
        negate:
    """

    operator: Operator
    cpe_match: Optional[List[CPEMatch]] = None
    negate: Optional[bool] = None


@dataclass
class Configuration(Model):
    """
    A CVE configuration

    Attributes:
        nodes:
        operator:
        negate:
    """

    nodes: List[Node]
    operator: Optional[Operator] = None
    negate: Optional[bool] = None


@dataclass
class CVE(Model):
    """
    A model representing a CVE

    Attributes:
        id: ID of the CVE
        source_identifier: Identifier for the source of the CVE
        published: Date of publishing
        last_modified: Last modification date
        vuln_status: Current vulnerability status
        descriptions: List of additional descriptions
        references: List of additional references (URLs)
        weaknesses: List of weaknesses
        configurations: List of configurations
        vendor_comments: List of vendor comments
        metrics: List of CVSS metrics for this CVE
        evaluator_comment:
        evaluator_solution:
        evaluator_impact:
        cisa_exploit_add:
        cisa_action_due:
        cisa_required_action:
        cisa_vulnerability_name:
    """

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
