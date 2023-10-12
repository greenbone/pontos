# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import AsyncIterator, Iterable, Optional, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.base import SortOrder
from pontos.github.models.code_scanning import (
    AlertSort,
    AlertState,
    Analysis,
    CodeQLDatabase,
    CodeScanningAlert,
    DefaultSetup,
    DefaultSetupState,
    DismissedReason,
    Instance,
    Language,
    QuerySuite,
    Severity,
)
from pontos.helper import enum_or_value


class GitHubAsyncRESTCodeScanning(GitHubAsyncREST):
    async def _alerts(
        self,
        api: str,
        *,
        tool_name: Optional[str] = None,
        tool_guid: Optional[str] = "",
        severity: Union[Severity, str, None] = None,
        state: Union[AlertState, str, None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[CodeScanningAlert]:
        params: dict[str, Union[str, None]] = {"per_page": "100"}

        if tool_name:
            params["tool_name"] = tool_name
        if tool_guid or tool_guid is None:
            params["tool_guid"] = tool_guid
        if severity:
            params["severity"] = enum_or_value(severity)
        if state:
            params["state"] = enum_or_value(state)
        if sort:
            params["sort"] = enum_or_value(sort)
        if direction:
            params["direction"] = enum_or_value(direction)

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for alert in response.json():
                yield CodeScanningAlert.from_dict(alert)

    async def organization_alerts(
        self,
        organization: str,
        *,
        tool_name: Optional[str] = None,
        tool_guid: Optional[str] = "",
        severity: Union[Severity, str, None] = None,
        state: Union[AlertState, str, None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[CodeScanningAlert]:
        """
        Get the list of code scanning alerts for all repositories of a GitHub
        organization

        https://docs.github.com/en/rest/code-scanning/code-scanning#list-code-scanning-alerts-for-an-organization

        Args:
            organization: Name of the organization
            tool_name: The name of a code scanning tool. Only results by this
                tool will be listed. You can specify the tool by using either
                tool_name or tool_guid, but not both.
            tool_guid: The GUID of a code scanning tool. Only results by this
                tool will be listed. Note that some code scanning tools may not
                include a GUID in their analysis data. You can specify the tool
                by using either tool_guid or tool_name, but not both
            severity: If specified, only code scanning alerts with this severity
                will be returned
            state: Filter alerts by state
                resolutions
            sort: The property by which to sort the results. Default is to sort
                alerts by creation date.
            direction: The direction to sort the results by. Default is desc.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the code scanning alerts

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for alert in api.code_scanning.organization_alerts(
                        "my-org"
                    ):
                        print(alert)
        """

        api = f"/orgs/{organization}/code-scanning/alerts"
        async for alert in self._alerts(
            api,
            state=state,
            severity=severity,
            tool_guid=tool_guid,
            tool_name=tool_name,
            sort=sort,
            direction=direction,
        ):
            yield alert

    async def alerts(
        self,
        repo: str,
        *,
        tool_name: Optional[str] = None,
        tool_guid: Optional[str] = "",
        severity: Union[Severity, str, None] = None,
        state: Union[AlertState, str, None] = None,
        sort: Union[AlertSort, str] = AlertSort.CREATED,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[CodeScanningAlert]:
        """
        Get the list of code scanning alerts for a repository

        https://docs.github.com/en/rest/code-scanning/code-scanning#list-code-scanning-alerts-for-a-repository

        Args:
            repo: GitHub repository (owner/name)

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the code scanning alerts

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for alert in api.code_scanning.alerts(
                        "org/repo"
                    ):
                        print(alert)
        """

        api = f"/repos/{repo}/code-scanning/alerts"
        async for alert in self._alerts(
            api,
            state=state,
            severity=severity,
            tool_guid=tool_guid,
            tool_name=tool_name,
            sort=sort,
            direction=direction,
        ):
            yield alert

    async def alert(
        self,
        repo: str,
        alert_number: Union[str, int],
    ) -> CodeScanningAlert:
        """
        Get a single code scanning alert

        https://docs.github.com/en/rest/code-scanning/code-scanning#get-a-code-scanning-alert

        Args:
            repo: GitHub repository (owner/name)
            alert_number: The number that identifies a code scanning alert in
                its repository

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Code scanning alert information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    alert = await api.code_scanning.alert("foo/bar", 123)
        """
        api = f"/repos/{repo}/code-scanning/alerts/{alert_number}"
        response = await self._client.get(api)
        response.raise_for_status()
        return CodeScanningAlert.from_dict(response.json())

    async def update_alert(
        self,
        repo: str,
        alert_number: Union[str, int],
        state: Union[AlertState, str],
        *,
        dismissed_reason: Union[DismissedReason, str, None] = None,
        dismissed_comment: Optional[str] = None,
    ) -> CodeScanningAlert:
        """
        Update a single code scanning alert

        https://docs.github.com/en/rest/code-scanning/code-scanning#update-a-code-scanning-alert

        Args:
            repo: GitHub repository (owner/name)
            alert_number: The number that identifies a code scanning alert in
                its repository
            state: The state of the alert
            dismissed_reason: The reason for dismissing or closing the alert
            dismissed_comment: The dismissal comment associated with the
                dismissal of the alert.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Code scanning alert information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi
                from pontos.github.models.code_scanning import (
                    AlertState,
                    DismissedReason,
                )

                async with GitHubAsyncRESTApi(token) as api:
                    alert = await api.code_scanning.update_alert(
                        "foo/bar",
                        123,
                        AlertState.DISMISSED,
                        dismissed_reason=DismissedReason.WONT_FIX,
                        dismissed_comment="Not applicable",
                    )
        """
        api = f"/repos/{repo}/code-scanning/alerts/{alert_number}"

        data = {"state": enum_or_value(state)}
        if dismissed_reason:
            data["dismissed_reason"] = enum_or_value(dismissed_reason)
        if dismissed_comment:
            data["dismissed_comment"] = dismissed_comment

        response = await self._client.patch(api, data=data)
        response.raise_for_status()
        return CodeScanningAlert.from_dict(response.json())

    async def instances(
        self,
        repo: str,
        alert_number: Union[str, int],
        *,
        ref: Optional[str] = None,
    ) -> AsyncIterator[Instance]:
        """
        Lists all instances of the specified code scanning alert

        https://docs.github.com/en/rest/code-scanning/code-scanning#list-instances-of-a-code-scanning-alert

        Args:
            repo: GitHub repository (owner/name)
            alert_number: The number that identifies a code scanning alert in
                its repository
            ref: The Git reference for the results you want to list. The ref
                for a branch can be formatted either as refs/heads/<branch name>
                or simply <branch name>. To reference a pull request use
                refs/pull/<number>/merge.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the code scanning alert instances

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for instance in api.code_scanning.instances(
                        "org/repo", 1
                    ):
                        print(instance)
        """

        api = f"/repos/{repo}/code-scanning/alerts/{alert_number}/instances"
        params = {"per_page": "100"}

        if ref:
            params["ref"] = ref

        async for response in self._client.get_all(api, params=params):
            for alert in response.json():
                yield Instance.from_dict(alert)

    async def analyses(
        self,
        repo: str,
        *,
        tool_name: Optional[str] = None,
        tool_guid: Optional[str] = "",
        ref: Optional[str] = None,
        sarif_id: Optional[str] = None,
        direction: Union[str, SortOrder] = SortOrder.DESC,
    ) -> AsyncIterator[Analysis]:
        """
        Lists the details of all code scanning analyses for a repository,
        starting with the most recent.

        https://docs.github.com/en/rest/code-scanning/code-scanning#list-code-scanning-analyses-for-a-repository

        Args:
            repo: GitHub repository (owner/name)
            tool_name: The name of a code scanning tool. Only results by this
                tool will be listed. You can specify the tool by using either
                tool_name or tool_guid, but not both.
            tool_guid: The GUID of a code scanning tool. Only results by this
                tool will be listed. Note that some code scanning tools may not
                include a GUID in their analysis data. You can specify the tool
                by using either tool_guid or tool_name, but not both
            ref: The Git reference for the analyses you want to list. The ref
                for a branch can be formatted either as refs/heads/<branch name>
                or simply <branch name>. To reference a pull request use
                refs/pull/<number>/merge.
            sarif_id: Filter analyses belonging to the same SARIF upload

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the code scanning alert analysis data

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for data in api.code_scanning.analyses(
                        "org/repo"
                    ):
                        print(data)
        """

        api = f"/repos/{repo}/code-scanning/analyses"
        params: dict[str, Union[str, None]] = {"per_page": "100"}

        if tool_name:
            params["tool_name"] = tool_name
        if tool_guid or tool_guid is None:
            params["tool_guid"] = tool_guid
        if ref:
            params["ref"] = ref
        if sarif_id:
            params["sarif_id"] = sarif_id
        if direction:
            params["direction"] = enum_or_value(direction)

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for alert in response.json():
                yield Analysis.from_dict(alert)

    async def analysis(
        self,
        repo: str,
        analysis_id: Union[int, str],
    ) -> Analysis:
        """
        Gets a specified code scanning analysis for a repository

        https://docs.github.com/en/rest/code-scanning/code-scanning#get-a-code-scanning-analysis-for-a-repository

        Args:
            repo: GitHub repository (owner/name)
            analysis_id: The ID of the analysis

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Code scanning alert analysis data

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    analysis = await api.code_scanning.analysis(
                        "org/repo", 123
                    )
                    print(analysis)
        """

        api = f"/repos/{repo}/code-scanning/analyses/{analysis_id}"
        response = await self._client.get(api)
        response.raise_for_status()
        return Analysis.from_dict(response.json())

    async def delete_analysis(
        self,
        repo: str,
        analysis_id: Union[int, str],
    ) -> dict[str, str]:
        """
        Delete a specified code scanning analysis from a repository

        https://docs.github.com/en/rest/code-scanning/code-scanning#delete-a-code-scanning-analysis-from-a-repository

        Args:
            repo: GitHub repository (owner/name)
            analysis_id: The ID of the analysis

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            See the GitHub documentation for the response object

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    await api.code_scanning.delete(
                        "org/repo", 123
                    )
        """

        api = f"/repos/{repo}/code-scanning/analyses/{analysis_id}"
        response = await self._client.delete(api)
        response.raise_for_status()
        return response.json()

    async def codeql_databases(
        self,
        repo: str,
    ) -> AsyncIterator[CodeQLDatabase]:
        """
        List the CodeQL databases that are available in a repository.

        https://docs.github.com/en/rest/code-scanning/code-scanning#list-codeql-databases-for-a-repository

        Args:
            repo: GitHub repository (owner/name)

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding the code scanning codeql database
            information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for database in api.code_scanning.codeql_databases(
                        "org/repo"
                    ):
                        print(database)
        """

        api = f"/repos/{repo}/code-scanning/codeql/databases"
        params = {"per_page": "100"}

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for alert in response.json():
                yield CodeQLDatabase.from_dict(alert)

    async def codeql_database(
        self,
        repo: str,
        language: str,
    ) -> CodeQLDatabase:
        """
        Get a CodeQL database for a language in a repository

        https://docs.github.com/en/rest/code-scanning/code-scanning#get-a-codeql-database-for-a-repository

        Args:
            repo: GitHub repository (owner/name)
            language: The language of the CodeQL database

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Code scanning CodeQL database information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    db = await api.code_scanning.codeql_database(
                        "org/repo", "java"
                    )
                    print(db)
        """

        api = f"/repos/{repo}/code-scanning/codeql/databases/{language}"
        response = await self._client.get(api)
        response.raise_for_status()
        return CodeQLDatabase.from_dict(response.json())

    async def default_setup(
        self,
        repo: str,
    ) -> DefaultSetup:
        """
        Gets a code scanning default setup configuration

        https://docs.github.com/en/rest/code-scanning/code-scanning#get-a-code-scanning-default-setup-configuration

        Args:
            repo: GitHub repository (owner/name)

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Code scanning default setup

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    setup = await api.code_scanning.default_setup(
                        "org/repo"
                    )
                    print(setup)
        """

        api = f"/repos/{repo}/code-scanning/default-setup"
        response = await self._client.get(api)
        response.raise_for_status()
        return DefaultSetup.from_dict(response.json())

    async def update_default_setup(
        self,
        repo: str,
        state: Union[str, DefaultSetupState],
        query_suite: Union[str, QuerySuite],
        languages: Iterable[Union[str, Language]],
    ) -> dict[str, str]:
        """
        Updates a code scanning default setup configuration

        https://docs.github.com/en/rest/code-scanning/code-scanning#update-a-code-scanning-default-setup-configuration

        Args:
            repo: GitHub repository (owner/name)
            state: Whether code scanning default setup has been configured or
                not
            query_suite: CodeQL query suite to be used
            languages: CodeQL languages to be analyzed

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            See the GitHub documentation for the response object

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi
                from pontos.github.models.code_scanning import (
                    DefaultSetupState,
                    Language,
                    QuerySuite,
                )

                async with GitHubAsyncRESTApi(token) as api:
                    await api.code_scanning.update_default_setup(
                        "org/repo",
                        state=DefaultSetupState.CONFIGURED,
                        query_suite=QuerySuite.EXTENDED,
                        languages=[Language.PYTHON, Language.JAVASCRIPT]
                    )
        """

        api = f"/repos/{repo}/code-scanning/code-scanning/default-setup"
        data = {
            "state": enum_or_value(state),
            "query_suite": enum_or_value(query_suite),
            "languages": [enum_or_value(value) for value in languages],
        }
        response = await self._client.patch(api, data=data)
        response.raise_for_status()
        return response.json()
