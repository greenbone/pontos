# Copyright (C) 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import defaultdict
from collections.abc import Container
from copy import deepcopy
from typing import Any, Dict, List, Set

from pontos.csaf import RelationshipCategory


class Relationship:
    def __init__(self, relationship: Dict[str, Any]):
        self._data = relationship

    def __hash__(self):
        # Should be unique for a given CSAF.
        return hash((self.parent_id, self.child_id, self.id))

    def __eq__(self, other):
        if not isinstance(other, (Relationship, dict)):
            return False
        if isinstance(other, Relationship):
            return self._data == other._data
        return self._data == other

    @property
    def product(self) -> Dict[str, Any]:
        return self._data["full_product_name"]

    @property
    def parent_id(self) -> str:
        return self._data["relates_to_product_reference"]

    @property
    def kind(self) -> RelationshipCategory:
        return RelationshipCategory(self._data["category"])

    @property
    def child_id(self) -> str:
        return self._data["product_reference"]

    @property
    def id(self) -> str:
        return self._data["full_product_name"]["product_id"]

    @staticmethod
    def create_combined_parent_to_child_mapping(
        relationships: List["Relationship"],
    ) -> Dict[str, Set[str]]:
        """Creates the typical {product -> {packages}} map, but by ID"""
        res = defaultdict(set)
        for relationship in relationships:
            res[relationship.parent_id].add(relationship.child_id)
        return dict(res)

    @staticmethod
    def build_root_to_leaf_map(
        root_relationships: List["Relationship"],
        inner_tree_relationships: List["Relationship"],
        leaf_product_ids: Container[str],
    ) -> Dict[str, set[str]]:

        if not root_relationships:
            raise ValueError("Cannot build leaf to root map without roots.")

        elif not inner_tree_relationships:
            # can directly read them from the root nodes.
            return Relationship.create_combined_parent_to_child_mapping(
                root_relationships
            )

        elif not leaf_product_ids:
            raise ValueError(
                "For a forest with inner nodes requires inputs which product "
                "references shall be considered leafs for simplicity."
            )

        remaining_inner_relationships = set(deepcopy(inner_tree_relationships))

        res = defaultdict(set)

        relationship_to_root = {
            root.id: root.parent_id for root in root_relationships
        }
        current_parent_ids = set(relationship_to_root.keys())

        # if some trees in the forest are trivial
        leaf_to_root = {
            root.child_id: root.parent_id
            for root in root_relationships
            if root.child_id in leaf_product_ids
        }

        while remaining_inner_relationships:

            matching_inner_children = {
                child
                for child in remaining_inner_relationships
                if child.parent_id in current_parent_ids
            }
            if not matching_inner_children:
                break

            for child in matching_inner_children:
                if child.parent_id not in relationship_to_root:
                    raise ValueError(
                        f"Orphaned Relationship with ID {child.id}"
                    )

                root_id = relationship_to_root[child.parent_id]

                # Step 2
                if child.child_id in leaf_product_ids:
                    # otherwise, it is a complex relationship ID
                    leaf_to_root[child.child_id] = root_id

            current_parent_ids = {child.id for child in matching_inner_children}

            remaining_inner_relationships = (
                remaining_inner_relationships - matching_inner_children
            )

        for relationship_id, root_id in leaf_to_root.items():
            res[root_id].add(relationship_id)

        return dict(res)
