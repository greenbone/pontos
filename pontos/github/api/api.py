# Copyright (C) 2022 - 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Optional, Type

import httpx

from pontos.github.api.artifacts import GitHubAsyncRESTArtifacts
from pontos.github.api.billing import GitHubAsyncRESTBilling
from pontos.github.api.branch import GitHubAsyncRESTBranches
from pontos.github.api.client import GitHubAsyncRESTClient
from pontos.github.api.code_scanning import GitHubAsyncRESTCodeScanning
from pontos.github.api.contents import GitHubAsyncRESTContent
from pontos.github.api.dependabot import GitHubAsyncRESTDependabot
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
from pontos.github.api.secret_scanning import GitHubAsyncRESTSecretScanning
from pontos.github.api.tags import GitHubAsyncRESTTags
from pontos.github.api.teams import GitHubAsyncRESTTeams
from pontos.github.api.users import GitHubAsyncRESTUsers
from pontos.github.api.workflows import GitHubAsyncRESTWorkflows
from pontos.helper import deprecated


class GitHubAsyncRESTApi(AbstractAsyncContextManager):
    """
    A asynchronous GitHub REST API.

    Should be used as an async context manager.

    Example:
        .. code-block:: python

            from pontos.github.api import GitHubAsyncRESTApi

            async with GitHubAsyncRESTApi(token) as api:
                repositories = await api.organizations.get_repositories("foo")
    """

    def __init__(
        self,
        token: Optional[str] = None,
        url: Optional[str] = DEFAULT_GITHUB_API_URL,
        *,
        timeout: Optional[httpx.Timeout] = DEFAULT_TIMEOUT_CONFIG,
    ) -> None:
        """
        Args:
            token: GitHub API token
            url: GitHub URL
            timeout: Timeout settings to use
        """
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
    def billing(self) -> GitHubAsyncRESTBilling:
        """
        Billing related API
        """
        return GitHubAsyncRESTBilling(self._client)

    @property
    def branches(self) -> GitHubAsyncRESTBranches:
        """
        Branches related API
        """
        return GitHubAsyncRESTBranches(self._client)

    @property
    def code_scanning(self) -> GitHubAsyncRESTCodeScanning:
        """
        Code scanning related API
        """
        return GitHubAsyncRESTCodeScanning(self._client)

    @property
    def contents(self) -> GitHubAsyncRESTContent:
        """
        Contents related API
        """
        return GitHubAsyncRESTContent(self._client)

    @property
    def dependabot(self) -> GitHubAsyncRESTDependabot:
        """
        Dependabot related API
        """
        return GitHubAsyncRESTDependabot(self._client)

    @property
    def labels(self) -> GitHubAsyncRESTLabels:
        """
        Labels related API
        """
        return GitHubAsyncRESTLabels(self._client)

    @property
    @deprecated(
        since="23.3.4",
        reason="The pulls property is obsolete. Please use pull_requests "
        "instead.",
    )
    def pulls(self) -> GitHubAsyncRESTPullRequests:
        """
        Pull Requests related API

        .. deprecated:: 23.3.4

            Use :py:attr:`pull_requests` instead.
        """
        return GitHubAsyncRESTPullRequests(self._client)

    @property
    def pull_requests(self) -> GitHubAsyncRESTPullRequests:
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
    def secret_scanning(self) -> GitHubAsyncRESTSecretScanning:
        """
        Secret scanning related API
        """
        return GitHubAsyncRESTSecretScanning(self._client)

    @property
    def search(self) -> GitHubAsyncRESTSearch:
        """
        Search related API
        """
        return GitHubAsyncRESTSearch(self._client)

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
    def users(self) -> GitHubAsyncRESTUsers:
        """
        Users related API
        """
        return GitHubAsyncRESTUsers(self._client)

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
