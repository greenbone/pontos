# SPDX-FileCopyrightText: 2022-2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field
from datetime import datetime

from pontos.models import Model


@dataclass
class AcceptanceLevel(Model):
    description: str
    last_modified: datetime


@dataclass
class Source(Model):
    last_modified: datetime
    created: datetime
    name: str | None = None
    source_identifiers: list[str] = field(default_factory=list)
    contact_email: str | None = None
    v2_acceptance_level: AcceptanceLevel | None = None
    v3_acceptance_level: AcceptanceLevel | None = None
    cwe_acceptance_level: AcceptanceLevel | None = None
