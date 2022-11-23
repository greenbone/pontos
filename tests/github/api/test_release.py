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

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import httpx

from pontos.github.api import GitHubRESTApi
from pontos.github.api.release import GitHubAsyncRESTReleases
from pontos.helper import DEFAULT_TIMEOUT
from tests import AsyncIteratorMock, AsyncMock, aiter, anext
from tests.github.api import (
    GitHubAsyncRESTTestCase,
    create_response,
    default_request,
)

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
            {"browser_download_url": "http://bar", "name": "bar"},
            {"browser_download_url": "http://baz", "name": "baz"},
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
            {"browser_download_url": "http://bar", "name": "bar"},
            {"browser_download_url": "http://baz", "name": "baz"},
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


class GitHubReleaseTestCase(unittest.TestCase):
    @patch("pontos.github.api.api.httpx.post")
    def test_create_tag_reference(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_tag_reference(
            repo="foo/bar",
            tag="v1.2.3",
            sha="sha",
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/git/refs",
            json={
                "repo": "foo/bar",
                "ref": "refs/tags/v1.2.3",
                "sha": "sha",
            },
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    def test_create_tag(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_tag(
            repo="foo/bar",
            tag="v1.2.3",
            message="test tag",
            git_object="sha",
            name="Test user",
            email="test@test.test",
            git_object_type="commit",
            date="2022-10-18T04:40:22.157178",
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/git/tags",
            json={
                "repo": "foo/bar",
                "tag": "v1.2.3",
                "message": "test tag",
                "object": "sha",
                "type": "commit",
                "tagger": {
                    "name": "Test user",
                    "email": "test@test.test",
                    "date": "2022-10-18T04:40:22.157178",
                },
            },
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    def test_create_tag_no_data_git_object_type(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_tag(
            repo="foo/bar",
            tag="v1.2.3",
            message="test tag",
            git_object="sha",
            name="Test user",
            email="test@test.test",
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/git/tags",
            json={
                "repo": "foo/bar",
                "tag": "v1.2.3",
                "message": "test tag",
                "object": "sha",
                "type": "commit",
                "tagger": {
                    "name": "Test user",
                    "email": "test@test.test",
                },
            },
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    def test_create_release(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_release(
            "foo/bar",
            "v1.2.3",
            name="Foo v1.2.3",
            body="This is a release",
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/releases",
            json={
                "tag_name": "v1.2.3",
                "name": "Foo v1.2.3",
                "body": "This is a release",
                "draft": False,
                "prerelease": False,
            },
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.get")
    def test_release_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.ok = True
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.release_exists("foo/bar", "v1.2.3")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/releases/tags/v1.2.3",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
        self.assertTrue(exists)

    @patch("pontos.github.api.api.httpx.get")
    def test_release(self, requests_mock: MagicMock):
        response = MagicMock()
        response.json.return_value = json.loads(
            (here / "release-response.json").read_text(encoding="utf-8")
        )

        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        data = api.release("greenbone/pontos", "v21.11.0")

        args, kwargs = default_request(
            "https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0",  # pylint: disable=line-too-long
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(data["id"], 52499047)

    @patch("pontos.helper.Path")
    @patch("pontos.github.api.api.httpx.stream")
    def test_download_release_tarball(
        self, requests_mock: MagicMock, path_mock: MagicMock
    ):
        response = MagicMock()
        response.iter_bytes.return_value = [b"foo", b"bar", b"baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = None
        response_stream = MagicMock()
        response_stream.__enter__.return_value = response
        requests_mock.return_value = response_stream

        api = GitHubRESTApi("12345")
        download_file = path_mock()
        with api.download_release_tarball(
            "greenbone/pontos", "v21.11.0", download_file
        ) as download_progress:
            args, kwargs = default_request(
                "GET",
                "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz",  # pylint: disable=line-too-long
                headers=None,
                timeout=DEFAULT_TIMEOUT,
            )
            requests_mock.assert_called_once_with(*args, **kwargs)
            response_headers.get.assert_called_once_with("content-length")

            self.assertIsNone(download_progress.length)

            it = iter(download_progress)
            progress = next(it)
            self.assertIsNone(progress)
            progress = next(it)
            self.assertIsNone(progress)
            progress = next(it)
            self.assertIsNone(progress)

            with self.assertRaises(StopIteration):
                next(it)

    @patch("pontos.helper.Path")
    @patch("pontos.github.api.api.httpx.stream")
    def test_download_release_tarball_with_content_length(
        self, requests_mock: MagicMock, path_mock: MagicMock
    ):
        response = MagicMock()
        response.iter_bytes.return_value = [b"foo", b"bar", b"baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = "9"
        response_stream = MagicMock()
        response_stream.__enter__.return_value = response
        requests_mock.return_value = response_stream

        api = GitHubRESTApi("12345")
        download_file = path_mock()
        with api.download_release_tarball(
            "greenbone/pontos", "v21.11.0", download_file
        ) as download_progress:
            args, kwargs = default_request(
                "GET",
                "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz",  # pylint: disable=line-too-long
                headers=None,
                timeout=DEFAULT_TIMEOUT,
            )
            requests_mock.assert_called_once_with(*args, **kwargs)
            response_headers.get.assert_called_once_with("content-length")

            self.assertEqual(download_progress.length, 9)

            it = iter(download_progress)
            progress = next(it)
            self.assertEqual(progress, 1 / 3)
            progress = next(it)
            self.assertEqual(progress, 2 / 3)
            progress = next(it)
            self.assertEqual(progress, 1)

            with self.assertRaises(StopIteration):
                next(it)

    @patch("pontos.helper.Path")
    @patch("pontos.github.api.api.httpx.stream")
    def test_download_release_zip(
        self, requests_mock: MagicMock, path_mock: MagicMock
    ):
        response = MagicMock()
        response.iter_bytes.return_value = [b"foo", b"bar", b"baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = None
        response_stream = MagicMock()
        response_stream.__enter__.return_value = response
        requests_mock.return_value = response_stream

        api = GitHubRESTApi("12345")
        download_file = path_mock()
        with api.download_release_zip(
            "greenbone/pontos", "v21.11.0", download_file
        ) as download_progress:
            args, kwargs = default_request(
                "GET",
                "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.zip",  # pylint: disable=line-too-long
                headers=None,
                timeout=DEFAULT_TIMEOUT,
            )
            requests_mock.assert_called_once_with(*args, **kwargs)
            response_headers.get.assert_called_once_with("content-length")

            self.assertIsNone(download_progress.length)

            it = iter(download_progress)
            progress = next(it)
            self.assertIsNone(progress)
            progress = next(it)
            self.assertIsNone(progress)
            progress = next(it)
            self.assertIsNone(progress)

            with self.assertRaises(StopIteration):
                next(it)

    @patch("pontos.helper.Path")
    @patch("pontos.github.api.api.httpx.get")
    @patch("pontos.github.api.api.httpx.stream")
    def test_download_release_assets(
        self,
        stream_mock: MagicMock,
        request_mock: MagicMock,
        _path_mock: MagicMock,
    ):
        response = MagicMock()
        response.iter_bytes.side_effect = [
            [b"foo", b"bar", b"baz"],
            [b"lorem", b"ipsum"],
        ]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = None
        response_stream = MagicMock()
        response_stream.__enter__.return_value = response
        stream_mock.return_value = response_stream

        response = MagicMock()
        response.json.side_effect = [
            {
                "assets_url": "https://api.github.com/repos/greenbone/pontos/releases/52499047/assets",  # pylint: disable=line-too-long
            },
            [
                {
                    "name": "foo-21.11.0.tar.gz",
                    "browser_download_url": "https://github.com/greenbone/pontos/releases/download/v21.11.0/foo-21.11.0.tar.gz",  # pylint: disable=line-too-long
                },
                {
                    "name": "bar-21.11.0.zip",
                    "browser_download_url": "https://github.com/greenbone/pontos/releases/download/v21.11.0/bar-21.11.0.zip",  # pylint: disable=line-too-long
                },
            ],
        ]

        request_mock.return_value = response

        api = GitHubRESTApi("12345")
        download_iter = iter(
            api.download_release_assets("greenbone/pontos", "v21.11.0")
        )

        download_progress = next(download_iter)
        self.assertIsNone(download_progress.length)

        progress_it = iter(download_progress)
        progress = next(progress_it)
        self.assertIsNone(progress)
        progress = next(progress_it)
        self.assertIsNone(progress)
        progress = next(progress_it)
        self.assertIsNone(progress)

        with self.assertRaises(StopIteration):
            next(progress_it)

        download_progress = next(download_iter)
        progress_it = iter(download_progress)
        progress = next(progress_it)
        self.assertIsNone(progress)
        progress = next(progress_it)

        with self.assertRaises(StopIteration):
            next(progress_it)

        with self.assertRaises(StopIteration):
            next(download_iter)

        args1, kwargs1 = default_request(
            "https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0",  # pylint: disable=line-too-long
        )
        args2, kwargs2 = default_request(
            "https://api.github.com/repos/greenbone/pontos/releases/52499047/assets",  # pylint: disable=line-too-long
        )
        request_mock.assert_has_calls(
            [
                call(
                    *args1,
                    **kwargs1,
                ),
                call().raise_for_status(),
                call().json(),
                call(
                    *args2,
                    **kwargs2,
                ),
                call().raise_for_status(),
                call().json(),
            ]
        )

    @patch("pontos.github.api.release.Path")
    @patch("pontos.github.api.api.httpx.get")
    def test_download_release_assets_no_assets(
        self,
        request_mock: MagicMock,
        _path_mock: MagicMock,
    ):
        response = MagicMock()
        response.json.return_value = {}
        request_mock.return_value = response

        api = GitHubRESTApi("12345")
        download_iter = iter(
            api.download_release_assets("greenbone/pontos", "v21.11.0")
        )

        with self.assertRaises(StopIteration):
            next(download_iter)

    @patch("pontos.github.api.release.Path")
    @patch("pontos.github.api.api.httpx.get")
    def test_download_release_assets_no_files(
        self,
        request_mock: MagicMock,
        _path_mock: MagicMock,
    ):
        response = MagicMock()
        response.json.side_effect = [
            {
                "assets_url": "https://api.github.com/repos/greenbone/pontos/releases/52499047/assets",  # pylint: disable=line-too-long
            },
            [
                {
                    "name": "foo.txt",
                    "browser_download_url": "https://github.com/greenbone/pontos/releases/download/v21.11.0/foo.txt",  # pylint: disable=line-too-long
                },
                {
                    "name": "foo.txt.asc",
                    "browser_download_url": "https://github.com/greenbone/pontos/releases/download/v21.11.0/foo.txt.asc",  # pylint: disable=line-too-long
                },
            ],
        ]
        request_mock.return_value = response

        api = GitHubRESTApi("12345")
        download_iter = iter(
            api.download_release_assets("greenbone/pontos", "v21.11.0")
        )

        with self.assertRaises(StopIteration):
            next(download_iter)

    @patch("pontos.github.api.api.httpx.post")
    @patch("pontos.github.api.api.httpx.get")
    def test_upload_release_assets(
        self, get_mock: MagicMock, post_mock: MagicMock
    ):
        response = MagicMock()
        response.json.return_value = {
            "upload_url": "https://uploads.github.com/repos/greenbone/pontos/releases/52499047/assets{?name,label}",  # pylint: disable=line-too-long
        }
        get_mock.return_value = response

        file1 = MagicMock()
        file1.name = "foo.txt"
        content1 = b"foo"
        file1.read_bytes.return_value = content1
        file2 = MagicMock()
        file2.name = "bar.pdf"
        content2 = b"bar"
        file2.read_bytes.return_value = content2
        upload_files = [file1, file2]

        post_response = MagicMock()
        post_mock.return_value = post_response

        api = GitHubRESTApi("12345")
        upload_it = iter(
            api.upload_release_assets(
                "greenbone/pontos", "v21.11.0", upload_files
            )
        )
        args, kwargs = default_request(
            "https://uploads.github.com/repos/greenbone/pontos/releases/52499047/assets",  # pylint: disable=line-too-long
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
                "Content-Type": "application/octet-stream",
            },
            params={"name": "foo.txt"},
            content=content1,
        )
        uploaded_file = next(upload_it)
        post_mock.assert_called_with(*args, **kwargs)
        self.assertEqual(uploaded_file, file1)

        args, kwargs = default_request(
            "https://uploads.github.com/repos/greenbone/pontos/releases/52499047/assets",  # pylint: disable=line-too-long
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
                "Content-Type": "application/octet-stream",
            },
            params={"name": "bar.pdf"},
            content=content2,
        )
        uploaded_file = next(upload_it)
        post_mock.assert_called_with(*args, **kwargs)
        self.assertEqual(uploaded_file, file2)

        args, kwargs = default_request(
            "https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0",  # pylint: disable=line-too-long
        )
        get_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    @patch("pontos.github.api.api.httpx.get")
    def test_upload_release_assets_no_release(
        self, get_mock: MagicMock, post_mock: MagicMock
    ):
        response = MagicMock()
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Authentication required 401",
            request=MagicMock(),
            response=response,
        )
        get_mock.return_value = response

        file1 = MagicMock()
        file2 = MagicMock()
        upload_files = [file1, file2]

        post_response = MagicMock()
        post_mock.return_value = post_response

        api = GitHubRESTApi("12345")
        upload_it = iter(
            api.upload_release_assets(
                "greenbone/pontos", "v21.11.0", upload_files
            )
        )
        with self.assertRaises(httpx.HTTPError):
            next(upload_it)

        args, kwargs = default_request(
            "https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0",  # pylint: disable=line-too-long
        )
        get_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    @patch("pontos.github.api.api.httpx.get")
    def test_upload_release_assets_upload_fails(
        self, get_mock: MagicMock, post_mock: MagicMock
    ):
        response = MagicMock()
        response.json.return_value = {
            "upload_url": "https://uploads.github.com/repos/greenbone/pontos/releases/52499047/assets{?name,label}",  # pylint: disable=line-too-long
        }
        get_mock.return_value = response

        file1 = MagicMock()
        file1.name = "foo.txt"
        content1 = b"foo"
        file1.read_bytes.return_value = content1
        file2 = MagicMock()
        file2.name = "bar.pdf"
        content2 = b"bar"
        file2.read_bytes.return_value = content2
        upload_files = [file1, file2]

        post_response = MagicMock()
        post_response.raise_for_status.side_effect = [
            "",
            httpx.HTTPStatusError(
                "Internal Server Error",
                request=MagicMock(),
                response=response,
            ),
        ]
        post_mock.return_value = post_response

        api = GitHubRESTApi("12345")
        upload_it = iter(
            api.upload_release_assets(
                "greenbone/pontos", "v21.11.0", upload_files
            )
        )
        uploaded_file = next(upload_it)
        args, kwargs = default_request(
            "https://uploads.github.com/repos/greenbone/pontos/releases/52499047/assets",  # pylint: disable=line-too-long
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
                "Content-Type": "application/octet-stream",
            },
            params={"name": "foo.txt"},
            content=content1,
        )
        post_mock.assert_called_with(*args, **kwargs)
        self.assertEqual(uploaded_file, file1)

        with self.assertRaises(httpx.HTTPError):
            next(upload_it)

        args, kwargs = default_request(
            "https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0",  # pylint: disable=line-too-long
        )
        get_mock.assert_called_once_with(*args, **kwargs)
