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

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from httpx import HTTPStatusError

from pontos.github.api import GitHubRESTApi
from pontos.github.api.branch import GitHubAsyncRESTBranches
from tests.github.api import (
    GitHubAsyncRESTTestCase,
    create_response,
    default_request,
)

here = Path(__file__).parent


class GitHubAsyncRESTBranchesTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTBranches

    async def test_exists(self):
        response = create_response(is_success=True)
        self.client.get.return_value = response

        self.assertTrue(await self.api.exists("foo/bar", "baz"))
        self.client.get.assert_awaited_once_with("/repos/foo/bar/branches/baz")

    async def test_not_exists(self):
        response = create_response(is_success=False)
        self.client.get.return_value = response

        self.assertFalse(await self.api.exists("foo/bar", "baz"))
        self.client.get.assert_awaited_once_with("/repos/foo/bar/branches/baz")

    async def test_delete_branch(self):
        response = create_response()
        self.client.delete.return_value = response

        await self.api.delete("foo/bar", "baz")

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/git/refs/baz"
        )

    async def test_delete_branch_failure(self):
        response = create_response()
        error = HTTPStatusError("404", request=MagicMock(), response=response)
        response.raise_for_status.side_effect = error

        self.client.delete.return_value = response

        with self.assertRaises(HTTPStatusError):
            await self.api.delete("foo/bar", "baz")

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/git/refs/baz"
        )

    async def test_protection_rules(self):
        rules = {
            "required_status_checks": {},
            "enforce_admins": {},
            "required_pull_request_reviews": {},
        }
        response = create_response()
        response.json.return_value = rules

        self.client.get.return_value = response

        data = await self.api.protection_rules("foo/bar", "baz")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection"
        )
        self.assertEqual(data, rules)

    async def test_protection_rules_failure(self):
        response = create_response()
        error = HTTPStatusError("404", request=MagicMock(), response=response)
        response.raise_for_status.side_effect = error

        self.client.get.return_value = response

        with self.assertRaises(HTTPStatusError):
            await self.api.protection_rules("foo/bar", "baz")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection"
        )


class GitHubBranchTestCase(unittest.TestCase):
    @patch("pontos.github.api.api.httpx.get")
    def test_branch_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.ok = True
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.branch_exists("foo/bar", "main")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/branches/main",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
        self.assertTrue(exists)

    @patch("pontos.github.api.api.httpx.get")
    def test_branch_not_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.is_success = False
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.branch_exists("foo/bar", "main")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/branches/main",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
        self.assertFalse(exists)

    @patch("pontos.github.api.api.httpx.delete")
    def test_delete_branch(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.delete_branch("foo/bar", "foo")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/git/refs/foo",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.get")
    def test_branch_protection_rules(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.branch_protection_rules(repo="foo/bar", branch="baz")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/branches/baz/protection",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
