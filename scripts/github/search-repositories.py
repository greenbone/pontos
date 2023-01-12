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

"""
This script search for repositories and prints out all found repositories
"""

import csv
import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from typing import Dict, Iterable, Union

from rich.console import Console
from rich.table import Table

from pontos.github.api import GitHubAsyncRESTApi
from pontos.github.models.search import (
    InDescriptionQualifier,
    InNameQualifier,
    InReadmeQualifier,
    InTopicsQualifier,
    IsPrivateQualifier,
    IsPublicQualifier,
    OrganizationQualifier,
    RepositorySort,
    SortOrder,
    UserQualifier,
)


def lower(value: str) -> str:
    return value.lower()


def order_type(value: Union[str, SortOrder]) -> SortOrder:
    if isinstance(value, SortOrder):
        return value
    try:
        return SortOrder[value.upper()]
    except KeyError:
        raise ArgumentTypeError(f"Invalid value {value}.") from None


def sort_type(value: Union[str, RepositorySort]) -> RepositorySort:
    if isinstance(value, RepositorySort):
        return value
    try:
        return RepositorySort[value.upper()]
    except KeyError:
        raise ArgumentTypeError(f"Invalid value {value}.") from None


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("terms", nargs="+")
    repo_space_group = parser.add_mutually_exclusive_group(required=False)
    repo_space_group.add_argument(
        "--organization",
        help="Restrict the search to the repositories of an organization.",
    )
    repo_space_group.add_argument(
        "--user", help="Restrict the search to the repositories of a user."
    )
    parser.add_argument(
        "--in-name",
        action="store_true",
        help="Search for terms within the repository name.",
    )
    parser.add_argument(
        "--in-description",
        action="store_true",
        help="Search for terms within the repository description.",
    )
    parser.add_argument(
        "--in-readme",
        action="store_true",
        help="Search for terms within the repository description.",
    )
    parser.add_argument(
        "--in-topics",
        action="store_true",
        help="Search for terms within the repository topics.",
    )
    visibility_group = parser.add_mutually_exclusive_group(required=False)
    visibility_group.add_argument(
        "--private",
        action="store_true",
        help="Restrict the search to private repositories only.",
    )
    visibility_group.add_argument(
        "--public",
        action="store_true",
        help="Restrict the search to public repositories only.",
    )
    parser.add_argument(
        "--format",
        choices=["console", "csv"],
        default="console",
        help="Output format. Default: %(default)s",
    )

    parser.add_argument(
        "--columns",
        choices=["name", "description", "url", "visibility"],
        default=["name", "description", "url", "visibility"],
        type=lower,
        nargs="*",
        help="Define columns to print. Default: %(default)s.",
    )
    parser.add_argument(
        "--order",
        type=order_type,
        help="Sort order. Choices: "
        f"{', '.join([o.name for o in SortOrder])}. Default: %(default)s.",
        default=SortOrder.DESC.name,
    )
    parser.add_argument(
        "--sort",
        type=sort_type,
        help="Sort order. Choices: "
        f"{', '.join([o.name for o in RepositorySort])}.",
    )


class Format(ABC):
    def __init__(self, columns: Iterable[str]) -> None:
        self.columns = columns

    @abstractmethod
    def add_row(self, **kwargs: Dict[str, str]) -> None:
        pass

    def finish(self) -> None:
        pass


class CSVFormat(Format):
    def __init__(self, columns: Iterable[str]) -> None:
        super().__init__(columns)
        self.csv_writer = csv.DictWriter(sys.stdout, fieldnames=self.columns)

    def add_row(self, **kwargs: Dict[str, str]) -> None:
        row = {}
        for column in self.columns:
            row[column] = kwargs[column]

        self.csv_writer.writerow(row)


class ConsoleFormat(Format):
    def __init__(self, columns: Iterable[str]) -> None:
        super().__init__(columns)
        self.table = Table()

        for column in self.columns:
            self.table.add_column(column)

    def add_row(self, **kwargs: Dict[str, str]) -> None:
        row = []
        for column in self.columns:
            value = kwargs[column]
            if column == "url":
                value = f"[link={value}]{value}[/link]"

            row.append(value)

        self.table.add_row(*row)

    def finish(self) -> None:
        console = Console()
        console.print(self.table)
        console.print(f"{self.table.row_count} repositories.", highlight=False)


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    if args.format == "console":
        output = ConsoleFormat(args.columns)
    else:
        output = CSVFormat(args.columns)

    qualifiers = []

    if args.public:
        qualifiers.append(IsPublicQualifier())

    if args.private:
        qualifiers.append(IsPrivateQualifier())

    if args.organization:
        qualifiers.append(OrganizationQualifier(args.organization))

    if args.user:
        qualifiers.append(UserQualifier(args.user))

    if args.in_name:
        qualifiers.append(InNameQualifier())

    if args.in_description:
        qualifiers.append(InDescriptionQualifier())

    if args.in_readme:
        qualifiers.append(InReadmeQualifier())

    if args.in_topics:
        qualifiers.append(InTopicsQualifier())

    async for repo in api.search.repositories(
        qualifiers=qualifiers,
        keywords=args.terms,
        order=args.order,
        sort=args.sort,
    ):
        output.add_row(
            name=repo.name,
            description=repo.description,
            url=repo.url,
            visibility=repo.visibility,
        )

    output.finish()

    return 0
