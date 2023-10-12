# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import AsyncIterator, Iterable, Optional, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.base import SortOrder
from pontos.github.models.secret_scanning import (
    AlertLocation,
    AlertSort,
    AlertState,
    CommitLocation,
    IssueBodyLocation,
    IssueCommentLocation,
    IssueTitleLocation,
    LocationType,
    Resolution,
    SecretScanningAlert,
)
from pontos.helper import enum_or_value


class GitHubAsyncRESTSecretScanning(GitHubAsyncREST):
    async def _alerts(
        self,
        api: str,
        *,
        state: Union[AlertState, str, None] = None,
        secret_types: Union[Iterable[str], None] = None,
        resolutions: Union[Iterable[str], None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[SecretScanningAlert]:
        params = {"per_page": "100"}

        if state:
            params["state"] = enum_or_value(state)
        if secret_types:
            # as per REST api docu this param is passed as secret_type
            params["secret_type"] = ",".join(secret_types)
        if resolutions:
            # as per REST api docu this param is passed as resolution
            params["resolution"] = ",".join(resolutions)
        if sort:
            params["sort"] = enum_or_value(sort)
        if direction:
            params["direction"] = enum_or_value(direction)

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for alert in response.json():
                yield SecretScanningAlert.from_dict(alert)

    async def enterprise_alerts(
        self,
        enterprise: str,
        *,
        state: Union[AlertState, str, None] = None,
        secret_types: Union[Iterable[str], None] = None,
        resolutions: Union[Iterable[str], None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[SecretScanningAlert]:
        """
        Get the list of secret scanning alerts for all repositories of a GitHub
        enterprise

        https://docs.github.com/en/rest/secret-scanning/secret-scanning#list-secret-scanning-alerts-for-an-enterprise

        Args:
            enterprise: Name of the enterprise
            state: Filter alerts by state
            secret_types: List of secret types to return.
            resolutions: List secret scanning alerts with one of these provided
                resolutions
            sort: The property by which to sort the results. Default is to sort
                alerts by creation date.
            direction: The direction to sort the results by. Default is desc.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the secret scanning alerts

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for alert in api.secret_scanning.enterprise_alerts(
                        "my-enterprise"
                    ):
                        print(alert)
        """

        api = f"/enterprises/{enterprise}/secret-scanning/alerts"
        async for alert in self._alerts(
            api,
            state=state,
            secret_types=secret_types,
            resolutions=resolutions,
            sort=sort,
            direction=direction,
        ):
            yield alert

    async def organization_alerts(
        self,
        organization: str,
        *,
        state: Union[AlertState, str, None] = None,
        secret_types: Union[Iterable[str], None] = None,
        resolutions: Union[Iterable[str], None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[SecretScanningAlert]:
        """
        Get the list of secret scanning alerts for all repositories of a GitHub
        organization

        https://docs.github.com/en/rest/secret-scanning/secret-scanning#list-secret-scanning-alerts-for-an-organization

        Args:
            organization: Name of the organization
            state: Filter alerts by state
            secret_types: List of secret types to return.
            resolutions: List secret scanning alerts with one of these provided
                resolutions
            sort: The property by which to sort the results. Default is to sort
                alerts by creation date.
            direction: The direction to sort the results by. Default is desc.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the secret scanning alerts

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for alert in api.secret_scanning.organization_alerts(
                        "my-org"
                    ):
                        print(alert)
        """

        api = f"/orgs/{organization}/secret-scanning/alerts"
        async for alert in self._alerts(
            api,
            state=state,
            secret_types=secret_types,
            resolutions=resolutions,
            sort=sort,
            direction=direction,
        ):
            yield alert

    async def alerts(
        self,
        repo: str,
        *,
        state: Union[AlertState, str, None] = None,
        secret_types: Union[Iterable[str], None] = None,
        resolutions: Union[Iterable[str], None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[SecretScanningAlert]:
        """
        Get the list of secret scanning alerts for a repository

        https://docs.github.com/en/rest/secret-scanning/secret-scanning#list-secret-scanning-alerts-for-a-repository

        Args:
            repo: GitHub repository (owner/name)
            state: Filter alerts by state
            secret_types: List of secret types to return.
            resolutions: List secret scanning alerts with one of these provided
                resolutions
            sort: The property by which to sort the results. Default is to sort
                alerts by creation date.
            direction: The direction to sort the results by. Default is desc.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the secret scanning alerts

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for alert in api.secret_scanning.alerts(
                        "my-org/my-repo"
                    ):
                        print(alert)
        """

        api = f"/repos/{repo}/secret-scanning/alerts"
        async for alert in self._alerts(
            api,
            state=state,
            secret_types=secret_types,
            resolutions=resolutions,
            sort=sort,
            direction=direction,
        ):
            yield alert

    async def alert(
        self,
        repo: str,
        alert_number: Union[str, int],
    ) -> SecretScanningAlert:
        """
        Get a single secret scanning alert

        https://docs.github.com/en/rest/secret-scanning/secret-scanning#get-a-secret-scanning-alert

        Args:
            repo: GitHub repository (owner/name)
            alert_number: The number that identifies a secret scanning alert in
                its repository

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Secret scanning alert information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    alert = await api.secret_scanning.alert("foo/bar", 123)
        """
        api = f"/repos/{repo}/secret-scanning/alerts/{alert_number}"
        response = await self._client.get(api)
        response.raise_for_status()
        return SecretScanningAlert.from_dict(response.json())

    async def update_alert(
        self,
        repo: str,
        alert_number: Union[str, int],
        state: Union[AlertState, str],
        *,
        resolution: Union[Resolution, str, None] = None,
        resolution_comment: Optional[str] = None,
    ) -> SecretScanningAlert:
        """
        Update a single secret scanning alert

        https://docs.github.com/en/rest/secret-scanning/secret-scanning#update-a-secret-scanning-alert

        Args:
            repo: GitHub repository (owner/name)
            alert_number: The number that identifies a secret scanning alert in
                its repository
            state: The state of the alert
            resolution: Required when the state is resolved. The reason for
                resolving the alert
            resolution_comment: An optional comment when closing an alert.
                Cannot be updated or deleted.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Secret scanning alert information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi
                from pontos.github.models.secret_scanning import (
                    AlertState,
                    Resolution,
                )

                async with GitHubAsyncRESTApi(token) as api:
                    alert = await api.secret_scanning.update_alert(
                        "foo/bar",
                        123,
                        AlertState.RESOLVED,
                        resolution=Resolution.WONT_FIX,
                        resolution_comment="Not applicable",
                    )
        """
        api = f"/repos/{repo}/secret-scanning/alerts/{alert_number}"

        data = {"state": enum_or_value(state)}
        if resolution:
            data["resolution"] = enum_or_value(resolution)
        if resolution_comment:
            data["resolution_comment"] = resolution_comment

        response = await self._client.patch(api, data=data)
        response.raise_for_status()
        return SecretScanningAlert.from_dict(response.json())

    async def locations(
        self,
        repo: str,
        alert_number: Union[str, int],
    ) -> AsyncIterator[AlertLocation]:
        """
        Lists all locations for a given secret scanning alert for an eligible
        repository

        https://docs.github.com/en/rest/secret-scanning/secret-scanning#list-locations-for-a-secret-scanning-alert

        Args:
            repo: GitHub repository (owner/name)
            alert_number: The number that identifies a secret scanning alert in
                its repository

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the secret scanning alert locations

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for location in await api.secret_scanning.locations(
                        "foo/bar",
                        123,
                    ):
                        print(location)
        """
        api = f"/repos/{repo}/secret-scanning/alerts/{alert_number}/locations"
        params = {"per_page": "100"}

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for location in response.json():
                location_type = location["type"]
                location_details = location["details"]
                if location_type == LocationType.COMMIT.value:
                    yield AlertLocation(
                        type=LocationType.COMMIT,
                        details=CommitLocation.from_dict(location_details),
                    )
                elif location_type == LocationType.ISSUE_BODY.value:
                    yield AlertLocation(
                        type=LocationType.ISSUE_BODY,
                        details=IssueBodyLocation.from_dict(location_details),
                    )
                elif location_type == LocationType.ISSUE_COMMENT.value:
                    yield AlertLocation(
                        type=LocationType.ISSUE_COMMENT,
                        details=IssueCommentLocation.from_dict(
                            location_details
                        ),
                    )
                elif location_type == LocationType.ISSUE_TITLE.value:
                    yield AlertLocation(
                        type=LocationType.ISSUE_TITLE,
                        details=IssueTitleLocation.from_dict(location_details),
                    )
