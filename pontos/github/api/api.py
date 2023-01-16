# Copyright (C) 2022 - 2023 Greenbone Networks GmbH
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

from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Callable, Dict, Iterable, Iterator, Optional, Type

import httpx

from pontos.github.api.artifacts import (
    GitHubAsyncRESTArtifacts,
    GitHubRESTArtifactsMixin,
)
from pontos.github.api.branch import (
    GitHubAsyncRESTBranches,
    GitHubRESTBranchMixin,
)
from pontos.github.api.client import GitHubAsyncRESTClient
from pontos.github.api.contents import (
    GitHubAsyncRESTContent,
    GitHubRESTContentMixin,
)
from pontos.github.api.helper import (
    DEFAULT_GITHUB_API_URL,
    DEFAULT_TIMEOUT_CONFIG,
    JSON,
    JSON_OBJECT,
    _get_next_url,
)
from pontos.github.api.labels import (
    GitHubAsyncRESTLabels,
    GitHubRESTLabelsMixin,
)
from pontos.github.api.organizations import (
    GitHubAsyncRESTOrganizations,
    GitHubRESTOrganizationsMixin,
)
from pontos.github.api.pull_requests import (
    GitHubAsyncRESTPullRequests,
    GitHubRESTPullRequestsMixin,
)
from pontos.github.api.release import (
    GitHubAsyncRESTReleases,
    GitHubRESTReleaseMixin,
)
from pontos.github.api.repositories import GitHubAsyncRESTRepositories
from pontos.github.api.search import GitHubAsyncRESTSearch
from pontos.github.api.tags import GitHubAsyncRESTTags
from pontos.github.api.teams import GitHubAsyncRESTTeams
from pontos.github.api.workflows import (
    GitHubAsyncRESTWorkflows,
    GitHubRESTWorkflowsMixin,
)


class GitHubAsyncRESTApi(AbstractAsyncContextManager):
    """
    A asynchronous GitHub REST API

    Example:
        .. code-block:: python

            with GitHubAsyncRESTApi(token) as api:
                repositories = await api.organizations.get_repositories("foo")
    """

    def __init__(
        self,
        token: Optional[str] = None,
        url: Optional[str] = DEFAULT_GITHUB_API_URL,
        *,
        timeout: Optional[httpx.Timeout] = DEFAULT_TIMEOUT_CONFIG,
    ) -> None:
        self._client = GitHubAsyncRESTClient(token, url, timeout=timeout)

    @property
    def organizations(self) -> GitHubAsyncRESTOrganizations:
        """
        Organizations related API
        """
        return GitHubAsyncRESTOrganizations(self._client)

    @property
    def artifacts(self) -> GitHubAsyncRESTArtifacts:
        """
        Artifacts related API
        """
        return GitHubAsyncRESTArtifacts(self._client)

    @property
    def branches(self) -> GitHubAsyncRESTBranches:
        """
        Branches related API

        """
        return GitHubAsyncRESTBranches(self._client)

    @property
    def contents(self) -> GitHubAsyncRESTContent:
        """
        Contents related API

        """
        return GitHubAsyncRESTContent(self._client)

    @property
    def labels(self) -> GitHubAsyncRESTLabels:
        """
        Labels related API

        """
        return GitHubAsyncRESTLabels(self._client)

    @property
    def pulls(self) -> GitHubAsyncRESTPullRequests:
        """
        Pull Requests related API

        """
        return GitHubAsyncRESTPullRequests(self._client)

    @property
    def releases(self) -> GitHubAsyncRESTReleases:
        """
        Releases related API

        """
        return GitHubAsyncRESTReleases(self._client)

    @property
    def workflows(self) -> GitHubAsyncRESTWorkflows:
        """
        Workflows related API

        """
        return GitHubAsyncRESTWorkflows(self._client)

    @property
    def repositories(self) -> GitHubAsyncRESTRepositories:
        """
        Repositories related API

        """
        return GitHubAsyncRESTRepositories(self._client)

    @property
    def teams(self) -> GitHubAsyncRESTTeams:
        """
        Teams related API
        """
        return GitHubAsyncRESTTeams(self._client)

    @property
    def tags(self) -> GitHubAsyncRESTTags:
        """
        Tags related API
        """
        return GitHubAsyncRESTTags(self._client)

    @property
    def search(self) -> GitHubAsyncRESTSearch:
        """
        Search related API
        """
        return GitHubAsyncRESTSearch(self._client)

    async def __aenter__(self) -> "GitHubAsyncRESTApi":
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        return await self._client.__aexit__(exc_type, exc_value, traceback)


