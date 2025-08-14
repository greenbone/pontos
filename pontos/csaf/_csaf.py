# Copyright (C) 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later


import json
import logging
from typing import Dict, Iterable, List, Set, Tuple, Optional

from black.trans import defaultdict

from pontos.csaf import (
    Relationship,
    RelationshipCategory,
    Remediation,
    Revision,
    Vulnerability,
    iter_next_branches,
)
from pontos.errors import PontosError

logger = logging.getLogger(__name__)


class Csaf(dict):
    """
    Main purpose:
    1. Increased accessibility of common data structures without having
        to remember how exactly all the dictionary keys are called,
        how the structures are nested

    2. Provide parsing of common attributes (CVEs etc.) in their standard location
        if they have a CSAF-dedicated field for it.

    3. Provide extraction of various data in dependencies based on the "product ids".
        These are the unique identifiers given to any specific OS/ package + version/ HW.
        Product identifiers by themselves are just unique IDs specific to each document.
        Specific vendors may use them in such a way, that they also encode semantic meaning,
        but this model does NOT handle finding out any such meaning. It solely uses them
        as generic identifiers (0,1,2,3).

    NOT purpose:
    1. Provide vendor-specific parsing.
        Even more so, if it's not in official compliance to standard.
    """

    """Notes about content types:
    Almost all values are strings, including  "product_id" (cf. 3.1.8).
        Thus, {0} shall never occur, but {"0"} instead and any
        iterable of len != 0 will evaluate to true.
    """

    @property
    def advisory_id(self) -> str:
        return self.document["tracking"]["id"]

    def iter_middle_branches(
        self, limit_to_categories: Optional[Set[str]] = None
    ) -> Iterable[Dict]:
        if "branches" not in self.product_tree:
            logger.warning(
                "{}: product tree doesn't contain any branches.".format(
                    self.advisory_id
                )
            )
            return

        for outer_branch in self.product_tree["branches"]:
            if "branches" not in outer_branch:
                logger.info(
                    "{} Outermost branch doesn't contain branches: {}".format(
                        self.advisory_id, json.dumps(outer_branch)
                    )
                )
            for br in iter_next_branches(
                outer_branch, limit_to_categories=limit_to_categories
            ):
                yield br

    def iter_inner_product_branches(self) -> Iterable[Dict]:
        """Provides all inner product branches - typically specific OSs/SW/HW versions.


        Assumes that these lie at depth 3 in the product-branch tree.
        """
        for second_layer_branch in self.iter_middle_branches():
            if "branches" not in second_layer_branch:
                logger.debug(
                    "{} Middle branch doesn't contain branches: {}".format(
                        self.advisory_id, json.dumps(second_layer_branch)
                    )
                )
                continue
            for br in iter_next_branches(second_layer_branch):
                yield br

    def iter_products_with_cpe(self) -> Iterable[tuple[Dict, str]]:
        """Provides all inner product branches that include a CPE for identification"""
        for prod in self.iter_inner_product_branches():
            if "cpe" not in prod["product"].get(
                "product_identification_helper", {}
            ):
                continue
            yield prod, prod["product"]["product_identification_helper"]["cpe"]

    def get_product_tree_ids(self) -> Set[str]:
        """Get those IDs assigned explicitly to unique products"""
        res = {
            prod["product"]["product_id"]
            for prod in self.iter_inner_product_branches()
        }
        return res

    def get_cves_from_vulnerabilities_mentioned(self) -> Set[str]:
        """Gets explicitly assigned CVEs, i.e., ignores any in descriptive fields."""
        cves = {vuln.cve for vuln in self.vulnerabilities}
        return cves

    def iter_products_with_matching_id(
        self, acceptable_ids: Set[str]
    ) -> Iterable[Dict]:
        """Retrieves complete product structures for these explicit IDs"""
        for prod in self.iter_inner_product_branches():
            if prod["product"]["product_id"] in acceptable_ids:
                yield prod

    def get_reference_urls(
        self, allow_self_references: bool, allow_external_references: bool
    ) -> Set[str]:
        """Retrieve all URLs this document references to in its main section."""
        # only 'self', and 'external' are CSAF-compliant enum entries for the
        # reference category
        allowed_categories = set()
        if allow_self_references:
            allowed_categories.add("self")
        if allow_external_references:
            allowed_categories.add("external")

        if not allowed_categories:
            raise PontosError(
                "At least one reference category must be allowed."
            )
        ref_urls = {
            reference["url"]
            for reference in self.document["references"]
            if reference["category"] in allowed_categories
            and "url" in reference
        }
        return ref_urls

    @property
    def title(self) -> str:
        return self.document["title"]

    @property
    def initial_release_year(self) -> int:
        initial_date = self.document["tracking"]["initial_release_date"]
        year = initial_date.split("-")[0]
        return int(year)

    @property
    def vulnerabilities(self) -> List[Vulnerability]:
        """Retrieves all vulnerabilities listed in a parsed format."""
        return [Vulnerability(v) for v in self.get("vulnerabilities", [])]

    @property
    def contains_product_tree(self) -> bool:
        # although *usually* contained, not required
        # and e.g., Microsoft doesn't always use it
        return "product_tree" in self

    @property
    def product_tree(self) -> Dict:
        # optional in CSAF, but most common
        return self["product_tree"]

    @property
    def relationships(self) -> List[Relationship]:
        # not mandatory element to be populated, thus fine for an empty list to be returned
        return [
            Relationship(relationship)
            for relationship in self.product_tree.get("relationships", [])
        ]

    @property
    def revisions(self) -> List[Revision]:
        return [
            Revision(revision)
            for revision in self.document["tracking"].get(
                "revision_history", []
            )
        ]

    @property
    def document(self) -> Dict:
        return self["document"]

    @property
    def notes(self) -> Iterable[Dict]:
        for note in self.document["notes"]:
            yield note

    @property
    def vulnerability_notes(self) -> Iterable[Dict]:
        for vuln in self.vulnerabilities:
            for note in vuln.iter_notes():
                yield note

    @property
    def raw_references(self) -> Iterable[Dict]:
        for reference in self.document["references"]:
            yield reference

    @property
    def has_vulnerabilities(self) -> bool:
        return "vulnerabilities" in self

    def get_matching_relationships(
        self,
        restrict_to_categories: Optional[Set[RelationshipCategory]] = None,
        restrict_to_parent_ids: Optional[Set[str]] = None,
        apply_transitively: bool = False,
    ) -> Tuple[List[Relationship], List[Relationship]]:
        """Retrieves product relationships ('component of' etc.) based on product IDs

        Includes retrieval of the relationship ID

        Args:
            restrict_to_categories: explicitly allowed kinds of relationships
            restrict_to_parent_ids: explicitly allowed "parent" IDs (return keys).
            apply_transitively: store relationship IDs whose parent matched & extract all
                relationship children of that relationship product ID.

        Returns:
            ([relationships with root as explicit parent],
            [relationships with root as implicit parent])
        """

        root_res = []
        transitive_res = []

        remaining_relationships = set()

        for relationship in self.relationships:
            if (
                not restrict_to_categories
                or relationship.kind in restrict_to_categories
            ) and (
                not restrict_to_parent_ids
                or relationship.parent_id in restrict_to_parent_ids
            ):
                root_res.append(relationship)
            # store those of future relevance
            elif apply_transitively and (
                not restrict_to_categories
                or relationship.kind in restrict_to_categories
            ):
                remaining_relationships.add(relationship)

        if apply_transitively:
            next_allowed_parents = {
                relationship.id for relationship in root_res
            }

            while next_fitting_subset := {
                relationship
                for relationship in remaining_relationships
                if relationship.parent_id in next_allowed_parents
            }:
                transitive_res.extend(list(next_fitting_subset))
                remaining_relationships -= next_fitting_subset
                next_allowed_parents = {
                    relationship.id for relationship in next_fitting_subset
                }

        return root_res, transitive_res

    def get_remediation_category_for_related_cves(
        self, prod_id: str
    ) -> Dict[str, Set[Optional[str]]]:
        """Retrieves the CSAF-proposed remediations possible

        Best-case is "vendor_fix" remediation. _Mostly_ this relates to a strict update path.
        The update path may relate to a SW different to the one stated as vulnerable depending
        on the vendor's SW dependency graph, publication and versioning cycle.

        Whether the SW-to-be-updated differs from the reported-as-vulnerable SW cannot be
        assumed across all CSAF publishers and documents.
        For some vendors they always match, for some they mostly match.

        Worst-case is "wont_fix" and no "mitigation" or "workaround' keys. In that case,
        there exists no official solution to circumvent the CVE. Sometimes there still exists
        an upgrade path via major versions though.
        """
        res = defaultdict(set)
        for vuln in self.vulnerabilities:
            if prod_id in vuln.affected_product_ids:
                found_remediation = False
                for rem in vuln.iter_remediations():
                    if prod_id in rem["product_ids"]:
                        res[vuln.cve].add(rem["category"])
                        found_remediation = True

                if not found_remediation:
                    res[vuln.cve].add(None)
            elif prod_id in vuln.confirmed_fixed_product_ids:
                res[vuln.cve].add(Remediation.VENDOR_FIX)

        return dict(res)

    def get_all_cves_that_mention_one_of_the_product_ids_as_fixed(
        self, restrict_to_product_ids: Optional[Set[str]] = None
    ) -> Set[str]:
        """Only retrieves that subset of CVEs interested in.

        If the advisory contains a CVE only affecting products we do not support, then we should
        ignore that CVE.
        """
        res = set()

        if restrict_to_product_ids:
            for vulnerability in self.vulnerabilities:
                if (
                    restrict_to_product_ids
                    & vulnerability.confirmed_fixed_product_ids
                ):
                    res.add(vulnerability.cve)
        else:
            for vulnerability in self.vulnerabilities:
                if vulnerability.confirmed_fixed_product_ids:
                    res.add(vulnerability.cve)

        return res

    def prod_has_vendor_fix_for_all_cves_affected_by(
        self, prod_id: str
    ) -> bool:
        """Verifies that ALL CVEs we report on for this product are fixed by the vendor.

        Optional verification, but required for >= 1 vendor.
        """
        for rem_cats in self.get_remediation_category_for_related_cves(
            prod_id
        ).values():
            if not rem_cats or Remediation.VENDOR_FIX not in rem_cats:
                return False
        return True
