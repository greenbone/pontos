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
from unittest.mock import patch, MagicMock

from pontos.github.api import (
    FileStatus,
    GitHubRESTApi,
    DEFAULT_TIMEOUT,
    download,
)

here = Path(__file__).parent


class GitHubApiTestCase(unittest.TestCase):
    @patch("pontos.github.api.requests.get")
    def test_branch_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.ok = True
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.branch_exists("foo/bar", "main")

        requests_mock.assert_called_once_with(
            'https://api.github.com/repos/foo/bar/branches/main',
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params=None,
            json=None,
        )
        self.assertTrue(exists)

    @patch("pontos.github.api.requests.get")
    def test_branch_not_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.ok = False
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.branch_exists("foo/bar", "main")

        requests_mock.assert_called_once_with(
            'https://api.github.com/repos/foo/bar/branches/main',
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params=None,
            json=None,
        )
        self.assertFalse(exists)

    @patch("pontos.github.api.requests.get")
    def test_pull_request_commits(self, requests_mock: MagicMock):
        response = MagicMock()
        response.json.return_value = [{"sha": "1"}]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        commits = api.pull_request_commits("foo/bar", pull_request=1)

        requests_mock.assert_called_once_with(
            'https://api.github.com/repos/foo/bar/pulls/1/commits',
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params={'per_page': '100'},
            json=None,
        )

        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]["sha"], "1")

    @patch("pontos.github.api.requests.post")
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
            'https://api.github.com/repos/foo/bar/pulls',
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params=None,
            json={
                'head': 'foo',
                'base': 'main',
                'title': 'Foo',
                'body': 'This is bar',
            },
        )

    @patch("pontos.github.api.requests.post")
    def test_add_pull_request_comment(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.add_pull_request_comment(
            "foo/bar", pull_request=123, comment="This is a comment"
        )

        requests_mock.assert_called_once_with(
            'https://api.github.com/repos/foo/bar/issues/123/comments',
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params=None,
            json={'body': 'This is a comment'},
        )

    @patch("pontos.github.api.requests.delete")
    def test_delete_branch(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.delete_branch("foo/bar", "foo")

        requests_mock.assert_called_once_with(
            'https://api.github.com/repos/foo/bar/git/refs/foo',
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params=None,
            json=None,
        )

    @patch("pontos.github.api.requests.post")
    def test_create_release(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_release(
            "foo/bar",
            "v1.2.3",
            name="Foo v1.2.3",
            body="This is a release",
        )

        requests_mock.assert_called_once_with(
            'https://api.github.com/repos/foo/bar/releases',
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params=None,
            json={
                'tag_name': 'v1.2.3',
                'target_commitish': None,
                'name': 'Foo v1.2.3',
                'body': 'This is a release',
                'draft': False,
                'prerelease': False,
            },
        )

    @patch("pontos.github.api.requests.get")
    def test_release_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.ok = True
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.release_exists("foo/bar", "v1.2.3")

        requests_mock.assert_called_once_with(
            'https://api.github.com/repos/foo/bar/releases/tags/v1.2.3',
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params=None,
            json=None,
        )
        self.assertTrue(exists)

    @patch("pontos.github.api.requests.get")
    def test_release(self, requests_mock: MagicMock):
        response = MagicMock()
        response.json.return_value = json.loads(
            (here / "release-response.json").read_text(encoding="utf-8")
        )

        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        data = api.release("greenbone/pontos", "v21.11.0")

        requests_mock.assert_called_once_with(
            'https://api.github.com/repos/greenbone/pontos/releases/tags/v21.11.0',  # pylint: disable=line-too-long
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params=None,
            json=None,
        )

        self.assertEqual(data["id"], 52499047)

    @patch("pontos.github.api.Path")
    @patch("pontos.github.api.requests.get")
    def test_download_release_tarball(
        self, requests_mock: MagicMock, path_mock: MagicMock
    ):
        response = MagicMock()
        response.iter_content.return_value = ["foo", "bar", "baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = None
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        download_file = path_mock()
        download_progress = api.download_release_tarball(
            "greenbone/pontos", "v21.11.0", download_file
        )

        requests_mock.assert_called_once_with(
            'https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz',  # pylint: disable=line-too-long
            stream=True,
            timeout=DEFAULT_TIMEOUT,
        )
        response_headers.get.assert_called_once_with('content-length')

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

    @patch("pontos.github.api.Path")
    @patch("pontos.github.api.requests.get")
    def test_download_release_tarball_with_content_length(
        self, requests_mock: MagicMock, path_mock: MagicMock
    ):
        response = MagicMock()
        response.iter_content.return_value = ["foo", "bar", "baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = "9"
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        download_file = path_mock()
        download_progress = api.download_release_tarball(
            "greenbone/pontos", "v21.11.0", download_file
        )

        requests_mock.assert_called_once_with(
            'https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz',  # pylint: disable=line-too-long
            stream=True,
            timeout=DEFAULT_TIMEOUT,
        )
        response_headers.get.assert_called_once_with('content-length')

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

    @patch("pontos.github.api.Path")
    @patch("pontos.github.api.requests.get")
    def test_download_release_zip(
        self, requests_mock: MagicMock, path_mock: MagicMock
    ):
        response = MagicMock()
        response.iter_content.return_value = ["foo", "bar", "baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = None
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        download_file = path_mock()
        download_progress = api.download_release_zip(
            "greenbone/pontos", "v21.11.0", download_file
        )

        requests_mock.assert_called_once_with(
            'https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.zip',  # pylint: disable=line-too-long
            stream=True,
            timeout=DEFAULT_TIMEOUT,
        )
        response_headers.get.assert_called_once_with('content-length')

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

    @patch("pontos.github.api.requests.get")
    def test_modified_files_in_pr(self, requests_mock: MagicMock):
        response = MagicMock()
        response.json.return_value = json.loads(
            (here / "pr-files.json").read_text(encoding="utf-8")
        )
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        files = api.pull_request_files(
            "foo/bar", pull_request=1, status_list=[FileStatus.MODIFIED]
        )

        requests_mock.assert_called_once_with(
            'https://api.github.com/repos/foo/bar/pulls/1/files',
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params={'per_page': '100'},
            json=None,
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

    @patch("pontos.github.api.requests.get")
    def test_added_files_in_pr(self, requests_mock: MagicMock):
        response = MagicMock()
        response.json.return_value = json.loads(
            (here / "pr-files.json").read_text(encoding="utf-8")
        )
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        files = api.pull_request_files(
            "foo/bar", pull_request=1, status_list=[FileStatus.ADDED]
        )

        requests_mock.assert_called_once_with(
            'https://api.github.com/repos/foo/bar/pulls/1/files',
            headers={
                'Authorization': 'token 12345',
                'Accept': 'application/vnd.github.v3+json',
            },
            params={'per_page': '100'},
            json=None,
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


class DownloadTestCase(unittest.TestCase):
    @patch("pontos.github.api.requests.get")
    def test_download_without_destination(
        self,
        requests_mock: MagicMock,
    ):
        response = MagicMock()
        response.iter_content.return_value = [b"foo", b"bar", b"baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = None
        requests_mock.return_value = response

        download_progress = download(
            "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz"  # pylint: disable=line-too-long
        )

        requests_mock.assert_called_once_with(
            'https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz',  # pylint: disable=line-too-long
            stream=True,
            timeout=DEFAULT_TIMEOUT,
        )
        response_headers.get.assert_called_once_with('content-length')

        self.assertIsNone(download_progress.length)
        self.assertEqual(download_progress.destination, Path("v21.11.0.tar.gz"))

        it = iter(download_progress)
        progress = next(it)
        self.assertIsNone(progress)
        progress = next(it)
        self.assertIsNone(progress)
        progress = next(it)
        self.assertIsNone(progress)

        with self.assertRaises(StopIteration):
            next(it)

        download_progress.destination.unlink()

    @patch("pontos.github.api.Path")
    @patch("pontos.github.api.requests.get")
    def test_download_with_content_length(
        self, requests_mock: MagicMock, path_mock: MagicMock
    ):
        response = MagicMock()
        response.iter_content.return_value = ["foo", "bar", "baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = "9"
        requests_mock.return_value = response

        download_file = path_mock()
        file_mock = MagicMock()
        file_mock.__enter__.return_value = file_mock
        download_file.open.return_value = file_mock

        download_progress = download(
            "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz",  # pylint: disable=line-too-long
            download_file,
        )

        requests_mock.assert_called_once_with(
            "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz",  # pylint: disable=line-too-long
            stream=True,
            timeout=DEFAULT_TIMEOUT,
        )
        response_headers.get.assert_called_once_with('content-length')

        self.assertEqual(download_progress.length, 9)

        it = iter(download_progress)

        progress = next(it)
        self.assertEqual(progress, 1 / 3)
        file_mock.write.assert_called_with("foo")

        progress = next(it)
        self.assertEqual(progress, 2 / 3)
        file_mock.write.assert_called_with("bar")

        progress = next(it)
        self.assertEqual(progress, 1)
        file_mock.write.assert_called_with("baz")

        with self.assertRaises(StopIteration):
            next(it)
