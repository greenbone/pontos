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

from pontos.github.api import GitHubRESTApi
from pontos.github.api.helper import FileStatus
from tests.github.api import default_request

here = Path(__file__).parent


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
