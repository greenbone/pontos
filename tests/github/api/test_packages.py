# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from pontos.github.api.packages import GitHubAsyncRESTPackages
from pontos.github.models.packages import (
    Package,
    PackageType,
    PackageVersion,
    PackageVisibility,
)
from pontos.testing import AsyncIteratorMock
from tests import aiter, anext
from tests.github.api import GitHubAsyncRESTTestCase, create_response

from .test_organizations import MEMBER_DICT, REPOSITORY_DICT

PACKAGE_VERSION = {
    "id": 1,
    "name": "v1.0.0",
    "url": "https://api.github.com/orgs/foo/packages/container/bar/versions/1",
    "package_html_url": "https://github.com/orgs/foo/packages/container/bar/versions",
    "created_at": "2022-01-01T00:00:00Z",
    "updated_at": "2022-01-01T00:00:00Z",
    "html_url": "https://github.com/orgs/foo/packages/container/bar/1",
    "metadata": {
        "package_type": "container",
        "container": {"tags": ["latest"]},
    },
}


class GitHubAsyncRESTPackagesTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTPackages

    async def test_exists(self):
        response = create_response(is_success=True)
        self.client.get.return_value = response

        self.assertTrue(
            await self.api.exists(
                organization="foo",
                package_type=PackageType.CONTAINER,
                package_name="bar",
            )
        )

        self.client.get.assert_awaited_once_with(
            "/orgs/foo/packages/container/bar"
        )

    async def test_package(self):
        response = create_response()
        response.json.return_value = {
            "id": 1,
            "name": "bar",
            "package_type": "container",
            "owner": MEMBER_DICT,
            "version_count": 1,
            "visibility": "public",
            "url": "https://api.github.com/orgs/foo/packages/container/bar",
            "tags": ["foo", "bar", "baz"],
            "created_at": "2022-01-01T00:00:00Z",
            "updated_at": "2022-01-01T00:00:00Z",
            "repository": REPOSITORY_DICT,
            "html_url": "https://github.com/orgs/foo/packages/container/repo/bar",
        }

        self.client.get.return_value = response

        package = await self.api.package("foo", PackageType.CONTAINER, "bar")

        self.client.get.assert_awaited_once_with(
            "/orgs/foo/packages/container/bar"
        )

        self.assertIsInstance(package, Package)
        self.assertEqual(package.owner.login, "octocat")
        self.assertEqual(package.name, "bar")
        self.assertEqual(package.version_count, 1)
        self.assertEqual(package.visibility, PackageVisibility.PUBLIC)
        self.assertEqual(
            package.url,
            "https://api.github.com/orgs/foo/packages/container/bar",
        )
        self.assertEqual(package.tags, ["foo", "bar", "baz"])
        self.assertEqual(package.created_at, "2022-01-01T00:00:00Z")
        self.assertEqual(package.updated_at, "2022-01-01T00:00:00Z")
        self.assertEqual(
            package.html_url,
            "https://github.com/orgs/foo/packages/container/repo/bar",
        )

    async def test_packages(self):
        response = create_response()
        response.json.return_value = [
            {
                "id": 1,
                "name": "bar",
                "package_type": "container",
                "owner": MEMBER_DICT,
                "version_count": 1,
                "visibility": "public",
                "url": "https://api.github.com/orgs/foo/packages/container/bar",
                "tags": ["foo", "bar", "baz"],
                "created_at": "2022-01-01T00:00:00Z",
                "updated_at": "2022-01-01T00:00:00Z",
                "repository": REPOSITORY_DICT,
                "html_url": "https://github.com/orgs/foo/packages/container/repo/bar",
            }
        ]

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.packages("foo", package_type=PackageType.CONTAINER)
        )
        package = await anext(async_it)
        self.assertEqual(package.id, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/packages/container",
            params={"per_page": "100"},
        )

    async def test_package_version(self):
        response = create_response()
        response.json.return_value = PACKAGE_VERSION

        self.client.get.return_value = response

        package_version: PackageVersion = await self.api.package_version(
            "foo", PackageType.CONTAINER, "bar", 1
        )

        self.client.get.assert_awaited_once_with(
            "/orgs/foo/packages/container/bar/versions/1"
        )

        self.assertEqual(package_version.id, 1)
        self.assertEqual(package_version.name, "v1.0.0")
        self.assertEqual(
            package_version.url,
            "https://api.github.com/orgs/foo/packages/container/bar/versions/1",
        )
        self.assertEqual(
            package_version.package_html_url,
            "https://github.com/orgs/foo/packages/container/bar/versions",
        )
        self.assertEqual(package_version.created_at, "2022-01-01T00:00:00Z")
        self.assertEqual(package_version.updated_at, "2022-01-01T00:00:00Z")
        self.assertEqual(
            package_version.html_url,
            "https://github.com/orgs/foo/packages/container/bar/1",
        )
        self.assertEqual(
            package_version.metadata.package_type, PackageType.CONTAINER
        )
        self.assertEqual(package_version.metadata.container.tags, ["latest"])

    async def test_package_version_tags(self):
        response = create_response()
        response.json.return_value = {
            "metadata": {"container": {"tags": ["latest", "stable"]}}
        }

        self.client.get.return_value = response

        tags = await self.api.package_version_tags(
            organization="foo",
            package_type=PackageType.CONTAINER,
            package_name="bar",
            version=1,
        )

        self.client.get.assert_awaited_once_with(
            "/orgs/foo/packages/container/bar/versions/1"
        )

        self.assertEqual(tags, ["latest", "stable"])

    async def test_delete_package(self):
        response = create_response(is_success=True)
        self.client.delete.return_value = response

        await self.api.delete_package(
            organization="foo",
            package_type=PackageType.CONTAINER,
            package_name="bar",
        )

        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/packages/container/bar"
        )

    async def test_delete_package_version(self):
        response = create_response(is_success=True)
        self.client.delete.return_value = response

        await self.api.delete_package_version(
            organization="foo",
            package_type=PackageType.CONTAINER,
            package_name="bar",
            version=1,
        )

        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/packages/container/bar/versions/1"
        )

    async def test_package_versions(self):
        response1 = create_response()
        response1.json.return_value = [PACKAGE_VERSION]
        response2 = create_response()
        package_version2 = PACKAGE_VERSION.copy()
        package_version2["id"] = 2
        response2.json.return_value = [package_version2]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(
            self.api.package_versions("foo", PackageType.CONTAINER, "bar")
        )
        package_version = await anext(async_it)
        self.assertEqual(package_version.id, 1)
        package_version = await anext(async_it)
        self.assertEqual(package_version.id, 2)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/packages/container/bar/versions"
        )

    async def test_delete_package_with_tag(self):
        response = create_response(is_success=True)
        self.client.delete.return_value = response

        package_version_response = create_response()
        package_version_response.json.return_value = [PACKAGE_VERSION]
        self.client.get_all.return_value = AsyncIteratorMock(
            [package_version_response]
        )

        tags_response = create_response()
        tags_response.json.return_value = {
            "metadata": {"container": {"tags": ["latest", "stable"]}}
        }
        self.client.get.return_value = tags_response

        await self.api.delete_package_with_tag(
            organization="foo",
            package_type=PackageType.CONTAINER,
            package_name="bar",
            tag="latest",
        )

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/packages/container/bar/versions"
        )
        self.client.get.assert_awaited_once_with(
            "/orgs/foo/packages/container/bar/versions/1"
        )
        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/packages/container/bar/versions/1"
        )
