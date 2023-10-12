# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later


from typing import AsyncIterator, Optional, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.base import SortOrder
from pontos.github.models.dependabot import (
    AlertSort,
    AlertState,
    DependabotAlert,
    DependencyScope,
    DismissedReason,
    Severity,
)
from pontos.helper import enum_or_value


class GitHubAsyncRESTDependabot(GitHubAsyncREST):
    async def _alerts(
        self,
        api: str,
        *,
        state: Union[AlertState, str, None] = None,
        severity: Union[Severity, str, None] = None,
        ecosystem: Optional[str] = None,
        packages: Optional[list[str]] = None,
        scope: Union[DependencyScope, str, None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[DependabotAlert]:
        params = {"per_page": "100"}

        if state:
            params["state"] = enum_or_value(state)
        if severity:
            params["severity"] = enum_or_value(severity)
        if ecosystem:
            params["ecosystem"] = ecosystem
        if packages:
            # as per REST api docu this param is passed as package (singular!)
            params["package"] = ",".join(packages)
        if scope:
            params["scope"] = enum_or_value(scope)
        if sort:
            params["sort"] = enum_or_value(sort)
        if direction:
            params["direction"] = enum_or_value(direction)

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for alert in response.json():
                yield DependabotAlert.from_dict(alert)

    async def enterprise_alerts(
        self,
        enterprise: str,
        *,
        state: Union[AlertState, str, None] = None,
        severity: Union[Severity, str, None] = None,
        ecosystem: Optional[str] = None,
        packages: Optional[list[str]] = None,
        scope: Union[DependencyScope, str, None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[DependabotAlert]:
        """
        Get the list of dependabot alerts for all repositories of a GitHub
        enterprise

        https://docs.github.com/en/rest/dependabot/alerts#list-dependabot-alerts-for-an-enterprise

        Args:
            enterprise: Name of the enterprise
            state: Filter alerts by state
            severity: Filter alerts by severity
            ecosystem: Filter alerts by package ecosystem
            package: Return alerts only for the provided packages
            scope: Filter alerts by scope of the vulnerable dependency
            sort: The property by which to sort the results. Default is to sort
                alerts by creation date.
            direction: The direction to sort the results by. Default is desc.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the dependabot alerts

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for alert in api.dependabot.enterprise_alerts(
                        "my-enterprise"
                    ):
                        print(alert)
        """

        api = f"/enterprises/{enterprise}/dependabot/alerts"
        async for alert in self._alerts(
            api,
            state=state,
            severity=severity,
            ecosystem=ecosystem,
            packages=packages,
            scope=scope,
            sort=sort,
            direction=direction,
        ):
            yield alert

    async def organization_alerts(
        self,
        organization: str,
        *,
        state: Union[AlertState, str, None] = None,
        severity: Union[Severity, str, None] = None,
        ecosystem: Optional[str] = None,
        packages: Optional[list[str]] = None,
        scope: Union[DependencyScope, str, None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[DependabotAlert]:
        """
        Get the list of dependabot alerts for all repositories of a GitHub
        organization

        https://docs.github.com/en/rest/dependabot/alerts#list-dependabot-alerts-for-an-organization

        Args:
            organization: Name of the organization
            state: Filter alerts by state
            severity: Filter alerts by severity
            ecosystem: Filter alerts by package ecosystem
            package: Return alerts only for the provided packages
            scope: Filter alerts by scope of the vulnerable dependency
            sort: The property by which to sort the results. Default is to sort
                alerts by creation date.
            direction: The direction to sort the results by. Default is desc.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the dependabot alerts

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for alert in api.dependabot.organization_alerts(
                        "my-enterprise"
                    ):
                        print(alert)
        """
        api = f"/orgs/{organization}/dependabot/alerts"

        async for alert in self._alerts(
            api,
            state=state,
            severity=severity,
            ecosystem=ecosystem,
            packages=packages,
            scope=scope,
            sort=sort,
            direction=direction,
        ):
            yield alert

    async def alerts(
        self,
        repo: str,
        *,
        state: Union[AlertState, str, None] = None,
        severity: Union[Severity, str, None] = None,
        ecosystem: Optional[str] = None,
        packages: Optional[list[str]] = None,
        scope: Union[DependencyScope, str, None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[DependabotAlert]:
        """
        Get the list of dependabot alerts for a repository

        https://docs.github.com/en/rest/dependabot/alerts#list-dependabot-alerts-for-a-repository

        Args:
            repo: GitHub repository (owner/name)
            state: Filter alerts by state
            severity: Filter alerts by severity
            ecosystem: Filter alerts by package ecosystem
            package: Return alerts only for the provided packages
            scope: Filter alerts by scope of the vulnerable dependency
            sort: The property by which to sort the results. Default is to sort
                alerts by creation date.
            direction: The direction to sort the results by. Default is desc.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the dependabot alerts

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for alert in api.dependabot.alerts(
                        "my-enterprise"
                    ):
                        print(alert)
        """
        api = f"/repos/{repo}/dependabot/alerts"

        async for alert in self._alerts(
            api,
            state=state,
            severity=severity,
            ecosystem=ecosystem,
            packages=packages,
            scope=scope,
            sort=sort,
            direction=direction,
        ):
            yield alert

    async def alert(
        self,
        repo: str,
        alert_number: Union[str, int],
    ) -> DependabotAlert:
        """
        Get a single dependabot alert

        https://docs.github.com/en/rest/dependabot/alerts#get-a-dependabot-alert

        Args:
            repo: GitHub repository (owner/name)
            alert_number: The number that identifies a Dependabot alert in its
                repository

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Dependabot alert information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    alert = await api.dependabot.alert("foo/bar", 123)
        """
        api = f"/repos/{repo}/dependabot/alerts/{alert_number}"
        response = await self._client.get(api)
        response.raise_for_status()
        return DependabotAlert.from_dict(response.json())

    async def update_alert(
        self,
        repo: str,
        alert_number: Union[str, int],
        state: Union[AlertState, str],
        *,
        dismissed_reason: Union[DismissedReason, str, None] = None,
        dismissed_comment: str,
    ) -> DependabotAlert:
        """
        Update a single dependabot alert

        https://docs.github.com/en/rest/dependabot/alerts#update-a-dependabot-alert

        Args:
            repo: GitHub repository (owner/name)
            alert_number: The number that identifies a Dependabot alert in its
                repository
            state: The state of the Dependabot alert
            dismissed_reason: Required when state is dismissed. A reason for
                dismissing the alert.
            dismissed_comment: An optional comment associated with dismissing
                the alert

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Dependabot alert information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    alert = await api.dependabot.update(
                        "foo/bar",
                        123,
                        AlertState.FIXED,
                    )
        """
        api = f"/repos/{repo}/dependabot/alerts/{alert_number}"

        data = {"state": enum_or_value(state)}
        if dismissed_comment:
            data["dismissed_comment"] = dismissed_comment
        if dismissed_reason:
            data["dismissed_reason"] = enum_or_value(dismissed_reason)

        response = await self._client.patch(api, data=data)
        response.raise_for_status()
        return DependabotAlert.from_dict(response.json())
