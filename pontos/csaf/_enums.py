# Copyright (C) 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import Set

from pontos.models import StrEnum


class Remediation(StrEnum):
    VENDOR_FIX = "vendor_fix"
    WORKAROUND = "workaround"
    NONE_AVAILABLE = "none_available"
    NO_FIX_PLANNED = "no_fix_planned"
    MITIGATION = "mitigation"


class ProductStatus(StrEnum):
    FIRST_AFFECTED = "first_affected"
    FIRST_FIXED = "first_fixed"
    FIXED = "fixed"
    KNOWN_AFFECTED = "known_affected"
    KNOWN_NOT_AFFECTED = "known_not_affected"
    LAST_AFFECTED = "last_affected"
    RECOMMENDED = "recommended"
    UNDER_INVESTIGATION = "under_investigation"

    @staticmethod
    def all_confirmed_affected_keys() -> Set["ProductStatus"]:
        return {
            ProductStatus.FIRST_AFFECTED,
            ProductStatus.KNOWN_AFFECTED,
            ProductStatus.LAST_AFFECTED,
        }

    @staticmethod
    def all_explicitly_fixed_keys() -> Set["ProductStatus"]:
        return {
            ProductStatus.FIRST_FIXED,
            ProductStatus.FIXED,
        }


class RelationshipCategory(StrEnum):
    DEFAULT_COMPONENT_OF = "default_component_of"
    EXTERNAL_COMPONENT_OF = "external_component_of"
    OPTIONAL_COMPONENT_OF = "optional_component_of"
    INSTALLED_ON = "installed_on"
    INSTALLED_WITH = "installed_with"


class CsafBranchCategory(StrEnum):
    PRODUCT_VERSION_RANGE = "product_version_range"
    PRODUCT_VERSION = "product_version"
    PRODUCT_NAME = "product_name"
    VENDOR = "vendor"
    ARCHITECTURE = "architecture"
