# SPDX-FileCopyrightText: 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa: E501

import json
import unittest
from pathlib import Path

from pontos.csaf import Csaf, Relationship, RelationshipCategory, Remediation
from pontos.errors import PontosError


def get_advisory_content(idx: int = 1) -> Csaf:
    file = Path(__file__).parent / f"csaf_sample_{idx}.json"
    data = json.loads(file.read_text())
    return Csaf(data)


class RedHatTestCase(unittest.TestCase):
    def test_advisory_id(self):
        csaf = get_advisory_content()
        expected_result = "RHSA-2024:1234"
        self.assertEqual(csaf.advisory_id, expected_result)

    def test_reference_urls(self):
        csaf = get_advisory_content()
        self_urls = {
            "https://access.redhat.com/errata/RHSA-2024:1234",
            "https://security.access.redhat.com/data/csaf/v2/advisories/2024/rhsa-2024_1234.json",
        }

        external_urls = {
            "https://access.redhat.com/security/updates/classification/#important",
            "https://bugzilla.redhat.com/show_bug.cgi?id=2178363",
            "https://issues.redhat.com/browse/FD-3267",
            "https://issues.redhat.com/browse/FDP-308",
        }

        self.assertEqual(
            csaf.get_reference_urls(
                allow_self_references=True, allow_external_references=False
            ),
            self_urls,
        )

        self.assertEqual(
            csaf.get_reference_urls(
                allow_self_references=False, allow_external_references=True
            ),
            external_urls,
        )

        self.assertEqual(
            csaf.get_reference_urls(
                allow_self_references=True, allow_external_references=True
            ),
            external_urls | self_urls,
        )
        with self.assertRaises(PontosError):
            csaf.get_reference_urls(
                allow_self_references=False, allow_external_references=False
            )

    def test_title(self):
        csaf = get_advisory_content()
        expected_result = (
            "Red Hat Security Advisory: openvswitch2.17 security update"
        )
        self.assertEqual(csaf.title, expected_result)

    def test_initial_release_year(self):
        csaf = get_advisory_content()
        expected_result = 2024
        self.assertEqual(csaf.initial_release_year, expected_result)

    def test_contains_product_tree(self):
        csaf = get_advisory_content()
        self.assertTrue(csaf.contains_product_tree)

    def test_first_inner_product_branch(self):
        csaf = get_advisory_content()
        expected_res = {
            "category": "product_name",
            "name": "Fast Datapath for Red Hat Enterprise Linux 8",
            "product": {
                "name": "Fast Datapath for Red Hat Enterprise Linux 8",
                "product_id": "8Base-Fast-Datapath",
                "product_identification_helper": {
                    "cpe": "cpe:/o:redhat:enterprise_linux:8::fastdatapath"
                },
            },
        }

        res = next(csaf.iter_inner_product_branches())

        self.assertEqual(res, expected_res)

    def test_get_all_cves_from_vulnerabilities_mentioned(self):
        csaf = get_advisory_content()
        expected_result = {"CVE-2023-3966", "CVE-2023-5366"}
        self.assertEqual(
            csaf.get_cves_from_vulnerabilities_mentioned(), expected_result
        )

    def test_get_all_cves_that_mention_one_of_the_product_ids_as_fixed(self):
        csaf = get_advisory_content()
        expected_result = {"CVE-2023-3966", "CVE-2023-5366"}
        self.assertEqual(
            csaf.get_all_cves_that_mention_one_of_the_product_ids_as_fixed(),
            expected_result,
        )
        self.assertEqual(
            csaf.get_all_cves_that_mention_one_of_the_product_ids_as_fixed(
                restrict_to_product_ids={
                    "8Base-Fast-Datapath:network-scripts-openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                }
            ),
            expected_result,
        )

        expected_partial_result = {
            "CVE-2023-5366",
        }
        self.assertEqual(
            csaf.get_all_cves_that_mention_one_of_the_product_ids_as_fixed(
                restrict_to_product_ids={
                    "only_in_fixed_status",
                }
            ),
            expected_partial_result,
        )

    def test_get_remediation_category_for_related_cves(self):
        csaf = get_advisory_content()
        expected_result = {
            "CVE-2023-3966": {Remediation.VENDOR_FIX},
            "CVE-2023-5366": {Remediation.VENDOR_FIX},
        }

        res = csaf.get_remediation_category_for_related_cves(
            "8Base-Fast-Datapath:network-scripts-openvswitch2.17-0:2.17.0-148.el8fdp.aarch64"
        )

        self.assertDictEqual(res, expected_result)

        expected_result = {
            "CVE-2023-3966": {Remediation.VENDOR_FIX},
            "CVE-2023-5366": {None},
        }
        res = csaf.get_remediation_category_for_related_cves(
            "only_fixed_for_one_cve"
        )

        self.assertDictEqual(res, expected_result)

    def test_prod_has_vendor_fix_for_all_cves_affected_by(self):
        csaf = get_advisory_content()
        self.assertTrue(
            csaf.prod_has_vendor_fix_for_all_cves_affected_by(
                "only_in_fixed_status"
            )
        )

        self.assertFalse(
            csaf.prod_has_vendor_fix_for_all_cves_affected_by(
                "only_fixed_for_one_cve"
            )
        )

    def test_get_matching_relationships_no_transitivity(self):
        csaf = get_advisory_content()
        expected_res = (
            [
                Relationship(
                    {
                        "category": "default_component_of",
                        "full_product_name": {
                            "name": "network-scripts-openvswitch2.17-0:2.17.0-148.el8fdp.aarch64 as a component of Fast Datapath for Red Hat Enterprise Linux 8",
                            "product_id": "8Base-Fast-Datapath:network-scripts-openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                        },
                        "product_reference": "network-scripts-openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                        "relates_to_product_reference": "8Base-Fast-Datapath",
                    }
                ),
                Relationship(
                    {
                        "category": "optional_component_of",
                        "full_product_name": {
                            "name": "openvswitch2.17-0:2.17.0-148.el8fdp.aarch64 as a component of Fast Datapath for Red Hat Enterprise Linux 8",
                            "product_id": "8Base-Fast-Datapath:openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                        },
                        "product_reference": "openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                        "relates_to_product_reference": "8Base-Fast-DatapathOtherParent",
                    }
                ),
                Relationship(
                    {
                        "category": "default_component_of",
                        "full_product_name": {
                            "name": "pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64 as a component of postgresql:15:9020020230619032405:rhel9 as a component of Red Hat Enterprise Linux AppStream (v. 9)",
                            "product_id": "AppStream-9.2.0.Z.MAIN.EUS:postgresql:15:9020020230619032405:rhel9:pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64",
                        },
                        "product_reference": "pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64",
                        "relates_to_product_reference": "8Base-Fast-Datapath:network-scripts-openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                    }
                ),
            ],
            [],
        )

        res = csaf.get_matching_relationships(
            restrict_to_categories=None,
            restrict_to_parent_ids=None,
            apply_transitively=False,
        )
        self.assertEqual(res, expected_res)

        expected_res = (
            [
                Relationship(
                    {
                        "category": "optional_component_of",
                        "full_product_name": {
                            "name": "openvswitch2.17-0:2.17.0-148.el8fdp.aarch64 as a component of Fast Datapath for Red Hat Enterprise Linux 8",
                            "product_id": "8Base-Fast-Datapath:openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                        },
                        "product_reference": "openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                        "relates_to_product_reference": "8Base-Fast-DatapathOtherParent",
                    }
                )
            ],
            [],
        )

        res = csaf.get_matching_relationships(
            restrict_to_categories={RelationshipCategory.OPTIONAL_COMPONENT_OF},
            restrict_to_parent_ids=None,
            apply_transitively=False,
        )
        self.assertEqual(res, expected_res)

        res = csaf.get_matching_relationships(
            restrict_to_categories=None,
            restrict_to_parent_ids={
                "8Base-Fast-DatapathOtherParent",
            },
            apply_transitively=False,
        )
        self.assertEqual(res, expected_res)

    def test_get_matching_relationships_with_transitivity(self):
        csaf = get_advisory_content()
        expected_res = (
            [
                Relationship(
                    {
                        "category": "default_component_of",
                        "full_product_name": {
                            "name": "network-scripts-openvswitch2.17-0:2.17.0-148.el8fdp.aarch64 as a component of Fast Datapath for Red Hat Enterprise Linux 8",
                            "product_id": "8Base-Fast-Datapath:network-scripts-openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                        },
                        "product_reference": "network-scripts-openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                        "relates_to_product_reference": "8Base-Fast-Datapath",
                    }
                ),
            ],
            [
                Relationship(
                    {
                        "category": "default_component_of",
                        "full_product_name": {
                            "name": "pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64 as a component of postgresql:15:9020020230619032405:rhel9 as a component of Red Hat Enterprise Linux AppStream (v. 9)",
                            "product_id": "AppStream-9.2.0.Z.MAIN.EUS:postgresql:15:9020020230619032405:rhel9:pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64",
                        },
                        "product_reference": "pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64",
                        "relates_to_product_reference": "8Base-Fast-Datapath:network-scripts-openvswitch2.17-0:2.17.0-148.el8fdp.aarch64",
                    }
                )
            ],
        )

        res = csaf.get_matching_relationships(
            restrict_to_categories=None,
            restrict_to_parent_ids={
                "8Base-Fast-Datapath",
            },
            apply_transitively=True,
        )
        self.assertEqual(res, expected_res)


#     def test_parse_insight(self):
#         redhat = RedHat()
#         advisory_content = get_advisory_content()
#         insight, xrefs = redhat._parse_insight(advisory_content)
#         expected_result = """The mod_nss module provides strong cryptography for the Apache HTTP Server via the Secure Sockets Layer (SSL) and Transport Layer Security (TLS) protocols, using the Network Security Services (NSS) security library.
#
# This update fixes the following bugs:
#
# * When the NSS library was not initialized and mod_nss tried to clear its SSL cache on start-up, mod_nss terminated unexpectedly when the NSS library was built with debugging enabled. With this update, mod_nss does not try to clear the SSL cache in the described scenario, thus preventing this bug. (BZ#691502)"""
#
#         self.assertEqual(expected_result, insight)
#         self.assertEqual(xrefs, [])
#
#     def test_parse_cves(self):
#         redhat = RedHat()
#         advisory_content = get_advisory_content()
#         cves = redhat._parse_cves(advisory_content)
#         expected_result = ["CVE-2024-4973"]
#         self.assertEqual(expected_result, cves)
#
#     # def test_parse_advisory_id(self):
#     #     redhat = RedHat()
#     #     advisory_content = get_advisory_content()
#     #     advisory_id = redhat._parse_advisory_id(advisory_content)
#     #     expected_result = "RHBA-2024:1234"
#     #     self.assertEqual(expected_result, advisory_id)
#
#     def test_get_packages(self):
#         redhat = RedHat()
#         advisory_content = get_advisory_content()
#         advisory = redhat._parse_advisory_content(advisory_content)[0]
#         packages = redhat._get_all_packages(advisory_content)
#         product_packages = redhat._get_packages(advisory, packages, "6")
#         expected_result = defaultdict(set)
#         expected_result.update(
#             {
#                 "Red Hat Enterprise Linux 6": {
#                     "mod_nss-0:1.0.8-13.el6.i686",
#                     "mod_nss-0:1.0.8-13.el6.ppc64",
#                     "mod_nss-0:1.0.8-13.el6.x86_64",
#                     "mod_nss-0:1.0.8-13.el6.s390x",
#                 }
#             }
#         )
#         self.assertEqual(expected_result, product_packages)
#
#     def test_get_vulnerability_information(self):
#         redhat = RedHat()
#         redhat._get_full_xml = MagicMock(return_value=[get_advisory_content()][0])
#         redhat._parse_advisory = MagicMock(return_value=Advisory())
#
#         expected_result = VulnerabilityInformation()
#         expected_result.advisories.add_advisory(Advisory())
#         expected_result.products.add_packages(
#             "Red Hat Enterprise Linux 6",
#             "1.3.6.1.4.1.25623.1.1.11.2024.1234",
#             [
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.i686"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.ppc64"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.s390x"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.x86_64"),
#             ],
#         )
#         expected_result.products.add_packages(
#             "Red Hat Enterprise Linux 7",
#             "1.3.6.1.4.1.25623.1.1.11.2024.1234",
#             [
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.i686"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.ppc64"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.s390x"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.x86_64"),
#             ],
#         )
#         expected_result.products.add_packages(
#             "Red Hat Enterprise Linux 8",
#             "1.3.6.1.4.1.25623.1.1.11.2024.1234",
#             [
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.i686"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.ppc64"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.s390x"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.x86_64"),
#             ],
#         )
#         expected_result.products.add_packages(
#             "Red Hat Enterprise Linux 9",
#             "1.3.6.1.4.1.25623.1.1.11.2024.1234",
#             [
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.i686"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.ppc64"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.s390x"),
#                 Package(full_name="mod_nss-0:1.0.8-13.el6.x86_64"),
#             ],
#         )
#
#         vulnerability_information = VulnerabilityInformation()
#         result = redhat.get_vulnerability_information(vulnerability_information)
#         self.assertEqual(expected_result, result)
#
#     def test_parse_advisory(self):
#         redhat = RedHat()
#         advisory_content = get_advisory_content()
#         all_packages = redhat._get_all_packages(advisory_content)
#
#         advisory = redhat._parse_advisory(
#             "1.3.6.1.4.1.25623.1.1.11.2024.1234",
#             "RHSA-2024:1234",
#             advisory_content,
#             redhat._get_packages(advisory_content, all_packages, "6"),
#             None,
#         )
#         expected_advisory = Advisory()
#         expected_advisory.oid = "1.3.6.1.4.1.25623.1.1.11.2024.1234"
#         expected_advisory.title = "Red Hat Enterprise Linux: Security Advisory (RHSA-2024:1234)"
#         expected_advisory.advisory_xref = "https://access.redhat.com/errata/RHSA-2024:1234"
#         expected_advisory.advisory_id = "RHSA-2024:1234"
#         expected_advisory.summary = (
#             "The remote host is missing an update for the "
#             "'mod_nss' package(s) announced via the RHSA-2024:1234 advisory."
#         )
#         expected_advisory.cves = ["CVE-2024-4973"]
#         expected_advisory.insight = """The mod_nss module provides strong cryptography for the Apache HTTP Server via the Secure Sockets Layer (SSL) and Transport Layer Security (TLS) protocols, using the Network Security Services (NSS) security library.
#
# This update fixes the following bugs:
#
# * When the NSS library was not initialized and mod_nss tried to clear its SSL cache on start-up, mod_nss terminated unexpectedly when the NSS library was built with debugging enabled. With this update, mod_nss does not try to clear the SSL cache in the described scenario, thus preventing this bug. (BZ#691502)"""
#         expected_advisory.affected = "'mod_nss' package(s) on Red Hat Enterprise Linux 6."
#         self.assertEqual(expected_advisory, advisory)
