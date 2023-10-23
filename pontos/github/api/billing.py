# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.billing import (
    ActionsBilling,
    PackagesBilling,
    StorageBilling,
)


class GitHubAsyncRESTBilling(GitHubAsyncREST):
    async def actions(self, organization: str) -> ActionsBilling:
        """
        Get the summary of the free and paid GitHub Actions minutes used

        https://docs.github.com/en/rest/billing/billing#get-github-actions-billing-for-an-organization

        Args:
            organization: The organization name

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the Actions billing

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    billing = await api.billing.actions("foo")
                    print(billing)
        """
        api = f"/orgs/{organization}/settings/billing/actions"
        response = await self._client.get(api)
        response.raise_for_status()
        return ActionsBilling.from_dict(response.json())

    async def packages(self, organization: str) -> PackagesBilling:
        """
        Get the free and paid storage used for GitHub Packages in gigabytes

        https://docs.github.com/en/rest/billing/billing#get-github-packages-billing-for-an-organization

        Args:
            organization: The organization name

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the Packages billing

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    billing = await api.billing.packages("foo")
                    print(billing)
        """
        api = f"/orgs/{organization}/settings/billing/packages"
        response = await self._client.get(api)
        response.raise_for_status()
        return PackagesBilling.from_dict(response.json())

    async def storage(self, organization: str) -> StorageBilling:
        """
        Get the estimated paid and estimated total storage used for GitHub
        Actions and GitHub Packages

        https://docs.github.com/en/rest/billing/billing#get-shared-storage-billing-for-an-organization

        Args:
            organization: The organization name

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the storage billing

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    billing = await api.billing.storage("foo")
                    print(billing)
        """
        api = f"/orgs/{organization}/settings/billing/shared-storage"
        response = await self._client.get(api)
        response.raise_for_status()
        return StorageBilling.from_dict(response.json())
