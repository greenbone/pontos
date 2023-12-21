# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pontos.github.models.base import GitHubModel
from pontos.models import StrEnum

__all__ = (
    "GitObjectType",
    "Tag",
    "Tagger",
    "Verification",
    "VerificationReason",
)


class GitObjectType(StrEnum):
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


class VerificationReason(StrEnum):
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


@dataclass
class Commit(GitHubModel):
    """
    A GitHub commit model, storing URL and SHA of a commit

    Attributes:
        sha: Commits SHA hash
        url: Commits URL
    """

    sha: str
    url: str


@dataclass
class RepositoryTag(GitHubModel):
    """
    A GitHub tag model, when accessing all tags of a repository

    Attributes:
        node_id: Node ID of the tag
        name: The tag name
        zipball_url: Link to the tags zip ball content
        tarball_url: Link to the tags tar ball content
        commit: SHA and URL to the commit the tag points to
    """

    node_id: str
    name: str
    zipball_url: str
    tarball_url: str
    commit: Commit
