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

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from pontos.github.models.base import GitHubModel

__all__ = (
    "GitObjectType",
    "Tag",
    "VerificationReason",
)


class GitObjectType(Enum):
    COMMIT = "commit"
    TREE = "tree"
    BLOB = "blob"


@dataclass
class GitObject(GitHubModel):
    sha: str
    type: GitObjectType
    url: str


@dataclass
class Tagger(GitHubModel):
    date: datetime
    email: str
    name: str


class VerificationReason(Enum):
    EXPIRED_KEY = "expired_key"
    NOT_SIGNING_KEY = "not_signing_key"
    GPGVERIFY_ERROR = "gpgverify_error"
    GPGVERIFY_UNAVAILABLE = "gpgverify_unavailable"
    UNSIGNED = "unsigned"
    UNKNOWN_SIGNATURE_TYPE = "unknown_signature_type"
    NO_USER = "no_user"
    UNVERIFIED_EMAIL = "unverified_email"
    BAD_EMAIL = "bad_email"
    UNKNOWN_KEY = "unknown_key"
    MALFORMED_SIGNATURE = "malformed_signature"
    INVALID = "invalid"
    VALID = "valid"


@dataclass
class Verification(GitHubModel):
    verified: bool
    reason: VerificationReason
    payload: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class Tag(GitHubModel):
    node_id: str
    tag: str
    sha: str
    url: str
    message: str
    tagger: Tagger
    object: GitObject
    verification: Optional[Verification] = None
