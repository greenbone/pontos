# SPDX-FileCopyrightText: 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa: E501

import unittest

from pontos.csaf import Relationship


class CSAFRelationshipTestCase(unittest.TestCase):
    def test_create_combined_parent_to_child_mapping(self):
        relationships = [
            Relationship(
                {
                    "product_reference": "abc",
                    "relates_to_product_reference": "same_parent",
                }
            ),
            Relationship(
                {
                    "product_reference": "def",
                    "relates_to_product_reference": "same_parent",
                }
            ),
            Relationship(
                {
                    "product_reference": "abc",
                    "relates_to_product_reference": "different_parent",
                }
            ),
        ]
        expected_res = {
            "same_parent": {"abc", "def"},
            "different_parent": {"abc"},
        }
        res = Relationship.create_combined_parent_to_child_mapping(
            relationships
        )
        self.assertEqual(res, expected_res)

    def test_build_root_to_leaf_map_no_inner_relationships(self):
        root_relationships = [
            Relationship(
                {
                    "product_reference": "abc",
                    "relates_to_product_reference": "same_parent",
                }
            ),
            Relationship(
                {
                    "product_reference": "def",
                    "relates_to_product_reference": "same_parent",
                    "full_product_name": {"product_id": "childRel1"},
                }
            ),
            Relationship(
                {
                    "product_reference": "abc",
                    "relates_to_product_reference": "different_parent",
                    "full_product_name": {"product_id": "childRel2"},
                }
            ),
        ]
        expected_res = Relationship.create_combined_parent_to_child_mapping(
            root_relationships
        )
        res = Relationship.build_root_to_leaf_map(root_relationships, [], set())
        self.assertEqual(res, expected_res)

        res2 = Relationship.build_root_to_leaf_map(
            root_relationships, [], {"1", "2"}
        )
        self.assertEqual(res2, expected_res)

    def test_build_root_to_leaf_map_throws(self):

        root_relationships = [
            Relationship(
                {
                    "product_reference": "abc",
                    "relates_to_product_reference": "same_parent",
                }
            ),
        ]
        with self.assertRaises(ValueError):
            Relationship.build_root_to_leaf_map([], [], set())

        with self.assertRaises(ValueError):
            Relationship.build_root_to_leaf_map([], root_relationships, set())

    def test_build_to_root_three_layered_forest(self):
        root_relationships = [
            Relationship(
                {
                    "category": "default_component_of",
                    "full_product_name": {
                        "name": "postgresql:15:9020020230619032405:rhel9 as a component of Red Hat Enterprise Linux AppStream (v. 9)",
                        "product_id": "AppStream-9.2.0.Z.MAIN.EUS:postgresql:15:9020020230619032405:rhel9",
                    },
                    "product_reference": "postgresql:15:9020020230619032405:rhel9",
                    "relates_to_product_reference": "AppStream-9.2.0.Z.MAIN.EUS",
                }
            )
        ]
        inner_relationships = [
            Relationship(
                {
                    "category": "default_component_of",
                    "full_product_name": {
                        "name": "pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64 as a component of postgresql:15:9020020230619032405:rhel9 as a component of Red Hat Enterprise Linux AppStream (v. 9)",
                        "product_id": "AppStream-9.2.0.Z.MAIN.EUS:postgresql:15:9020020230619032405:rhel9:pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64",
                    },
                    "product_reference": "pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64",
                    "relates_to_product_reference": "AppStream-9.2.0.Z.MAIN.EUS:postgresql:15:9020020230619032405:rhel9",
                }
            ),
            Relationship(
                {
                    "category": "default_component_of",
                    "full_product_name": {
                        "name": "postgresql-upgrade-devel-0:15.3-1.module+el9.2.0.z+19113+6f5d9d63.x86_64 as a component of postgresql:15:9020020230619032405:rhel9 as a component of Red Hat Enterprise Linux AppStream (v. 9)",
                        "product_id": "AppStream-9.2.0.Z.MAIN.EUS:postgresql:15:9020020230619032405:rhel9:postgresql-upgrade-devel-0:15.3-1.module+el9.2.0.z+19113+6f5d9d63.x86_64",
                    },
                    "product_reference": "postgresql-upgrade-devel-0:15.3-1.module+el9.2.0.z+19113+6f5d9d63.x86_64",
                    "relates_to_product_reference": "AppStream-9.2.0.Z.MAIN.EUS:postgresql:15:9020020230619032405:rhel9",
                }
            ),
        ]

        leaf_product_ids = {
            "postgresql-upgrade-devel-0:15.3-1.module+el9.2.0.z+19113+6f5d9d63.x86_64",
            "pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64",
        }

        expected_res = {
            "AppStream-9.2.0.Z.MAIN.EUS": {
                "postgresql-upgrade-devel-0:15.3-1.module+el9.2.0.z+19113+6f5d9d63.x86_64",
                "pg_repack-0:1.4.8-1.module+el9.2.0+17405+aeb9ec60.aarch64",
            },
        }
        res = Relationship.build_root_to_leaf_map(
            root_relationships, inner_relationships, leaf_product_ids
        )
        self.assertDictEqual(res, expected_res)
