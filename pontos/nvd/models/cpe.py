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
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pontos.models import Model


@dataclass
class Title(Model):
    title: str
    lang: str


class ReferenceType(Enum):
    ADVISORY = "Advisory"
    CHANGELOG = "Change Log"
    PRODUCT = "Product"
    PROJECT = "Project"
    VENDOR = "Vendor"
    VERSION = "Version"


@dataclass
class Reference(Model):
    ref: str
    type: Optional[ReferenceType] = None


@dataclass
class DeprecatedBy(Model):
    cpe_name: Optional[str] = None
    cpe_name_id: Optional[str] = None


@dataclass
class CPE(Model):
    cpe_name: str
    cpe_name_id: str
    deprecated: bool
    last_modified: datetime
    created: datetime
    titles: List[Title] = field(default_factory=list)
    refs: List[Reference] = field(default_factory=list)
    deprecated_by: List[DeprecatedBy] = field(default_factory=list)
