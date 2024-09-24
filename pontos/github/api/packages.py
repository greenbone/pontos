# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import AsyncIterator

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.errors import GitHubApiError
from pontos.github.models.packages import Package, PackageType, PackageVersion


class GitHubAsyncRESTPackages(GitHubAsyncREST):
    async def exists(
        self, organization: str, package_type: PackageType, package_name: str
    ) -> bool:
        """
        Check if a package exists

        Args:
            package: GitHub package (owner/name) to use

        Returns:
            True if the package exists

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    exists = api.packages.exists("foo")
        """
        api = f"/orgs/{organization}/packages/{package_type}/{package_name}"
        response = await self._client.get(api)
        return response.is_success

    async def package(
        self, organization: str, package_type: PackageType, package_name: str
    ) -> Package:
        """
        Get information about a package

        https://docs.github.com/en/rest/reference/packages#get-a-package-for-an-organization

        Args:
            organization: GitHub organization to use
            package_type: Type of the package to get
            package_name: Name of the package to get

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            Package information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    package = api.packages.package(
                        organization="foo",
                        package_type="container",
                        package_name="bar",
                    ):

                        print(package.name)

        """
        api = f"/orgs/{organization}/packages/{package_type}/{package_name}"
        response = await self._client.get(api)
        response.raise_for_status()
        return Package.from_dict(response.json())

    async def packages(
        self, organization: str, package_type: str
    ) -> AsyncIterator[Package]:
        """
        Get information about organization packages

        https://docs.github.com/en/rest/reference/packages#list-packages-for-an-organization

        Args:
            organization: GitHub organization to use
            package_type: Type of the packages to list


        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            An async iterator yielding packages information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for package in api.packages.packages(
                        organization="foo",
                        package_type="container",
                    ):
                        print(package)
        """
        api = f"/orgs/{organization}/packages/{package_type}"
        params = {"per_page": "100"}
        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for package in response.json():
                yield Package.from_dict(package)

    async def package_version(
        self,
        organization: str,
        package_type: PackageType,
        package_name: str,
        version: int,
    ) -> PackageVersion:
        """
        Get information about a package version

        https://docs.github.com/en/rest/reference/packages#get-a-package-version-for-an-organization

        Args:
            organization: GitHub organization to use
            package_type: Type of the package to get
            package_name: Name of the package to get
            version: Version of the package to get

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            Package version information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    package = api.packages.package_version(
                        organization="foo",
                        package_type="container",
                        package_name="bar",
                        version=1,
                    ):

                    print(package.version)
        """
        api = f"/orgs/{organization}/packages/{package_type}/{package_name}/versions/{version}"
        response = await self._client.get(api)
        if not response.is_success:
            raise GitHubApiError(response)
        return PackageVersion.from_dict(response.json())

    async def package_versions(
        self, organization: str, package_type: PackageType, package_name: str
    ) -> AsyncIterator[PackageVersion]:
        """
        Get information about package versions


        https://docs.github.com/en/rest/reference/packages#list-package-versions-for-an-organization


        Args:
            organization: GitHub organization to use
            package_type: Type of the package to get
            package_name: Name of the package to get

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            An async iterator yielding package versions

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for package in api.packages.package_versions(
                        organization="foo",
                        package_type="container",
                        package_name="bar",
                    ):
                        print(package)
        """
        api = f"/orgs/{organization}/packages/{package_type}/{package_name}/versions"
        async for response in self._client.get_all(api):
            response.raise_for_status()
            versions = response.json()
            if versions:
                for version in versions:
                    yield PackageVersion.from_dict(version)

    async def package_version_tags(
        self,
        organization: str,
        package_type: PackageType,
        package_name: str,
        version: int,
    ) -> list[str]:
        """
        Get information about package version tags

        Uses https://docs.github.com/en/rest/reference/packages#get-a-package-version-for-an-organization
        and only returns the tags

        Args:
            organization: GitHub organization to use
            package_type: Type of the package to get
            package_name: Name of the package to get
            version: Version of the package to get

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            List of tags for the package version

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    tags = api.packages.package_version_tags(
                        organization="foo",
                        package_type="container",
                        package_name="bar",
                        version=1,
                    )

                    print(tags)
        """
        api = f"/orgs/{organization}/packages/{package_type}/{package_name}/versions/{version}"
        response = await self._client.get(api)
        if not response.is_success:
            raise GitHubApiError(response)
        resp = response.json()
        return resp["metadata"]["container"]["tags"]

    async def delete_package(
        self, organization: str, package_type: PackageType, package_name: str
    ) -> None:
        """
        Delete a package

        https://docs.github.com/en/rest/reference/packages#delete-a-package-for-an-organization

        Args:
            organization: GitHub organization to use
            package_type: Type of the package to delete
            package_name: Name of the package to delete

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    api.packages.delete_package(
                        organization="foo",
                        package_type="container",
                        package_name="bar",
                    )
        """
        api = f"/orgs/{organization}/packages/{package_type}/{package_name}"
        response = await self._client.delete(api)
        if not response.is_success:
            raise GitHubApiError(response)

    async def delete_package_version(
        self,
        organization: str,
        package_type: PackageType,
        package_name: str,
        version: int,
    ) -> None:
        """
        Delete a package version

        https://docs.github.com/en/rest/reference/packages#delete-a-package-version-for-an-organization

        Args:
            organization: GitHub organization to use
            package_type: Type of the package to delete
            package_name: Name of the package to delete
            version: Version of the package to delete

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    api.packages.delete_package_version(
                        organization="foo",
                        package_type="container",
                        package_name="bar",
                        version=1,
                    )
        """

        api = f"/orgs/{organization}/packages/{package_type}/{package_name}/versions/{version}"
        response = await self._client.delete(api)
        if not response.is_success:
            raise GitHubApiError(response)

    async def delete_package_with_tag(
        self,
        organization: str,
        package_type: PackageType,
        package_name: str,
        tag: str,
    ) -> None:
        """
        Delete a package with a specific tag

        Args:
            organization: GitHub organization to use
            package_type: Type of the package to delete
            package_name: Name of the package to delete
            tag: Tag of the package to delete

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    api.packages.delete_package_with_tag(
                        organization="foo",
                        package_type="container",
                        package_name="bar",
                        tag="latest",
                    )
        """
        async for package_version in self.package_versions(
            organization, package_type, package_name
        ):
            if tag in await self.package_version_tags(
                organization, package_type, package_name, package_version.id
            ):
                api = f"/orgs/{organization}/packages/{package_type}/{package_name}/versions/{package_version.id}"
                response = await self._client.delete(api)
                if not response.is_success:
                    raise GitHubApiError(response)
