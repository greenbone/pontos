# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from pontos.models import Model, StrEnum


class EventName(StrEnum):
    CVE_RECEIVED = "CVE Received"
    INITIAL_ANALYSIS = "Initial Analysis"
    REANALYSIS = "Reanalysis"
    CVE_MODIFIED = "CVE Modified"
    MODIFIED_ANALYSIS = "Modified Analysis"
    CVE_TRANSLATED = "CVE Translated"
    VENDOR_COMMENT = "Vendor Comment"
    CVE_SOURCE_UPDATE = "CVE Source Update"
    CPE_DEPRECATION_REMAP = "CPE Deprecation Remap"
    CWE_REMAP = "CWE Remap"
    CVE_REJECTED = "CVE Rejected"
    CVE_UNREJECTED = "CVE Unrejected"


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
    details: Optional[list[Detail]] = None
