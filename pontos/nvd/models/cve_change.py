# Copyright (C) 2023 Greenbone AG
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


from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pontos.models import Model


class EventName(str, Enum):
    INITAL_ANALYSIS = "Initial Analysis"
    REANALYSIS = "Reanalysis"
    CVE_MODIFIED = "CVE Modified"
    MODIFIED_ANALYSIS = "Modified Analysis"
    CVE_TRANSLATED = "CVE Translated"
    VENDOR_COMMENT = "Vendor Comment"
    CVE_SOURCE_UPDATE = "CVE Source Update"
    CPE_DEPRECATION_REMAP = "CPE Deprecation Remap"
    CWE_REMAP = "CWE Remap"
    CVE_REJECTED = "CVE Rejected"
    CVE_UNREJECT = "CVE Unreject"

    def __str__(self) -> str:
        return self.value


@dataclass
class Detail:
    type: str
    action: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None


@dataclass
class CVEChange(Model):
    cve_id: str
    event_name: EventName
    cve_change_id: UUID
    source_identifier: str
    created: Optional[datetime] = None
    details: Optional[List[Detail]] = None
