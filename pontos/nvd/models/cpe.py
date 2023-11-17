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
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pontos.models import Model, StrEnum

__all__ = (
    "DeprecatedBy",
    "ReferenceType",
    "Reference",
    "Title",
    "CPE",
)


@dataclass
class Title(Model):
    """
    A CPE title

    Attributes:
        title: The actual title
        lang: Language of the title
    """

    title: str
    lang: str


class ReferenceType(StrEnum):
    """
    A CPE reference type

    Attributes:
        ADVISORY: The reference is an advisory
        CHANGELOG: The reference is a changelog
        PRODUCT: The reference is a product
        PROJECT: The reference is a project
        VENDOR: The reference is a vendor
        VERSION: The reference is version
    """

    ADVISORY = "Advisory"
    CHANGELOG = "Change Log"
    PRODUCT = "Product"
    PROJECT = "Project"
    VENDOR = "Vendor"
    VERSION = "Version"


@dataclass
class Reference(Model):
    """
    A CPE reference

    Attributes:
        ref: The content of the reference
        type: The type of the reference
    """

    ref: str
    type: Optional[ReferenceType] = None


@dataclass
class DeprecatedBy(Model):
    """
    A CPE is deprecated by another CPE

    Attributes:
        cpe_name: Name of the CPE that deprecates this CPE
        cpe_name_id: ID of the CPE that deprecates this CPE
    """

    cpe_name: Optional[str] = None
    cpe_name_id: Optional[UUID] = None


@dataclass
class CPE(Model):
    """
    Represents a CPE

    Attributes:
        cpe_name: The name of the CPE
        cpe_name_id: UUID of the CPE
        deprecated: True if the CPE is deprecated
        last_modified: Last modification date of the CPE
        created: Creation date of the CPE
        titles: List of titles for the CPE
        refs: References to additional data
        deprecated_by: Additional information about possible deprecation by
            another CPE
    """

    cpe_name: str
    cpe_name_id: UUID
    deprecated: bool
    last_modified: datetime
    created: datetime
    titles: List[Title] = field(default_factory=list)
    refs: List[Reference] = field(default_factory=list)
    deprecated_by: List[DeprecatedBy] = field(default_factory=list)
