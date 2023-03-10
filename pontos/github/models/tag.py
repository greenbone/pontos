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

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from pontos.github.models.base import GitHubModel

__all__ = (
    "GitObjectType",
    "Tag",
    "Tagger",
    "Verification",
    "VerificationReason",
)


class GitObjectType(Enum):
    """
    A git object type

    Attributes:
        COMMIT: A commit object
        TREE: A tree object
        BLOB: A blob object
    """

    COMMIT = "commit"
    TREE = "tree"
    BLOB = "blob"


@dataclass
class GitObject(GitHubModel):
    """
    A GitHub GitObject model

    Attributes:
        sha: The sha (git ID) of the object
        type: Type of the Git object (commit, tree or blob)
        url: URL to the git object
    """

    sha: str
    type: GitObjectType
    url: str


@dataclass
class Tagger(GitHubModel):
    """
    GitHub user who created a tag

    Attributes:
        date: Date of the tag
        email: Email address of the user
        name: Name of the user
    """

    date: datetime
    email: str
    name: str


class VerificationReason(Enum):
    """
    Verification reason details

    Attributes:
        EXPIRED_KEY: Signature key has expired
        NOT_SIGNING_KEY: No signature key available
        GPGVERIFY_ERROR: GPG verification error
        GPGVERIFY_UNAVAILABLE: GPG verification not available
        UNSIGNED: Not signed
        UNKNOWN_SIGNATURE_TYPE: Unknown signature type
        NO_USER: No user
        UNVERIFIED_EMAIL: Email address not verified
        BAD_EMAIL: Bad email address
        UNKNOWN_KEY: Unknown signature key
        MALFORMED_SIGNATURE: Malformed signature
        INVALID: Invalid signature
        VALID: Valid signature
    """

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
    """
    Verification details of a tag

    Attributes:
        verified: True if the tag is verified
        reason: Details of the reason of the verification status
        payload: Payload of the verification
        signature: Signature of the verification
    """

    verified: bool
    reason: VerificationReason
    payload: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class Tag(GitHubModel):
    """
    A GitHub tag model

    Attributes:
        node_id: Node ID of the tag
        tag: The tag name
        sha: The corresponding sha (git ID)
        url: URL to the tag
        message: The git commit message of the tag
        tagger: The creator of the tag
        object: The corresponding git object
        verification: The verification status of the tag
    """

    node_id: str
    tag: str
    sha: str
    url: str
    message: str
    tagger: Tagger
    object: GitObject
    verification: Optional[Verification] = None
