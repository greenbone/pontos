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

from typing import AsyncIterator, Iterable, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.organization import Repository
from pontos.github.models.search import Qualifier, RepositorySort, SortOrder
from pontos.helper import enum_or_value


class GitHubAsyncRESTSearch(GitHubAsyncREST):
    async def repositories(
        self,
        *,
        keywords: Iterable[str],
        qualifiers: Iterable[Qualifier],
        order: Union[str, SortOrder] = SortOrder.DESC,
        sort: Union[str, RepositorySort, None] = None,
    ) -> AsyncIterator[Repository]:
        """
        Search for repositories

        https://docs.github.com/en/rest/search#search-repositories

        https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories

        Args:
            keywords: List of keywords to search for.
            qualifiers: List of qualifiers.
            order: Sort order either 'asc' or 'desc'. Default is 'desc'.
            sort: Sort the found repositories by this criteria.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = "/search/repositories"
        params = {
            "per_page": "100",
        }
        if order:
            params["order"] = enum_or_value(order)
        if sort:
            params["sort"] = enum_or_value(sort)

        query = (
            f"{' '.join(keywords)} "
            f"{' '.join([str(qualifier) for qualifier in qualifiers])}"
        )
        params["q"] = query

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()
            data = response.json()
            for repo in data["items"]:
                yield Repository.from_dict(repo)
