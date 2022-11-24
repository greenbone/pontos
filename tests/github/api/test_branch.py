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

# pylint: disable=line-too-long

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from httpx import HTTPStatusError

from pontos.github.api import GitHubRESTApi
from pontos.github.api.branch import (
    GitHubAsyncRESTBranches,
    update_from_applied_settings,
)
from pontos.github.models.branch import BranchProtection
from tests.github.api import (
    GitHubAsyncRESTTestCase,
    create_response,
    default_request,
)

here = Path(__file__).parent


class UpdateFromAppliedSettingsTestCase(unittest.TestCase):
    def test_update_from_applied_settings(self):
        branch_protection = BranchProtection.from_dict(
            {
                "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions",
                "users_url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions/users",
                "teams_url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions/teams",
                "apps_url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions/apps",
                "users": [
                    {
                        "login": "greenbonebot",
                        "id": 123,
                        "node_id": "MDQ6VXNlcjg1MjU0NjY2",
                        "avatar_url": "https://avatars.githubusercontent.com/u/85254666?v=4",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/greenbonebot",
                        "html_url": "https://github.com/greenbonebot",
                        "followers_url": "https://api.github.com/users/greenbonebot/followers",
                        "following_url": "https://api.github.com/users/greenbonebot/following{/other_user}",
                        "gists_url": "https://api.github.com/users/greenbonebot/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/greenbonebot/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/greenbonebot/subscriptions",
                        "organizations_url": "https://api.github.com/users/greenbonebot/orgs",
                        "repos_url": "https://api.github.com/users/greenbonebot/repos",
                        "events_url": "https://api.github.com/users/greenbonebot/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/greenbonebot/received_events",
                        "type": "User",
                        "site_admin": False,
                    }
                ],
                "teams": [],
                "apps": [],
                "lock_branch": {"enabled": False},
                "allow_fork_syncing": {"enabled": False},
                "required_signatures": {"enabled": False},
            }
        )

        kwargs = update_from_applied_settings(
            branch_protection=branch_protection,
            lock_branch=True,
            allow_fork_syncing=True,
            allow_deletions=True,
            allow_force_pushes=True,
        )

        self.assertTrue(kwargs["lock_branch"])
        self.assertTrue(kwargs["allow_fork_syncing"])
        self.assertTrue(kwargs["allow_deletions"])
        self.assertTrue(kwargs["allow_force_pushes"])

        self.assertFalse(kwargs["required_signatures"])

        self.assertIsNone(kwargs["required_linear_history"])
        self.assertIsNone(kwargs["block_creations"])
        self.assertIsNone(kwargs["required_conversation_resolution"])
        self.assertIsNone(kwargs["enforce_admins"])


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
            "url": "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
            "required_signatures": {
                "url": "https://api.github.com/repos/octocat/Hello-World/branches/main/protection/required_signatures",
                "enabled": False,
            },
            "enforce_admins": {
                "url": "https://api.github.com/repos/octocat/Hello-World/branches/main/protection/enforce_admins",
                "enabled": False,
            },
        }
        response = create_response()
        response.json.return_value = rules

        self.client.get.return_value = response

        data = await self.api.protection_rules("foo/bar", "baz")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection"
        )
        self.assertEqual(
            data.url,
            "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        )

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

    async def test_update_protection_rules_defaults(self):
        response = create_response()
        response.json.return_value = {
            "url": "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        }
        self.client.put.return_value = response

        rules = await self.api.update_protection_rules(
            "foo/bar",
            "baz",
        )
        self.client.put.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection",
            data={
                "required_status_checks": None,
                "enforce_admins": None,
                "required_pull_request_reviews": None,
                "restrictions": None,
            },
        )

        self.assertEqual(
            rules.url,
            "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        )

    async def test_update_protection_rules(self):
        response = create_response()
        response.json.return_value = {
            "url": "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        }
        self.client.put.return_value = response

        rules = await self.api.update_protection_rules(
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

        self.assertEqual(
            rules.url,
            "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        )

    async def test_update_protection_defaults(self):
        response = create_response()
        response.json.return_value = {
            "url": "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        }
        self.client.put.return_value = response

        rules = await self.api.update_protection_rules(
            "foo/bar",
            "baz",
        )

        self.client.put.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection",
            data={
                "required_status_checks": None,
                "enforce_admins": None,
                "required_pull_request_reviews": None,
                "restrictions": None,
            },
        )

        self.assertEqual(
            rules.url,
            "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        )

    async def test_update_protection_rules_up_to_date_branch(self):
        response = create_response()
        response.json.return_value = {
            "url": "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        }
        self.client.put.return_value = response

        rules = await self.api.update_protection_rules(
            "foo/bar",
            "baz",
            require_branches_to_be_up_to_date=True,
        )

        self.client.put.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection",
            data={
                "required_status_checks": {
                    "strict": True,
                    "checks": [],
                },
                "enforce_admins": None,
                "required_pull_request_reviews": None,
                "restrictions": None,
            },
        )

        self.assertEqual(
            rules.url,
            "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        )

    async def test_update_protection_rules_restriction_users(self):
        response = create_response()
        response.json.return_value = {
            "url": "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        }
        self.client.put.return_value = response

        rules = await self.api.update_protection_rules(
            "foo/bar", "baz", restrictions_users=["foo", "bar"]
        )

        self.client.put.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection",
            data={
                "enforce_admins": None,
                "required_pull_request_reviews": None,
                "required_status_checks": None,
                "restrictions": {"users": ["foo", "bar"], "teams": []},
            },
        )

        self.assertEqual(
            rules.url,
            "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        )

    async def test_update_protection_rules_restriction_teams(self):
        response = create_response()
        response.json.return_value = {
            "url": "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
        }
        self.client.put.return_value = response

        rules = await self.api.update_protection_rules(
            "foo/bar", "baz", restrictions_teams=["foo", "bar"]
        )

        self.client.put.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection",
            data={
                "enforce_admins": None,
                "required_pull_request_reviews": None,
                "required_status_checks": None,
                "restrictions": {"teams": ["foo", "bar"], "users": []},
            },
        )

        self.assertEqual(
            rules.url,
            "https://api.github.com/repos/octocat/Hello-World/branches/main/protection",
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
            data={
                "enforce_admins": True,
                "required_status_checks": None,
                "required_pull_request_reviews": None,
                "restrictions": None,
            },
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

    async def test_update_required_status_checks(self):
        response = create_response()
        self.client.patch.return_value = response

        await self.api.update_required_status_checks(
            "foo/bar",
            "baz",
            required_status_checks=[("foo", "123"), ("bar", None)],
            require_branches_to_be_up_to_date=True,
        )

        self.client.patch.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection/required_status_checks",
            data={
                "strict": True,
                "checks": [
                    {"context": "foo", "app_id": "123"},
                    {"context": "bar"},
                ],
            },
        )

    async def test_remove_required_required_status_checks(self):
        response = create_response()
        self.client.delete.return_value = response

        await self.api.remove_required_status_checks("foo/bar", "baz")

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection/required_status_checks"
        )

    async def test_remove_required_required_status_checks_failure(self):
        response = create_response()
        error = HTTPStatusError("404", request=MagicMock(), response=response)
        response.raise_for_status.side_effect = error

        self.client.delete.return_value = response

        with self.assertRaises(HTTPStatusError):
            await self.api.remove_required_status_checks("foo/bar", "baz")

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/branches/baz/protection/required_status_checks"
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
