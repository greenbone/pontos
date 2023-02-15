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
from typing import Optional, Type

import httpx

from pontos.github.api.artifacts import GitHubAsyncRESTArtifacts
from pontos.github.api.branch import GitHubAsyncRESTBranches
from pontos.github.api.client import GitHubAsyncRESTClient
from pontos.github.api.contents import GitHubAsyncRESTContent
from pontos.github.api.helper import (
    DEFAULT_GITHUB_API_URL,
    DEFAULT_TIMEOUT_CONFIG,
)
from pontos.github.api.labels import GitHubAsyncRESTLabels
from pontos.github.api.organizations import GitHubAsyncRESTOrganizations
from pontos.github.api.pull_requests import GitHubAsyncRESTPullRequests
from pontos.github.api.release import GitHubAsyncRESTReleases
from pontos.github.api.repositories import GitHubAsyncRESTRepositories
from pontos.github.api.search import GitHubAsyncRESTSearch
from pontos.github.api.tags import GitHubAsyncRESTTags
from pontos.github.api.teams import GitHubAsyncRESTTeams
from pontos.github.api.workflows import GitHubAsyncRESTWorkflows


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
