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

# pylint: disable=too-many-lines

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import httpx

from pontos.github.api import FileStatus, GitHubRESTApi
from pontos.helper import DEFAULT_TIMEOUT

here = Path(__file__).parent


class GitHubApiTestCase(unittest.TestCase):
    @patch("pontos.github.api.httpx.get")
    def test_branch_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.ok = True
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.branch_exists("foo/bar", "main")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/branches/main",
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
        )
        self.assertTrue(exists)

    @patch("pontos.github.api.httpx.get")
    def test_branch_not_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.is_success = False
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.branch_exists("foo/bar", "main")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/branches/main",
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
        )
        self.assertFalse(exists)

    @patch("pontos.github.api.httpx.get")
    def test_pull_request_commits(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = [{"sha": "1"}]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        commits = api.pull_request_commits("foo/bar", pull_request=1)

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/pulls/1/commits",
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params={"per_page": "100"},
            follow_redirects=True,
        )

        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]["sha"], "1")

    @patch("pontos.github.api.httpx.post")
    def test_create_pull_request(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_pull_request(
            "foo/bar",
            head_branch="foo",
            base_branch="main",
            title="Foo",
            body="This is bar",
        )

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/pulls",
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
            json={
                "head": "foo",
                "base": "main",
                "title": "Foo",
                "body": "This is bar",
            },
        )

    @patch("pontos.github.api.httpx.post")
    def test_update_pull_request(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.update_pull_request(
            "foo/bar",
            123,
            base_branch="main",
            title="Foo",
            body="This is bar",
        )

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/pulls/123",
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
            json={
                "base": "main",
                "title": "Foo",
                "body": "This is bar",
            },
        )

    @patch("pontos.github.api.httpx.post")
    def test_add_pull_request_comment(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.add_pull_request_comment(
            "foo/bar", pull_request=123, comment="This is a comment"
        )

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/issues/123/comments",
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
            json={"body": "This is a comment"},
        )

    @patch("pontos.github.api.httpx.delete")
    def test_delete_branch(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.delete_branch("foo/bar", "foo")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/git/refs/foo",
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
        )

    @patch("pontos.github.api.httpx.post")
    def test_create_release(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_release(
            "foo/bar",
            "v1.2.3",
            name="Foo v1.2.3",
            body="This is a release",
        )

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/releases",
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
            json={
                "tag_name": "v1.2.3",
                "name": "Foo v1.2.3",
                "body": "This is a release",
                "draft": False,
                "prerelease": False,
            },
        )

    @patch("pontos.github.api.httpx.get")
    def test_release_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.ok = True
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.release_exists("foo/bar", "v1.2.3")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/releases/tags/v1.2.3",
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
        )
        self.assertTrue(exists)

    @patch("pontos.github.api.httpx.get")
    def test_release(self, requests_mock: MagicMock):
        response = MagicMock()
        response.json.return_value = json.loads(
            (here / "release-response.json").read_text(encoding="utf-8")
        )

        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        data = api.release("greenbone/pontos", "v21.11.0")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0",  # pylint: disable=line-too-long
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
        )

        self.assertEqual(data["id"], 52499047)

    @patch("pontos.helper.Path")
    @patch("pontos.github.api.httpx.stream")
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
            requests_mock.assert_called_once_with(
                "GET",
                "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz",  # pylint: disable=line-too-long
                headers=None,
                params=None,
                follow_redirects=True,
                timeout=DEFAULT_TIMEOUT,
            )
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
    @patch("pontos.github.api.httpx.stream")
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
            requests_mock.assert_called_once_with(
                "GET",
                "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz",  # pylint: disable=line-too-long
                params=None,
                headers=None,
                follow_redirects=True,
                timeout=DEFAULT_TIMEOUT,
            )
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
    @patch("pontos.github.api.httpx.stream")
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
            requests_mock.assert_called_once_with(
                "GET",
                "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.zip",  # pylint: disable=line-too-long
                follow_redirects=True,
                headers=None,
                params=None,
                timeout=DEFAULT_TIMEOUT,
            )
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

    @patch("pontos.github.api.httpx.get")
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

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/pulls/1/files",
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params={"per_page": "100"},
        )

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

    @patch("pontos.github.api.httpx.get")
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

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/pulls/1/files",
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params={"per_page": "100"},
        )

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

    @patch("pontos.helper.Path")
    @patch("pontos.github.api.httpx.get")
    @patch("pontos.github.api.httpx.stream")
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

        request_mock.assert_has_calls(
            [
                call(
                    "https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0",  # pylint: disable=line-too-long
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token 12345",
                    },
                    params=None,
                    follow_redirects=True,
                ),
                call().raise_for_status(),
                call().json(),
                call(
                    "https://api.github.com/repos/greenbone/pontos/releases/52499047/assets",  # pylint: disable=line-too-long
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token 12345",
                    },
                    params=None,
                    follow_redirects=True,
                ),
                call().raise_for_status(),
                call().json(),
            ]
        )

    @patch("pontos.github.api.Path")
    @patch("pontos.github.api.httpx.get")
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

    @patch("pontos.github.api.Path")
    @patch("pontos.github.api.httpx.get")
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

    @patch("pontos.github.api.httpx.post")
    @patch("pontos.github.api.httpx.get")
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
        uploaded_file = next(upload_it)
        post_mock.assert_called_with(
            "https://uploads.github.com/repos/greenbone/pontos/releases/52499047/assets",  # pylint: disable=line-too-long
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
                "Content-Type": "application/octet-stream",
            },
            params={"name": "foo.txt"},
            follow_redirects=True,
            content=content1,
        )
        self.assertEqual(uploaded_file, file1)

        uploaded_file = next(upload_it)
        post_mock.assert_called_with(
            "https://uploads.github.com/repos/greenbone/pontos/releases/52499047/assets",  # pylint: disable=line-too-long
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
                "Content-Type": "application/octet-stream",
            },
            params={"name": "bar.pdf"},
            follow_redirects=True,
            content=content2,
        )
        self.assertEqual(uploaded_file, file2)

        get_mock.assert_called_once_with(
            "https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0",  # pylint: disable=line-too-long
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
        )

    @patch("pontos.github.api.httpx.post")
    @patch("pontos.github.api.httpx.get")
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

        get_mock.assert_called_once_with(
            "https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0",  # pylint: disable=line-too-long
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
        )

    @patch("pontos.github.api.httpx.post")
    @patch("pontos.github.api.httpx.get")
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
        post_mock.assert_called_with(
            "https://uploads.github.com/repos/greenbone/pontos/releases/52499047/assets",  # pylint: disable=line-too-long
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
                "Content-Type": "application/octet-stream",
            },
            params={"name": "foo.txt"},
            follow_redirects=True,
            content=content1,
        )
        self.assertEqual(uploaded_file, file1)

        with self.assertRaises(httpx.HTTPError):
            next(upload_it)

        get_mock.assert_called_once_with(
            "https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0",  # pylint: disable=line-too-long
            follow_redirects=True,
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params=None,
        )

    @patch("pontos.github.api.httpx.get")
    def test_get_repository_artifacts(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "artifacts": [
                {
                    "id": 11,
                    "node_id": "MDg6QXJ0aWZhY3QxMQ==",
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_repository_artifacts("foo/bar")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/artifacts",
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params={"per_page": 100, "page": 1},
            follow_redirects=True,
        )

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.httpx.get")
    def test_get_repository_artifacts_with_pagination(
        self, requests_mock: MagicMock
    ):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "artifacts": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "artifacts": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(100, 120)
                ],
            },
        ]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_repository_artifacts("foo/bar")

        requests_mock.assert_has_calls(
            [
                call.__bool__(),
                call(
                    "https://api.github.com/repos/foo/bar/actions/artifacts",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token 12345",
                    },
                    params={"per_page": 100, "page": 1},
                    follow_redirects=True,
                ),
                call().raise_for_status(),
                call().json(),
                call.__bool__(),
                call(
                    "https://api.github.com/repos/foo/bar/actions/artifacts",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token 12345",
                    },
                    params={"per_page": 100, "page": 2},
                    follow_redirects=True,
                ),
                call().raise_for_status(),
                call().json(),
            ]
        )

        self.assertEqual(len(artifacts), 120)
        self.assertEqual(artifacts[0]["name"], "Foo-0")
        self.assertEqual(artifacts[119]["name"], "Foo-119")

    @patch("pontos.github.api.httpx.get")
    def test_get_repository_artifact(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.json.return_value = {
            "id": 123,
            "name": "Foo",
        }

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_repository_artifact("foo/bar", "123")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
            },
            params=None,
            follow_redirects=True,
        )

        self.assertEqual(artifacts["id"], 123)
        self.assertEqual(artifacts["name"], "Foo")

    @patch("pontos.github.api.httpx.get")
    def test_get_repository_artifact_invalid(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Testing Status Message", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.get_repository_artifact("foo/bar", "123")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
            },
            params=None,
            follow_redirects=True,
        )

    @patch("pontos.helper.Path")
    @patch("pontos.github.api.httpx.stream")
    def test_download_repository_artifact(
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
        with api.download_repository_artifact(
            "foo/bar", "123", download_file
        ) as download_progress:
            requests_mock.assert_called_once_with(
                "GET",
                "https://api.github.com/repos/foo/bar/actions/artifacts/123/zip",  # pylint: disable=line-too-long
                timeout=DEFAULT_TIMEOUT,
                follow_redirects=True,
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "Authorization": "token 12345",
                },
                params=None,
            )
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

    @patch("pontos.github.api.httpx.get")
    def test_get_workflow_artifacts(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "artifacts": [
                {
                    "id": 11,
                    "node_id": "MDg6QXJ0aWZhY3QxMQ==",
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_artifacts("foo/bar", "123")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/runs/123/artifacts",
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params={"per_page": 100, "page": 1},
            follow_redirects=True,
        )

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.httpx.get")
    def test_get_workflow_artifacts_with_pagination(
        self, requests_mock: MagicMock
    ):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "artifacts": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "artifacts": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(100, 120)
                ],
            },
        ]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_artifacts("foo/bar", "123")

        requests_mock.assert_has_calls(
            [
                call.__bool__(),
                call(
                    "https://api.github.com/repos/foo/bar/actions/runs/123/"
                    "artifacts",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token 12345",
                    },
                    params={"per_page": 100, "page": 1},
                    follow_redirects=True,
                ),
                call().raise_for_status(),
                call().json(),
                call.__bool__(),
                call(
                    "https://api.github.com/repos/foo/bar/actions/runs/123/"
                    "artifacts",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token 12345",
                    },
                    params={"per_page": 100, "page": 2},
                    follow_redirects=True,
                ),
                call().raise_for_status(),
                call().json(),
            ]
        )

        self.assertEqual(len(artifacts), 120)
        self.assertEqual(artifacts[0]["name"], "Foo-0")
        self.assertEqual(artifacts[119]["name"], "Foo-119")

    @patch("pontos.github.api.httpx.delete")
    def test_delete_repository_artifact(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.delete_repository_artifact("foo/bar", "123")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
            },
            params=None,
            follow_redirects=True,
        )

    @patch("pontos.github.api.httpx.delete")
    def test_delete_repository_artifact_failure(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Delete Failed", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.delete_repository_artifact("foo/bar", "123")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
            },
            params=None,
            follow_redirects=True,
        )

    @patch("pontos.github.api.httpx.get")
    def test_get_workflows(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflows": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflows("foo/bar")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/workflows",
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params={"per_page": 100, "page": 1},
            follow_redirects=True,
        )

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.httpx.get")
    def test_get_workflows_with_pagination(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "workflows": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "workflows": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(100, 120)
                ],
            },
        ]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflows("foo/bar")

        requests_mock.assert_has_calls(
            [
                call.__bool__(),
                call(
                    "https://api.github.com/repos/foo/bar/actions/workflows",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token 12345",
                    },
                    params={"per_page": 100, "page": 1},
                    follow_redirects=True,
                ),
                call().raise_for_status(),
                call().json(),
                call.__bool__(),
                call(
                    "https://api.github.com/repos/foo/bar/actions/workflows",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token 12345",
                    },
                    params={"per_page": 100, "page": 2},
                    follow_redirects=True,
                ),
                call().raise_for_status(),
                call().json(),
            ]
        )

        self.assertEqual(len(artifacts), 120)
        self.assertEqual(artifacts[0]["name"], "Foo-0")
        self.assertEqual(artifacts[119]["name"], "Foo-119")

    @patch("pontos.github.api.httpx.get")
    def test_get_workflow(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.json.return_value = {
            "id": 123,
            "name": "Foo",
        }

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow("foo/bar", "123")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/workflows/123",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
            },
            params=None,
            follow_redirects=True,
        )

        self.assertEqual(artifacts["id"], 123)
        self.assertEqual(artifacts["name"], "Foo")

    @patch("pontos.github.api.httpx.get")
    def test_get_workflow_invalid(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Testing Status Message", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.get_workflow("foo/bar", "123")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/workflows/123",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
            },
            params=None,
            follow_redirects=True,
        )

    @patch("pontos.github.api.httpx.post")
    def test_create_workflow_dispatch(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_workflow_dispatch("foo/bar", "123", ref="main")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/workflows/123"
            "/dispatches",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
            },
            params=None,
            follow_redirects=True,
            json={"ref": "main"},
        )

    @patch("pontos.github.api.httpx.post")
    def test_create_workflow_dispatch_failure(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Dispatch Failed", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.create_workflow_dispatch("foo/bar", "123", ref="main")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/workflows/123"
            "/dispatches",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
            },
            params=None,
            follow_redirects=True,
            json={"ref": "main"},
        )

    @patch("pontos.github.api.httpx.get")
    def test_get_workflow_runs(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflow_runs": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_runs("foo/bar")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/runs",
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params={"per_page": 100, "page": 1},
            follow_redirects=True,
        )

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.httpx.get")
    def test_get_workflow_runs_with_pagination(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "workflow_runs": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "workflow_runs": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(100, 120)
                ],
            },
        ]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_runs("foo/bar")

        requests_mock.assert_has_calls(
            [
                call.__bool__(),
                call(
                    "https://api.github.com/repos/foo/bar/actions/runs",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token 12345",
                    },
                    params={"per_page": 100, "page": 1},
                    follow_redirects=True,
                ),
                call().raise_for_status(),
                call().json(),
                call.__bool__(),
                call(
                    "https://api.github.com/repos/foo/bar/actions/runs",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token 12345",
                    },
                    params={"per_page": 100, "page": 2},
                    follow_redirects=True,
                ),
                call().raise_for_status(),
                call().json(),
            ]
        )

        self.assertEqual(len(artifacts), 120)
        self.assertEqual(artifacts[0]["name"], "Foo-0")
        self.assertEqual(artifacts[119]["name"], "Foo-119")

    @patch("pontos.github.api.httpx.get")
    def test_get_workflow_runs_for_workflow(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflow_runs": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_runs("foo/bar", "foo")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/workflows/foo/runs",
            headers={
                "Authorization": "token 12345",
                "Accept": "application/vnd.github.v3+json",
            },
            params={"per_page": 100, "page": 1},
            follow_redirects=True,
        )

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.httpx.get")
    def test_get_workflow_run(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.json.return_value = {
            "id": 123,
            "name": "Foo",
        }

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_run("foo/bar", "123")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/runs/123",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
            },
            params=None,
            follow_redirects=True,
        )

        self.assertEqual(artifacts["id"], 123)
        self.assertEqual(artifacts["name"], "Foo")

    @patch("pontos.github.api.httpx.get")
    def test_get_workflow_run_invalid(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Workflow Run Not Found", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.get_workflow_run("foo/bar", "123")

        requests_mock.assert_called_once_with(
            "https://api.github.com/repos/foo/bar/actions/runs/123",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token 12345",
            },
            params=None,
            follow_redirects=True,
        )
