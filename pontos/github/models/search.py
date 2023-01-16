# Copyright (C) 2023 Greenbone Networks GmbH
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

__all__ = (
    "InDescriptionQualifier",
    "InNameQualifier",
    "InReadmeQualifier",
    "InTopicsQualifier",
    "IsPrivateQualifier",
    "IsPublicQualifier",
    "NotQualifier",
    "OrganizationQualifier",
    "Qualifier",
    "RepositoryQualifier",
    "RepositorySort",
    "SortOrder",
    "UserQualifier",
)

from abc import ABC
from enum import Enum


class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class RepositorySort(Enum):
    STARS = "stars"
    FORKS = "forks"
    HELP_WANTED_ISSUES = "help-wanted-issues"
    UPDATED = "updated"


class Qualifier(ABC):
    operator: str
    term: str

    def __str__(self) -> str:
        """ """
        return f"{self.operator}:{self.term}"


class NotQualifier(Qualifier):
    def __init__(self, qualifier: Qualifier) -> None:
        self.qualifier = qualifier

    def __str__(self) -> str:
        return f"-{str(self.qualifier)}"


class InQualifier(Qualifier):
    operator = "in"


class InNameQualifier(InQualifier):
    term = "name"


class InDescriptionQualifier(InQualifier):
    term = "description"


class InTopicsQualifier(InQualifier):
    term = "topics"


class InReadmeQualifier(InQualifier):
    term = "readme"


class RepositoryQualifier(Qualifier):
    operator = "repo"

    def __init__(self, repository: str) -> None:
        """
        Search within a repository

        Args:
            repository: owner/repo
        """
        self.term = repository


class OrganizationQualifier(Qualifier):
    operator = "org"

    def __init__(self, organization: str) -> None:
        """
        Search within an organization

        Args:
            organization: Name of the organization to search within
        """
        self.term = organization


class UserQualifier(Qualifier):
    operator = "user"

    def __init__(self, user: str) -> None:
        """
        Search within an user space

        Args:
            user: Name of the user
        """
        self.term = user


class IsPublicQualifier(Qualifier):
    operator = "is"
    term = "public"


class IsPrivateQualifier(Qualifier):
    operator = "is"
    term = "private"
