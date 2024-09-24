# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from dataclasses import dataclass, field

from pontos.github.models.base import GitHubModel, User
from pontos.github.models.organization import Repository
from pontos.models import StrEnum

__all__ = [
    "PackageType",
    "PackageVisibility",
    "Package",
    "Container",
    "PackageVersionMetadata",
    "PackageVersion",
]


class PackageType(StrEnum):
    CONTAINER = "container"
    DOCKER = "docker"
    MAVEN = "maven"
    NPM = "npm"
    NUGET = "nuget"
    RUBYGEMS = "rubygems"


class PackageVisibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


@dataclass
class Package(GitHubModel):
    id: int
    name: str
    package_type: PackageType
    owner: User
    version_count: int
    visibility: PackageVisibility
    url: str
    created_at: str
    updated_at: str
    repository: Repository
    html_url: str


@dataclass
class Container(GitHubModel):
    tags: list[str] = field(default_factory=list)


@dataclass
class PackageVersionMetadata(GitHubModel):
    package_type: PackageType
    container: Container


@dataclass
class PackageVersion(GitHubModel):
    id: int
    name: str
    url: str
    package_html_url: str
    created_at: str
    updated_at: str
    html_url: str
    metadata: PackageVersionMetadata
