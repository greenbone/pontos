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

    async def test_delete_protection_rules(self):
        response = create_response()
        self.client.delete.return_value = response

        await self.api.delete_protection_rules("foo/bar", "baz")

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection"
        )

    async def test_delete_protection_rules_failure(self):
        response = create_response()
        error = HTTPStatusError("404", request=MagicMock(), response=response)
        response.raise_for_status.side_effect = error

        self.client.delete.return_value = response

        with self.assertRaises(HTTPStatusError):
            await self.api.delete_protection_rules("foo/bar", "baz")

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection"
        )

    async def test_update_protection_rules(self):
        response = create_response()
        self.client.put.return_value = response

        await self.api.update_protection_rules(
            "foo/bar",
            "baz",
            required_status_checks=[("foo", "123"), ("bar", None)],
            require_branches_to_be_up_to_date=True,
            enforce_admins=True,
            dismissal_restrictions_users=("foo", "bar"),
            dismissal_restrictions_teams=("team_foo", "team_bar"),
            dismissal_restrictions_apps=("123", "321"),
            dismiss_stale_reviews=True,
            require_code_owner_reviews=True,
            required_approving_review_count=2,
            require_last_push_approval=True,
            bypass_pull_request_allowances_users=("foo", "bar"),
            bypass_pull_request_allowances_teams=("team_foo", "team_bar"),
            bypass_pull_request_allowances_apps=("123", "321"),
            restrictions_users=("foo", "bar"),
            restrictions_teams=("team_foo", "team_bar"),
            restrictions_apps=("123", "321"),
            required_linear_history=True,
            allow_force_pushes=True,
            allow_deletions=True,
            block_creations=True,
            required_conversation_resolution=True,
            lock_branch=True,
            allow_fork_syncing=True,
        )

        self.client.put.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection",
            data={
                "required_status_checks": {
                    "strict": True,
                    "checks": [
                        {"context": "foo", "app_id": "123"},
                        {"context": "bar"},
                    ],
                },
                "enforce_admins": True,
                "required_pull_request_reviews": {
                    "dismissal_restrictions": {
                        "users": ["foo", "bar"],
                        "teams": ["team_foo", "team_bar"],
                        "apps": ["123", "321"],
                    },
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": True,
                    "required_approving_review_count": 2,
                    "require_last_push_approval": True,
                    "bypass_pull_request_allowances": {
                        "users": ["foo", "bar"],
                        "teams": ["team_foo", "team_bar"],
                        "apps": ["123", "321"],
                    },
                },
                "restrictions": {
                    "users": ["foo", "bar"],
                    "teams": ["team_foo", "team_bar"],
                    "apps": ["123", "321"],
                },
                "required_linear_history": True,
                "allow_force_pushes": True,
                "allow_deletions": True,
                "block_creations": True,
                "required_conversation_resolution": True,
                "lock_branch": True,
                "allow_fork_syncing": True,
            },
        )

    async def test_update_protection_rules_failure(self):
        response = create_response()
        error = HTTPStatusError("404", request=MagicMock(), response=response)
        response.raise_for_status.side_effect = error

        self.client.put.return_value = response

        with self.assertRaises(HTTPStatusError):
            await self.api.update_protection_rules(
                "foo/bar",
                "baz",
                enforce_admins=True,
            )

        self.client.put.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection",
            data={"enforce_admins": True},
        )

    async def test_enable_enforce_admins(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.set_enforce_admins("foo/bar", "baz", enforce_admins=True)

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection/enforce_admins"
        )

    async def test_disable_enforce_admins(self):
        response = create_response()
        self.client.delete.return_value = response

        await self.api.set_enforce_admins(
            "foo/bar", "baz", enforce_admins=False
        )

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection/enforce_admins"
        )

    async def test_enable_required_signatures(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.set_required_signatures(
            "foo/bar", "baz", required_signatures=True
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection/required_signatures"
        )

    async def test_disable_required_signatures(self):
        response = create_response()
        self.client.delete.return_value = response

        await self.api.set_required_signatures(
            "foo/bar", "baz", required_signatures=False
        )

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection/required_signatures"
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
