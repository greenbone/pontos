# Copyright (C) 2022 Greenbone Networks GmbH
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

# pylint: disable=redefined-builtin, line-too-long, too-many-lines

from pathlib import Path
from unittest.mock import MagicMock, call

import httpx

from pontos.github.api.release import GitHubAsyncRESTReleases
from tests import AsyncIteratorMock, AsyncMock, aiter, anext
from tests.github.api import GitHubAsyncRESTTestCase, create_response

here = Path(__file__).parent

RELEASE_JSON = {
    "url": "https://api.github.com/repos/octocat/Hello-World/releases/1",
    "html_url": "https://github.com/octocat/Hello-World/releases/v1.0.0",
    "assets_url": "https://api.github.com/repos/octocat/Hello-World/releases/1/assets",
    "upload_url": "https://uploads.github.com/repos/octocat/Hello-World/releases/1/assets{?name,label}",
    "tarball_url": "https://api.github.com/repos/octocat/Hello-World/tarball/v1.0.0",
    "zipball_url": "https://api.github.com/repos/octocat/Hello-World/zipball/v1.0.0",
    "discussion_url": "https://github.com/octocat/Hello-World/discussions/90",
    "id": 1,
    "node_id": "MDc6UmVsZWFzZTE=",
    "tag_name": "v1.0.0",
    "target_commitish": "master",
    "name": "v1.0.0",
    "body": "Description of the release",
    "draft": False,
    "prerelease": False,
    "created_at": "2013-02-27T19:35:32Z",
    "published_at": "2013-02-27T19:35:32Z",
    "author": {
        "login": "octocat",
        "id": 1,
        "node_id": "MDQ6VXNlcjE=",
        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
        "gravatar_id": "",
        "url": "https://api.github.com/users/octocat",
        "html_url": "https://github.com/octocat",
        "followers_url": "https://api.github.com/users/octocat/followers",
        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
        "organizations_url": "https://api.github.com/users/octocat/orgs",
        "repos_url": "https://api.github.com/users/octocat/repos",
        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
        "received_events_url": "https://api.github.com/users/octocat/received_events",
        "type": "User",
        "site_admin": False,
    },
    "assets": [
        {
            "url": "https://api.github.com/repos/octocat/Hello-World/releases/assets/1",
            "browser_download_url": "https://github.com/octocat/Hello-World/releases/download/v1.0.0/example.zip",
            "id": 1,
            "node_id": "MDEyOlJlbGVhc2VBc3NldDE=",
            "name": "example.zip",
            "label": "short description",
            "state": "uploaded",
            "content_type": "application/zip",
            "size": 1024,
            "download_count": 42,
            "created_at": "2013-02-27T19:35:32Z",
            "updated_at": "2013-02-27T19:35:32Z",
            "uploader": {
                "login": "octocat",
                "id": 1,
                "node_id": "MDQ6VXNlcjE=",
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octocat",
                "html_url": "https://github.com/octocat",
                "followers_url": "https://api.github.com/users/octocat/followers",
                "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                "organizations_url": "https://api.github.com/users/octocat/orgs",
                "repos_url": "https://api.github.com/users/octocat/repos",
                "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octocat/received_events",
                "type": "User",
                "site_admin": False,
            },
        }
    ],
}


class GitHubAsyncRESTReleasesTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTReleases

    async def test_exists(self):
        response = create_response(is_success=True)
        self.client.get.return_value = response

        self.assertTrue(await self.api.exists("foo/bar", "v1.2.3"))

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/releases/tags/v1.2.3"
        )

    async def test_not_exists(self):
        response = create_response(is_success=False)
        self.client.get.return_value = response

        self.assertFalse(await self.api.exists("foo/bar", "v1.2.3"))

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/releases/tags/v1.2.3"
        )

    async def test_create(self):
        response = create_response()
        response.json.return_value = RELEASE_JSON
        self.client.post.return_value = response

        release = await self.api.create(
            "foo/bar",
            "v1.2.3",
            body="foo",
            name="baz",
            target_commitish="stable",
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/releases",
            data={
                "tag_name": "v1.2.3",
                "draft": False,
                "prerelease": False,
                "name": "baz",
                "body": "foo",
                "target_commitish": "stable",
            },
        )

        self.assertEqual(release.id, 1)

    async def test_create_simple(self):
        response = create_response()
        response.json.return_value = RELEASE_JSON
        self.client.post.return_value = response

        release = await self.api.create(
            "foo/bar",
            "v1.2.3",
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/releases",
            data={
                "tag_name": "v1.2.3",
                "draft": False,
                "prerelease": False,
            },
        )

        self.assertEqual(release.id, 1)

    async def test_create_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.create(
                "foo/bar",
                "v1.2.3",
                body="foo",
                name="baz",
                target_commitish="stable",
            )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/releases",
            data={
                "tag_name": "v1.2.3",
                "draft": False,
                "prerelease": False,
                "name": "baz",
                "body": "foo",
                "target_commitish": "stable",
            },
        )

    async def test_get(self):
        response = create_response()
        response.json.return_value = RELEASE_JSON
        self.client.get.return_value = response

        release = await self.api.get(
            "foo/bar",
            "v1.2.3",
        )

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/releases/tags/v1.2.3",
        )
        self.assertEqual(release.id, 1)

    async def test_get_failure(self):
        response = create_response()
        self.client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.get(
                "foo/bar",
                "v1.2.3",
            )

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/releases/tags/v1.2.3",
        )

    async def test_download_release_tarball(self):
        response = create_response(headers=MagicMock())
        response.headers.get.return_value = 2
        response.aiter_bytes.return_value = AsyncIteratorMock(["1", "2"])
        stream_context = AsyncMock()
        stream_context.__aenter__.return_value = response
        self.client.stream.return_value = stream_context

        async with self.api.download_release_tarball(
            "foo/bar", "v1.2.3"
        ) as download_iterable:
            it = aiter(download_iterable)
            content, progress = await anext(it)

            self.assertEqual(content, "1")
            self.assertEqual(progress, 50)

            content, progress = await anext(it)
            self.assertEqual(content, "2")
            self.assertEqual(progress, 100)

        self.client.stream.assert_called_once_with(
            "https://github.com/foo/bar/archive/refs/tags/v1.2.3.tar.gz"
        )

    async def test_download_release_zip(self):
        response = create_response(headers=MagicMock())
        response.headers.get.return_value = 2
        response.aiter_bytes.return_value = AsyncIteratorMock(["1", "2"])
        stream_context = AsyncMock()
        stream_context.__aenter__.return_value = response
        self.client.stream.return_value = stream_context

        async with self.api.download_release_zip(
            "foo/bar", "v1.2.3"
        ) as download_iterable:
            it = aiter(download_iterable)
            content, progress = await anext(it)

            self.assertEqual(content, "1")
            self.assertEqual(progress, 50)

            content, progress = await anext(it)
            self.assertEqual(content, "2")
            self.assertEqual(progress, 100)

        self.client.stream.assert_called_once_with(
            "https://github.com/foo/bar/archive/refs/tags/v1.2.3.zip"
        )

    async def test_download_release_assets(self):
        get_assets_url_response = create_response()
        data = RELEASE_JSON.copy()
        data.update({"assets_url": "https://foo.bar/assets"})
        get_assets_url_response.json.return_value = data
        get_assets_response = create_response()
        get_assets_response.json.return_value = [
            {"url": "http://bar", "name": "bar"},
            {"url": "http://baz", "name": "baz"},
        ]
        response = create_response(headers=MagicMock())
        response.headers.get.return_value = 2
        response.aiter_bytes.return_value = AsyncIteratorMock(["1", "2"])
        stream_context = AsyncMock()
        stream_context.__aenter__.return_value = response
        self.client.stream.return_value = stream_context
        self.client.get.side_effect = [
            get_assets_url_response,
            get_assets_response,
        ]

        assets_it = aiter(self.api.download_release_assets("foo/bar", "v1.2.3"))

        name, cm = await anext(assets_it)

        self.client.get.assert_has_awaits(
            [
                call("/repos/foo/bar/releases/tags/v1.2.3"),
                call("https://foo.bar/assets"),
            ]
        )

        self.client.stream.assert_called_once_with("http://bar")

        self.assertEqual(name, "bar")

        async with cm as progress_it:
            it = aiter(progress_it)
            content, progress = await anext(it)

            self.assertEqual(content, "1")
            self.assertEqual(progress, 50)

            content, progress = await anext(it)
            self.assertEqual(content, "2")
            self.assertEqual(progress, 100)

        self.client.stream.reset_mock()
        response = create_response(headers=MagicMock())
        response.headers.get.return_value = 2
        response.aiter_bytes.return_value = AsyncIteratorMock(["1", "2"])
        stream_context = AsyncMock()
        stream_context.__aenter__.return_value = response
        self.client.stream.return_value = stream_context

        name, cm = await anext(assets_it)

        self.client.stream.assert_called_once_with("http://baz")

        self.assertEqual(name, "baz")

        async with cm as progress_it:
            it = aiter(progress_it)
            content, progress = await anext(it)

            self.assertEqual(content, "1")
            self.assertEqual(progress, 50)

            content, progress = await anext(it)
            self.assertEqual(content, "2")
            self.assertEqual(progress, 100)

        with self.assertRaises(StopAsyncIteration):
            await anext(assets_it)

    async def test_download_release_assets_no_assets_url(self):
        get_assets_url_response = create_response()
        data = RELEASE_JSON.copy()
        data.update({"assets_url": None})
        get_assets_url_response.json.return_value = data
        self.client.get.return_value = get_assets_url_response
        assets_it = aiter(self.api.download_release_assets("foo/bar", "v1.2.3"))

        with self.assertRaises(RuntimeError):
            await anext(assets_it)

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/releases/tags/v1.2.3"
        )

    async def test_download_release_assets_filter(self):
        get_assets_url_response = create_response()
        data = RELEASE_JSON.copy()
        data.update({"assets_url": "https://foo.bar/assets"})
        get_assets_url_response.json.return_value = data
        get_assets_response = create_response()
        get_assets_response.json.return_value = [
            {"url": "http://bar", "name": "bar"},
            {"url": "http://baz", "name": "baz"},
        ]
        response = create_response(headers=MagicMock())
        response.headers.get.return_value = 2
        response.aiter_bytes.return_value = AsyncIteratorMock(["1", "2"])
        stream_context = AsyncMock()
        stream_context.__aenter__.return_value = response
        self.client.stream.return_value = stream_context
        self.client.get.side_effect = [
            get_assets_url_response,
            get_assets_response,
        ]

        assets_it = aiter(
            self.api.download_release_assets(
                "foo/bar", "v1.2.3", match_pattern="*r"
            )
        )

        name, cm = await anext(assets_it)

        self.client.get.assert_has_awaits(
            [
                call("/repos/foo/bar/releases/tags/v1.2.3"),
                call("https://foo.bar/assets"),
            ]
        )

        self.client.stream.assert_called_once_with("http://bar")

        self.assertEqual(name, "bar")

        async with cm as progress_it:
            it = aiter(progress_it)
            content, progress = await anext(it)

            self.assertEqual(content, "1")
            self.assertEqual(progress, 50)

            content, progress = await anext(it)
            self.assertEqual(content, "2")
            self.assertEqual(progress, 100)

        with self.assertRaises(StopAsyncIteration):
            await anext(assets_it)

    async def test_upload_release_assets(self):
        response = create_response()
        data = RELEASE_JSON.copy()
        data.update({"upload_url": "https://uploads/assets{?name,label}"})
        response.json.return_value = data
        post_response = create_response()
        self.client.get.return_value = response
        self.client.post.return_value = post_response

        file1 = MagicMock(spec=Path)
        file1.name = "foo.txt"
        content1 = b"foo"
        file1.open.return_value.__enter__.return_value.read.side_effect = [
            content1
        ]
        file2 = MagicMock(spec=Path)
        file2.name = "bar.pdf"
        content2 = b"bar"
        file2.open.return_value.__enter__.return_value.read.side_effect = [
            content2
        ]
        upload_files = [file1, (file2, "application/pdf")]

        def assert_file1(index: int):
            args = self.client.post.await_args_list[index].args
            self.assertEqual(args, ("https://uploads/assets",))
            kwargs = self.client.post.await_args_list[index].kwargs
            self.assertEqual(kwargs["params"], {"name": "foo.txt"})
            self.assertEqual(kwargs["content_type"], "application/octet-stream")

        def assert_file2(index: int):
            args = self.client.post.await_args_list[index].args
            self.assertEqual(args, ("https://uploads/assets",))
            kwargs = self.client.post.await_args_list[index].kwargs
            self.assertEqual(kwargs["params"], {"name": "bar.pdf"})
            self.assertEqual(kwargs["content_type"], "application/pdf")

        it = aiter(
            self.api.upload_release_assets("foo/bar", "v1.2.3", upload_files)
        )

        # the order of the files is non-deterministic

        f = await anext(it)
        if f == file1:
            assert_file1(0)
        else:
            assert_file2(0)

        f = await anext(it)
        if f == file1:
            assert_file1(1)
        else:
            assert_file2(1)

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/releases/tags/v1.2.3"
        )
