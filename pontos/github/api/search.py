# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

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
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            An async iterator yielding repositories

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi
                from pontos.github.models import (
                    InReadmeQualifier,
                    InTopicsQualifier,
                )

                async with GitHubAsyncRESTApi(token) as api:
                    # search for keywords in repo topics and READMEs
                    async for repo in api.search(
                        keywords=["utils", "search", "golang"],
                        qualifier=[
                            InTopicsQualifier(),
                            InReadmeQualifier(),
                        ],
                    )
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
