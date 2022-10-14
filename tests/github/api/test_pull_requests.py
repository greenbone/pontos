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

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from httpx import HTTPStatusError

from pontos.github.api import GitHubRESTApi
from pontos.github.api.helper import FileStatus
from pontos.github.api.pull_requests import GitHubAsyncRESTPullRequests
from tests import AsyncIteratorMock
from tests.github.api import (
    GitHubAsyncRESTTestCase,
    create_response,
    default_request,
)

here = Path(__file__).parent


class GitHubAsyncRESTPullRequestsTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTPullRequests

    async def test_exists(self):
        response = create_response(is_success=True)
        self.client.get.return_value = response

        self.assertTrue(await self.api.exists("foo/bar", 123))

        self.client.get.assert_awaited_once_with("/repos/foo/bar/pulls/123")

    async def test_not_exists(self):
        response = create_response(is_success=False)
        self.client.get.return_value = response

        self.assertFalse(await self.api.exists("foo/bar", 123))

        self.client.get.assert_awaited_once_with("/repos/foo/bar/pulls/123")

    async def test_commits(self):
        response1 = create_response()
        response1.json.return_value = [{"id": 1}]
        response2 = create_response()
        response2.json.return_value = [{"id": 2}, {"id": 3}]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        commits = await self.api.commits("foo/bar", 123)

        self.assertEqual(len(commits), 3)
        self.assertEqual(commits, [{"id": 1}, {"id": 2}, {"id": 3}])

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/pulls/123/commits",
            params={"per_page": "100"},
        )

    async def test_create(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.create(
            "foo/bar",
            head_branch="main",
            base_branch="baz",
            title="Lorem",
            body="Ipsum",
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/pulls",
            data={
                "head": "main",
                "base": "baz",
                "title": "Lorem",
                "body": "Ipsum",
            },
        )

    async def test_create_failure(self):
        response = create_response()
        self.client.post.side_effect = HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(HTTPStatusError):
            await self.api.create(
                "foo/bar",
                head_branch="main",
                base_branch="baz",
                title="Lorem",
                body="Ipsum",
            )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/pulls",
            data={
                "head": "main",
                "base": "baz",
                "title": "Lorem",
                "body": "Ipsum",
            },
        )

    async def test_update(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.update(
            "foo/bar",
            123,
            base_branch="baz",
            title="Lorem",
            body="Ipsum",
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/pulls/123",
            data={
                "base": "baz",
                "title": "Lorem",
                "body": "Ipsum",
            },
        )

    async def test_update_simple(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.update(
            "foo/bar",
            123,
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/pulls/123",
            data={},
        )

    async def test_update_failure(self):
        response = create_response()
        self.client.post.side_effect = HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(HTTPStatusError):
            await self.api.update(
                "foo/bar",
                123,
                base_branch="baz",
                title="Lorem",
                body="Ipsum",
            )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/pulls/123",
            data={
                "base": "baz",
                "title": "Lorem",
                "body": "Ipsum",
            },
        )

    async def test_add_comment(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.add_comment(
            "foo/bar",
            123,
            "Lorem Ipsum",
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/issues/123/comments",
            data={
                "body": "Lorem Ipsum",
            },
        )

    async def test_add_comment_failure(self):
        response = create_response()
        self.client.post.side_effect = HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(HTTPStatusError):
            await self.api.add_comment(
                "foo/bar",
                123,
                "Lorem Ipsum",
            )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/issues/123/comments",
            data={
                "body": "Lorem Ipsum",
            },
        )

    async def test_files(self):
        response1 = create_response()
        response1.json.return_value = [
            {"filename": "baz", "status": FileStatus.MODIFIED.value}
        ]
        response2 = create_response()
        response2.json.return_value = [
            {"filename": "foo", "status": FileStatus.DELETED.value},
            {"filename": "bar", "status": FileStatus.MODIFIED.value},
        ]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        files = await self.api.files("foo/bar", 123)

        self.assertEqual(len(files), 2)
        self.assertEqual(len(files[FileStatus.MODIFIED]), 2)
        self.assertEqual(len(files[FileStatus.DELETED]), 1)
        self.assertEqual(len(files[FileStatus.ADDED]), 0)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/pulls/123/files",
            params={"per_page": "100"},
        )

    async def test_files_with_status_list(self):
        response1 = create_response()
        response1.json.return_value = [
            {"filename": "baz", "status": FileStatus.MODIFIED.value}
        ]
        response2 = create_response()
        response2.json.return_value = [
            {"filename": "foo", "status": FileStatus.DELETED.value},
            {"filename": "bar", "status": FileStatus.MODIFIED.value},
        ]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        files = await self.api.files(
            "foo/bar", 123, status_list=[FileStatus.ADDED, FileStatus.MODIFIED]
        )

        self.assertEqual(len(files), 1)
        self.assertEqual(len(files[FileStatus.MODIFIED]), 2)
        self.assertEqual(len(files[FileStatus.DELETED]), 0)
        self.assertEqual(len(files[FileStatus.ADDED]), 0)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/pulls/123/files",
            params={"per_page": "100"},
        )


class GitHubPullRequestsTestCase(unittest.TestCase):
    @patch("pontos.github.api.api.httpx.get")
    def test_pull_request_commits(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = [{"sha": "1"}]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        commits = api.pull_request_commits("foo/bar", pull_request=1)

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/pulls/1/commits",
            params={"per_page": "100"},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]["sha"], "1")

    @patch("pontos.github.api.api.httpx.post")
    def test_create_pull_request(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_pull_request(
            "foo/bar",
            head_branch="foo",
            base_branch="main",
            title="Foo",
            body="This is bar",
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/pulls",
            json={
                "head": "foo",
                "base": "main",
                "title": "Foo",
                "body": "This is bar",
            },
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    def test_update_pull_request(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.update_pull_request(
            "foo/bar",
            123,
            base_branch="main",
            title="Foo",
            body="This is bar",
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/pulls/123",
            json={
                "base": "main",
                "title": "Foo",
                "body": "This is bar",
            },
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    def test_add_pull_request_comment(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.add_pull_request_comment(
            "foo/bar", pull_request=123, comment="This is a comment"
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/issues/123/comments",
            json={"body": "This is a comment"},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.get")
    def test_modified_files_in_pr(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = json.loads(
            (here / "pr-files.json").read_text(encoding="utf-8")
        )
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        files = api.pull_request_files(
            "foo/bar", pull_request=1, status_list=[FileStatus.MODIFIED]
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/pulls/1/files",
            params={"per_page": "100"},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(
            files,
            {
                FileStatus.MODIFIED: [
                    Path("gvm/protocols/gmpv2110/__init__.py"),
                    Path("tests/protocols/gmpv2110/entities/test_users.py"),
                    Path("tests/protocols/gmpv2110/entities/users/__init__.py"),
                    Path(
                        "tests/protocols/gmpv2110/"
                        "entities/users/test_modify_user.py"
                    ),
                ]
            },
        )

    @patch("pontos.github.api.api.httpx.get")
    def test_added_files_in_pr(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = json.loads(
            (here / "pr-files.json").read_text(encoding="utf-8")
        )
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        files = api.pull_request_files(
            "foo/bar", pull_request=1, status_list=[FileStatus.ADDED]
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/pulls/1/files",
            params={"per_page": "100"},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(
            files,
            {
                FileStatus.ADDED: [
                    Path("gvm/protocols/gmpv2110/entities/users.py"),
                    Path(
                        "tests/protocols/gmpv2110/entities/"
                        "users/test_create_user.py"
                    ),
                ]
            },
        )
