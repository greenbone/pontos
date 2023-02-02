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

# pylint: disable=line-too-long

import unittest
from datetime import date, datetime

from pontos.nvd.models import cvss_v2, cvss_v3
from pontos.nvd.models.cve import CVE, CVSSType, Operator
from tests.nvd import get_cve_data


class CVETestCase(unittest.TestCase):
    def test_required_only(self):
        cve = CVE.from_dict(get_cve_data())

        self.assertEqual(cve.id, "CVE-2022-45536")
        self.assertEqual(cve.source_identifier, "cve@mitre.org")
        self.assertEqual(
            cve.published, datetime(2022, 11, 22, 21, 15, 11, 103000)
        )
        self.assertEqual(
            cve.last_modified, datetime(2022, 11, 23, 16, 2, 7, 367000)
        )
        self.assertEqual(len(cve.descriptions), 1)
        self.assertEqual(len(cve.references), 2)
        self.assertEqual(len(cve.weaknesses), 0)
        self.assertEqual(len(cve.configurations), 0)
        self.assertEqual(len(cve.vendor_comments), 0)
        self.assertIsNone(cve.metrics)
        self.assertIsNone(cve.evaluator_comment)
        self.assertIsNone(cve.evaluator_solution)
        self.assertIsNone(cve.evaluator_impact)
        self.assertIsNone(cve.cisa_exploit_add)
        self.assertIsNone(cve.cisa_action_due)
        self.assertIsNone(cve.cisa_required_action)
        self.assertIsNone(cve.cisa_vulnerability_name)

    def test_descriptions(self):
        cve = CVE.from_dict(get_cve_data())

        description = cve.descriptions[0]
        self.assertEqual(description.lang, "en")
        self.assertEqual(
            description.value,
            "AeroCMS v0.0.1 was discovered to contain a SQL "
            "Injection vulnerability via the id parameter at "
            "\\admin\\post_comments.php. This vulnerability allows "
            "attackers to access database information.",
        )

    def test_references(self):
        cve = CVE.from_dict(get_cve_data())

        reference = cve.references[0]
        self.assertEqual(
            reference.url,
            "https://github.com/rdyx0/CVE/blob/master/AeroCMS/AeroCMS-v0.0.1-SQLi/post_comments_sql_injection/post_comments_sql_injection.md",
        )
        self.assertEqual(reference.source, "cve@mitre.org")
        self.assertEqual(reference.tags, ["Exploit", "Third Party Advisory"])

        reference = cve.references[1]
        self.assertEqual(
            reference.url,
            "https://rdyx0.github.io/2018/09/07/AeroCMS-v0.0.1-SQLi%20post_comments_sql_injection/",
        )
        self.assertEqual(reference.source, "cve@mitre.org")
        self.assertEqual(reference.tags, ["Exploit", "Third Party Advisory"])

    def test_weaknesses(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "weaknesses": [
                        {
                            "source": "nvd@nist.gov",
                            "type": "Primary",
                            "description": [{"lang": "en", "value": "CWE-89"}],
                        }
                    ],
                }
            )
        )

        self.assertEqual(len(cve.weaknesses), 1)

        weakness = cve.weaknesses[0]
        self.assertEqual(weakness.source, "nvd@nist.gov")
        self.assertEqual(weakness.type, "Primary")
        self.assertEqual(len(weakness.description), 1)

        description = weakness.description[0]
        self.assertEqual(description.lang, "en")
        self.assertEqual(description.value, "CWE-89")

    def test_configuration(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "configurations": [
                        {
                            "nodes": [
                                {
                                    "operator": "OR",
                                    "negate": False,
                                    "cpe_match": [
                                        {
                                            "vulnerable": True,
                                            "criteria": "cpe:2.3:a:aerocms_project:aerocms:0.0.1:*:*:*:*:*:*:*",
                                            "match_criteria_id": "52639E84-244D-4DA3-B1AE-6D8BA1C38863",
                                        }
                                    ],
                                }
                            ]
                        }
                    ],
                }
            )
        )

        self.assertEqual(len(cve.configurations), 1)

        configuration = cve.configurations[0]
        self.assertIsNone(configuration.operator)
        self.assertIsNone(configuration.negate)
        self.assertEqual(len(configuration.nodes), 1)

        node = configuration.nodes[0]
        self.assertFalse(node.negate)
        self.assertEqual(node.operator, Operator.OR)
        self.assertEqual(len(node.cpe_match), 1)

        cpe_match = node.cpe_match[0]
        self.assertTrue(cpe_match.vulnerable)
        self.assertEqual(
            cpe_match.criteria,
            "cpe:2.3:a:aerocms_project:aerocms:0.0.1:*:*:*:*:*:*:*",
        )
        self.assertEqual(
            cpe_match.match_criteria_id, "52639E84-244D-4DA3-B1AE-6D8BA1C38863"
        )
        self.assertIsNone(cpe_match.version_start_including)
        self.assertIsNone(cpe_match.version_start_excluding)
        self.assertIsNone(cpe_match.version_end_including)
        self.assertIsNone(cpe_match.version_end_excluding)

    def test_metrics_v2(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "metrics": {
                        "cvss_metric_v2": [
                            {
                                "source": "nvd@nist.gov",
                                "type": "Primary",
                                "cvss_data": {
                                    "version": "2.0",
                                    "vector_string": "AV:N/AC:M/Au:N/C:N/I:P/A:N",
                                    "access_vector": "NETWORK",
                                    "access_complexity": "MEDIUM",
                                    "authentication": "NONE",
                                    "confidentiality_impact": "NONE",
                                    "integrity_impact": "PARTIAL",
                                    "availability_impact": "NONE",
                                    "base_score": 4.3,
                                    "base_severity": "MEDIUM",
                                },
                                "exploitability_score": 8.6,
                                "impact_score": 2.9,
                                "ac_insuf_info": False,
                                "obtain_all_privilege": False,
                                "obtain_user_privilege": False,
                                "obtain_other_privilege": False,
                                "user_interaction_required": True,
                            }
                        ]
                    }
                }
            )
        )

        self.assertEqual(len(cve.metrics.cvss_metric_v2), 1)
        self.assertEqual(len(cve.metrics.cvss_metric_v30), 0)
        self.assertEqual(len(cve.metrics.cvss_metric_v31), 0)

        cvss_metric = cve.metrics.cvss_metric_v2[0]
        self.assertEqual(cvss_metric.source, "nvd@nist.gov")
        self.assertEqual(cvss_metric.type, CVSSType.PRIMARY)
        self.assertEqual(cvss_metric.exploitability_score, 8.6)
        self.assertEqual(cvss_metric.impact_score, 2.9)
        self.assertFalse(cvss_metric.ac_insuf_info)
        self.assertFalse(cvss_metric.obtain_all_privilege)
        self.assertFalse(cvss_metric.obtain_user_privilege)
        self.assertFalse(cvss_metric.obtain_other_privilege)
        self.assertTrue(cvss_metric.user_interaction_required)

        cvss_data = cvss_metric.cvss_data
        self.assertEqual(cvss_data.version, "2.0")
        self.assertEqual(cvss_data.vector_string, "AV:N/AC:M/Au:N/C:N/I:P/A:N")
        self.assertEqual(cvss_data.base_score, 4.3)
        self.assertEqual(cvss_data.access_vector, cvss_v2.AccessVector.NETWORK)
        self.assertEqual(
            cvss_data.access_complexity, cvss_v2.AccessComplexity.MEDIUM
        )
        self.assertEqual(cvss_data.authentication, cvss_v2.Authentication.NONE)
        self.assertEqual(cvss_data.confidentiality_impact, cvss_v2.Impact.NONE)
        self.assertEqual(cvss_data.integrity_impact, cvss_v2.Impact.PARTIAL)
        self.assertEqual(cvss_data.availability_impact, cvss_v2.Impact.NONE)
        self.assertIsNone(cvss_data.exploitability)
        self.assertIsNone(cvss_data.remediation_level)
        self.assertIsNone(cvss_data.report_confidence)
        self.assertIsNone(cvss_data.temporal_score)
        self.assertIsNone(cvss_data.collateral_damage_potential)
        self.assertIsNone(cvss_data.target_distribution)
        self.assertIsNone(cvss_data.confidentiality_requirement)
        self.assertIsNone(cvss_data.integrity_requirement)
        self.assertIsNone(cvss_data.availability_requirement)
        self.assertIsNone(cvss_data.environmental_score)

    def test_metrics_v30(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "metrics": {
                        "cvss_metric_v30": [
                            {
                                "source": "nvd@nist.gov",
                                "type": "Primary",
                                "cvss_data": {
                                    "version": "3.0",
                                    "vector_string": "CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
                                    "attack_vector": "NETWORK",
                                    "attack_complexity": "LOW",
                                    "privileges_required": "NONE",
                                    "user_interaction": "REQUIRED",
                                    "scope": "CHANGED",
                                    "confidentiality_impact": "LOW",
                                    "integrity_impact": "LOW",
                                    "availability_impact": "NONE",
                                    "base_score": 6.1,
                                    "base_severity": "MEDIUM",
                                },
                                "exploitability_score": 2.8,
                                "impact_score": 2.7,
                            }
                        ],
                    }
                }
            )
        )

        self.assertEqual(len(cve.metrics.cvss_metric_v2), 0)
        self.assertEqual(len(cve.metrics.cvss_metric_v30), 1)
        self.assertEqual(len(cve.metrics.cvss_metric_v31), 0)

        cvss_metric = cve.metrics.cvss_metric_v30[0]
        self.assertEqual(cvss_metric.source, "nvd@nist.gov")
        self.assertEqual(cvss_metric.type, CVSSType.PRIMARY)
        self.assertEqual(cvss_metric.exploitability_score, 2.8)
        self.assertEqual(cvss_metric.impact_score, 2.7)

        cvss_data = cvss_metric.cvss_data
        self.assertEqual(cvss_data.version, "3.0")
        self.assertEqual(
            cvss_data.vector_string,
            "CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
        )
        self.assertEqual(cvss_data.base_score, 6.1)
        self.assertEqual(cvss_data.base_severity, cvss_v3.Severity.MEDIUM)
        self.assertEqual(cvss_data.attack_vector, cvss_v3.AttackVector.NETWORK)
        self.assertEqual(
            cvss_data.attack_complexity, cvss_v3.AttackComplexity.LOW
        )
        self.assertEqual(
            cvss_data.privileges_required, cvss_v3.PrivilegesRequired.NONE
        )
        self.assertEqual(
            cvss_data.user_interaction, cvss_v3.UserInteraction.REQUIRED
        )
        self.assertEqual(cvss_data.scope, cvss_v3.Scope.CHANGED)
        self.assertEqual(cvss_data.confidentiality_impact, cvss_v3.Impact.LOW)
        self.assertEqual(cvss_data.integrity_impact, cvss_v3.Impact.LOW)
        self.assertEqual(cvss_data.availability_impact, cvss_v3.Impact.NONE)
        self.assertIsNone(cvss_data.exploit_code_maturity)
        self.assertIsNone(cvss_data.remediation_level)
        self.assertIsNone(cvss_data.report_confidence)
        self.assertIsNone(cvss_data.temporal_score)
        self.assertIsNone(cvss_data.temporal_severity)
        self.assertIsNone(cvss_data.confidentiality_requirement)
        self.assertIsNone(cvss_data.integrity_requirement)
        self.assertIsNone(cvss_data.availability_requirement)
        self.assertIsNone(cvss_data.modified_attack_vector)
        self.assertIsNone(cvss_data.modified_attack_complexity)
        self.assertIsNone(cvss_data.modified_privileges_required)
        self.assertIsNone(cvss_data.modified_user_interaction)
        self.assertIsNone(cvss_data.modified_scope)
        self.assertIsNone(cvss_data.modified_confidentiality_impact)
        self.assertIsNone(cvss_data.modified_integrity_impact)
        self.assertIsNone(cvss_data.modified_availability_impact)
        self.assertIsNone(cvss_data.environmental_score)
        self.assertIsNone(cvss_data.environmental_severity)

    def test_metrics_v31(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "metrics": {
                        "cvss_metric_v31": [
                            {
                                "source": "nvd@nist.gov",
                                "type": "Primary",
                                "cvss_data": {
                                    "version": "3.1",
                                    "vector_string": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N",
                                    "attack_vector": "NETWORK",
                                    "attack_complexity": "LOW",
                                    "privileges_required": "HIGH",
                                    "user_interaction": "NONE",
                                    "scope": "UNCHANGED",
                                    "confidentiality_impact": "HIGH",
                                    "integrity_impact": "NONE",
                                    "availability_impact": "NONE",
                                    "base_score": 4.9,
                                    "base_severity": "MEDIUM",
                                },
                                "exploitability_score": 1.2,
                                "impact_score": 3.6,
                            }
                        ]
                    },
                }
            )
        )

        self.assertEqual(len(cve.metrics.cvss_metric_v2), 0)
        self.assertEqual(len(cve.metrics.cvss_metric_v30), 0)
        self.assertEqual(len(cve.metrics.cvss_metric_v31), 1)

        cvss_metric = cve.metrics.cvss_metric_v31[0]
        self.assertEqual(cvss_metric.source, "nvd@nist.gov")
        self.assertEqual(cvss_metric.type, CVSSType.PRIMARY)
        self.assertEqual(cvss_metric.exploitability_score, 1.2)
        self.assertEqual(cvss_metric.impact_score, 3.6)

        cvss_data = cvss_metric.cvss_data
        self.assertEqual(cvss_data.version, "3.1")
        self.assertEqual(
            cvss_data.vector_string,
            "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N",
        )
        self.assertEqual(cvss_data.base_score, 4.9)
        self.assertEqual(cvss_data.base_severity, cvss_v3.Severity.MEDIUM)
        self.assertEqual(cvss_data.attack_vector, cvss_v3.AttackVector.NETWORK)
        self.assertEqual(
            cvss_data.attack_complexity, cvss_v3.AttackComplexity.LOW
        )
        self.assertEqual(
            cvss_data.privileges_required, cvss_v3.PrivilegesRequired.HIGH
        )
        self.assertEqual(
            cvss_data.user_interaction, cvss_v3.UserInteraction.NONE
        )
        self.assertEqual(cvss_data.scope, cvss_v3.Scope.UNCHANGED)
        self.assertEqual(cvss_data.confidentiality_impact, cvss_v3.Impact.HIGH)
        self.assertEqual(cvss_data.integrity_impact, cvss_v3.Impact.NONE)
        self.assertEqual(cvss_data.availability_impact, cvss_v3.Impact.NONE)
        self.assertIsNone(cvss_data.exploit_code_maturity)
        self.assertIsNone(cvss_data.remediation_level)
        self.assertIsNone(cvss_data.report_confidence)
        self.assertIsNone(cvss_data.temporal_score)
        self.assertIsNone(cvss_data.temporal_severity)
        self.assertIsNone(cvss_data.confidentiality_requirement)
        self.assertIsNone(cvss_data.integrity_requirement)
        self.assertIsNone(cvss_data.availability_requirement)
        self.assertIsNone(cvss_data.modified_attack_vector)
        self.assertIsNone(cvss_data.modified_attack_complexity)
        self.assertIsNone(cvss_data.modified_privileges_required)
        self.assertIsNone(cvss_data.modified_user_interaction)
        self.assertIsNone(cvss_data.modified_scope)
        self.assertIsNone(cvss_data.modified_confidentiality_impact)
        self.assertIsNone(cvss_data.modified_integrity_impact)
        self.assertIsNone(cvss_data.modified_availability_impact)
        self.assertIsNone(cvss_data.environmental_score)
        self.assertIsNone(cvss_data.environmental_severity)

    def test_metrics_v31_severity_none(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "metrics": {
                        "cvss_metric_v31": [
                            {
                                "source": "nvd@nist.gov",
                                "type": "Secondary",
                                "cvss_data": {
                                    "version": "3.1",
                                    "vector_string": "CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:N",
                                    "attack_vector": "NETWORK",
                                    "attack_complexity": "LOW",
                                    "privileges_required": "NONE",
                                    "user_interaction": "REQUIRED",
                                    "scope": "UNCHANGED",
                                    "confidentiality_impact": "NONE",
                                    "integrity_impact": "NONE",
                                    "availability_impact": "NONE",
                                    "base_score": 0.0,
                                    "base_severity": "NONE",
                                },
                                "exploitability_score": 2.8,
                                "impact_score": 0.0,
                            }
                        ]
                    },
                }
            )
        )

        self.assertEqual(len(cve.metrics.cvss_metric_v2), 0)
        self.assertEqual(len(cve.metrics.cvss_metric_v30), 0)
        self.assertEqual(len(cve.metrics.cvss_metric_v31), 1)

        cvss_metric = cve.metrics.cvss_metric_v31[0]
        self.assertEqual(cvss_metric.source, "nvd@nist.gov")
        self.assertEqual(cvss_metric.type, CVSSType.SECONDARY)
        self.assertEqual(cvss_metric.exploitability_score, 2.8)
        self.assertEqual(cvss_metric.impact_score, 0.0)

        cvss_data = cvss_metric.cvss_data
        self.assertEqual(cvss_data.version, "3.1")
        self.assertEqual(
            cvss_data.vector_string,
            "CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:N",
        )
        self.assertEqual(cvss_data.base_score, 0.0)
        self.assertEqual(cvss_data.base_severity, cvss_v3.Severity.NONE)
        self.assertEqual(cvss_data.attack_vector, cvss_v3.AttackVector.NETWORK)
        self.assertEqual(
            cvss_data.attack_complexity, cvss_v3.AttackComplexity.LOW
        )
        self.assertEqual(
            cvss_data.privileges_required, cvss_v3.PrivilegesRequired.NONE
        )
        self.assertEqual(
            cvss_data.user_interaction, cvss_v3.UserInteraction.REQUIRED
        )
        self.assertEqual(cvss_data.scope, cvss_v3.Scope.UNCHANGED)
        self.assertEqual(cvss_data.confidentiality_impact, cvss_v3.Impact.NONE)
        self.assertEqual(cvss_data.integrity_impact, cvss_v3.Impact.NONE)
        self.assertEqual(cvss_data.availability_impact, cvss_v3.Impact.NONE)
        self.assertIsNone(cvss_data.exploit_code_maturity)
        self.assertIsNone(cvss_data.remediation_level)
        self.assertIsNone(cvss_data.report_confidence)
        self.assertIsNone(cvss_data.temporal_score)
        self.assertIsNone(cvss_data.temporal_severity)
        self.assertIsNone(cvss_data.confidentiality_requirement)
        self.assertIsNone(cvss_data.integrity_requirement)
        self.assertIsNone(cvss_data.availability_requirement)
        self.assertIsNone(cvss_data.modified_attack_vector)
        self.assertIsNone(cvss_data.modified_attack_complexity)
        self.assertIsNone(cvss_data.modified_privileges_required)
        self.assertIsNone(cvss_data.modified_user_interaction)
        self.assertIsNone(cvss_data.modified_scope)
        self.assertIsNone(cvss_data.modified_confidentiality_impact)
        self.assertIsNone(cvss_data.modified_integrity_impact)
        self.assertIsNone(cvss_data.modified_availability_impact)
        self.assertIsNone(cvss_data.environmental_score)
        self.assertIsNone(cvss_data.environmental_severity)

    def test_vendor_comments(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "vendor_comments": [
                        {
                            "organization": "Apache",
                            "comment": "Fixed in Apache HTTP Server 1.3.12:\nhttp://httpd.apache.org/security/vulnerabilities_13.html",
                            "last_modified": "2008-07-02T00:00:00",
                        }
                    ],
                }
            )
        )

        self.assertEqual(len(cve.vendor_comments), 1)

        comment = cve.vendor_comments[0]
        self.assertEqual(comment.organization, "Apache")
        self.assertEqual(
            comment.comment,
            "Fixed in Apache HTTP Server 1.3.12:\nhttp://httpd.apache.org/security/vulnerabilities_13.html",
        )
        self.assertEqual(comment.last_modified, datetime(2008, 7, 2))

    def test_evaluator_comment(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "evaluator_comment": "Please see the following link for more information:\r\n\r\nhttp://seclists.org/bugtraq/1999/Jan/0215.html"
                }
            )
        )

        self.assertEqual(
            cve.evaluator_comment,
            "Please see the following link for more information:\r\n\r\nhttp://seclists.org/bugtraq/1999/Jan/0215.html",
        )

    def test_evaluator_solution(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "evaluator_solution": "This problem was fixed in Linux kernel 2.2.4 and later releases."
                }
            )
        )

        self.assertEqual(
            cve.evaluator_solution,
            "This problem was fixed in Linux kernel 2.2.4 and later releases.",
        )

    def test_evaluator_impact(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "evaluator_impact": "This Common Vulnerabilities and Exposures (CVE) entry is a configuration issue and not a software flaw. As such, it doesn’t fit in the CVE software flaw list. The Common Vulnerability Scoring System (CVSS) base score for this CVE entry has been set to 0 because this CVE entry has no impact as a software flaw according to CVSS. This does not mean that the configuration issue is not important and there may be security implications relative to computers having this configuration."
                }
            )
        )

        self.assertEqual(
            cve.evaluator_impact,
            "This Common Vulnerabilities and Exposures (CVE) entry is a configuration issue and not a software flaw. As such, it doesn’t fit in the CVE software flaw list. The Common Vulnerability Scoring System (CVSS) base score for this CVE entry has been set to 0 because this CVE entry has no impact as a software flaw according to CVSS. This does not mean that the configuration issue is not important and there may be security implications relative to computers having this configuration.",
        )

    def test_cisa(self):
        cve = CVE.from_dict(
            get_cve_data(
                {
                    "cisa_exploit_add": "2022-03-03",
                    "cisa_action_due": "2022-03-24",
                    "cisa_required_action": "Apply updates per vendor instructions.",
                    "cisa_vulnerability_name": "Microsoft Windows Privilege Escalation Vulnerability",
                }
            )
        )

        self.assertEqual(cve.cisa_action_due, date(2022, 3, 24))
        self.assertEqual(cve.cisa_exploit_add, date(2022, 3, 3))
        self.assertEqual(
            cve.cisa_required_action, "Apply updates per vendor instructions."
        )
        self.assertEqual(
            cve.cisa_vulnerability_name,
            "Microsoft Windows Privilege Escalation Vulnerability",
        )
