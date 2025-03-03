# SPDX-FileCopyrightText: 2022-2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from pontos.models import Model


@dataclass
class AcceptanceLevel(Model):
    description: str
    last_modified: datetime


@dataclass
class Source(Model):
    last_modified: datetime
    created: datetime
    name: Optional[str] = None
    source_identifiers: List[str] = field(default_factory=list)
    contact_email: Optional[str] = None
    v2_acceptance_level: Optional[AcceptanceLevel] = None
    v3_acceptance_level: Optional[AcceptanceLevel] = None
    cwe_acceptance_level: Optional[AcceptanceLevel] = None