class GitHubRESTApi(
    GitHubRESTArtifactsMixin,
    GitHubRESTBranchMixin,
    GitHubRESTContentMixin,
    GitHubRESTLabelsMixin,
    GitHubRESTOrganizationsMixin,
    GitHubRESTPullRequestsMixin,
    GitHubRESTReleaseMixin,
    GitHubRESTWorkflowsMixin,
):
    """GitHubRESTApi Mixin"""

    def __init__(
        self,
        token: Optional[str] = None,
        url: Optional[str] = DEFAULT_GITHUB_API_URL,
        *,
        timeout: httpx.Timeout = DEFAULT_TIMEOUT_CONFIG,
    ) -> None:
        self.token = token
        self.url = url
        self.timeout = timeout

    def _request_headers(
        self, *, content_type: Optional[str] = None
    ) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        if content_type:
            headers["Content-Type"] = content_type

        return headers

    def _request_kwargs(self, *, data, content) -> Dict[str, str]:
        kwargs = {}
        if data is not None:
            kwargs["json"] = data
        if content is not None:
            kwargs["content"] = content
        return kwargs

    def _request_internal(
        self,
        url: str,
        *,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, str]] = None,
        content: Optional[bytes] = None,
        request: Optional[Callable] = None,
        content_type: Optional[str] = None,
    ) -> httpx.Response:
        request = request or httpx.get
        headers = self._request_headers(content_type=content_type)
        kwargs = self._request_kwargs(data=data, content=content)
        return request(
            url,
            headers=headers,
            params=params,
            follow_redirects=True,
            timeout=self.timeout,
            **kwargs,
        )

    def _request_api_url(self, api) -> str:
        return f"{self.url}{api}"

    def _request(
        self,
        api: str,
        *,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, str]] = None,
        request: Optional[Callable] = None,
    ) -> httpx.Response:
        return self._request_internal(
            self._request_api_url(api),
            params=params,
            data=data,
            request=request,
        )

    def _request_all(
        self,
        api: str,
        *,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, str]] = None,
        request: Optional[Callable] = None,
    ) -> Iterator[JSON]:
        response: httpx.Response = self._request(
            api, params=params, data=data, request=request
        )

        yield from response.json()

        next_url = _get_next_url(response)

        while next_url:
            response = self._request_internal(
                next_url, params=params, data=data, request=request
            )

            yield from response.json()

            next_url = _get_next_url(response)

        return data

    def _get_paged_items(
        self, api: str, key: str, *, params: Optional[JSON_OBJECT] = None
    ) -> Iterable[JSON_OBJECT]:
        """
        Internal method to get the paged items information from different REST
        URLs.
        """
        page = 1
        per_page = 100
        params = params or {}
        params.update({"per_page": per_page, "page": page})

        response: httpx.Response = self._request(
            api, request=httpx.get, params=params
        )
        response.raise_for_status()

        json = response.json()
        total = json.get("total_count", 0)
        items = json[key]
        downloaded = len(items)

        while total - downloaded > 0:
            page += 1
            params = {"per_page": per_page, "page": page}

            response = self._request(api, request=httpx.get, params=params)
            response.raise_for_status()

            json = response.json()
            items.extend(json[key])
            downloaded = len(items)

        return items
