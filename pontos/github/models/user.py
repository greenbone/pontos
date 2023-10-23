# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pontos.github.models.base import GitHubModel


@dataclass
class SSHPublicKey(GitHubModel):
    """
    A public SSH key of a user

    Attributes:
        id: ID of the SSH key
        key: SSH Key
    """

    id: int
    key: str


@dataclass
class SSHPublicKeyExtended(GitHubModel):
    """
    Extended details of public SSH key of a user

    Attributes:
        id: ID of the SSH key
        key: SSH Key
        url:
        title:
        created_at
        verified:
        read_only:
    """

    id: int
    key: str
    url: str
    title: str
    created_at: datetime
    verified: bool
    read_only: bool


@dataclass
class EmailInformation(GitHubModel):
    """
    Information about an email address stored in GitHub

    Attributes:
        email: The email address
        primary: True if it is the primary email address of the user
        verified: True if the email address is verified
        visibility: public, private
    """

    email: str
    primary: bool
    verified: bool
    # visibility should be an enum but the schema didn't define the possible
    # values. therefore be safe and just use a str
    visibility: Optional[str] = None
