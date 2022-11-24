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

from pontos.github.api.teams import TeamPrivacy
from pontos.github.models.base import Permission
from pontos.github.models.branch import (
    BranchProtection,
    RequiredPullRequestReviews,
    RequiredStatusChecks,
    Restrictions,
)


class RestrictionsTestCase(unittest.TestCase):
    def test_from_dict(self):
        data = {
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
        }

        restrictions = Restrictions.from_dict(data)
        self.assertEqual(
            restrictions.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions",
        )
        self.assertEqual(
            restrictions.users_url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions/users",
        )
        self.assertEqual(
            restrictions.teams_url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions/teams",
        )
        self.assertEqual(
            restrictions.apps_url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions/apps",
        )
        user = restrictions.users[0]
        self.assertEqual(len(restrictions.users), 1)
        self.assertEqual(user.login, "greenbonebot")
        self.assertEqual(user.node_id, "MDQ6VXNlcjg1MjU0NjY2")
        self.assertEqual(
            user.avatar_url,
            "https://avatars.githubusercontent.com/u/85254666?v=4",
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/greenbonebot")
        self.assertEqual(user.html_url, "https://github.com/greenbonebot")
        self.assertEqual(
            user.followers_url,
            "https://api.github.com/users/greenbonebot/followers",
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/greenbonebot/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/greenbonebot/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/greenbonebot/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/greenbonebot/subscriptions",
        )
        self.assertEqual(
            user.organizations_url,
            "https://api.github.com/users/greenbonebot/orgs",
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/greenbonebot/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/greenbonebot/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/greenbonebot/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertEqual(user.site_admin, False)
        self.assertEqual(restrictions.teams, [])
        self.assertEqual(restrictions.apps, [])


class RequiredStatusChecksTestCase(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_status_checks",
            "strict": True,
            "checks": [
                {"context": "unittests", "app_id": 123},
                {"context": "linting"},
            ],
        }

        checks = RequiredStatusChecks.from_dict(data)

        self.assertEqual(
            checks.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_status_checks",
        )
        self.assertTrue(checks.strict)
        self.assertEqual(len(checks.checks), 2)
        self.assertEqual(checks.checks[0].context, "unittests")
        self.assertEqual(checks.checks[0].app_id, 123)
        self.assertEqual(checks.checks[1].context, "linting")
        self.assertIsNone(checks.checks[1].app_id)


class RequiredPullRequestReviewsTestCase(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_pull_request_reviews",
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "require_last_push_approval": True,
            "required_approving_review_count": 1,
            "dismissal_restrictions": {
                "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions",
                "users_url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions/users",
                "teams_url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions/teams",
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
                "teams": [
                    {
                        "name": "devops",
                        "id": 123,
                        "node_id": "T_kwDOAegUqc4AUtL1",
                        "slug": "devops",
                        "description": "Team responsible for DevOps",
                        "privacy": "closed",
                        "url": "https://api.github.com/organizations/321/team/123",
                        "html_url": "https://github.com/orgs/foo/teams/devops",
                        "members_url": "https://api.github.com/organizations/321/team/123/members{/member}",
                        "repositories_url": "https://api.github.com/organizations/321/team/123/repos",
                        "permission": "pull",
                        "parent": None,
                    }
                ],
                "apps": [],
            },
        }

        reviews = RequiredPullRequestReviews.from_dict(data)

        self.assertEqual(
            reviews.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_pull_request_reviews",
        )
        self.assertTrue(reviews.dismiss_stale_reviews)
        self.assertTrue(reviews.require_code_owner_reviews)
        self.assertTrue(reviews.require_last_push_approval)
        self.assertEqual(
            reviews.required_approving_review_count,
            1,
        )
        dismissal_restrictions = reviews.dismissal_restrictions
        self.assertEqual(
            dismissal_restrictions.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions",
        )
        self.assertEqual(
            dismissal_restrictions.users_url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions/users",
        )
        self.assertEqual(
            dismissal_restrictions.teams_url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions/teams",
        )
        self.assertEqual(dismissal_restrictions.apps, [])
        user = dismissal_restrictions.users[0]
        self.assertEqual(len(dismissal_restrictions.users), 1)
        self.assertEqual(user.login, "greenbonebot")
        self.assertEqual(user.node_id, "MDQ6VXNlcjg1MjU0NjY2")
        self.assertEqual(
            user.avatar_url,
            "https://avatars.githubusercontent.com/u/85254666?v=4",
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/greenbonebot")
        self.assertEqual(user.html_url, "https://github.com/greenbonebot")
        self.assertEqual(
            user.followers_url,
            "https://api.github.com/users/greenbonebot/followers",
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/greenbonebot/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/greenbonebot/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/greenbonebot/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/greenbonebot/subscriptions",
        )
        self.assertEqual(
            user.organizations_url,
            "https://api.github.com/users/greenbonebot/orgs",
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/greenbonebot/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/greenbonebot/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/greenbonebot/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertEqual(user.site_admin, False)
        self.assertEqual(len(dismissal_restrictions.teams), 1)
        team = dismissal_restrictions.teams[0]
        self.assertEqual(team.name, "devops")
        self.assertEqual(team.id, 123)
        self.assertEqual(team.node_id, "T_kwDOAegUqc4AUtL1")
        self.assertEqual(team.slug, "devops")
        self.assertEqual(team.description, "Team responsible for DevOps")
        self.assertEqual(team.permission, Permission.PULL)
        self.assertEqual(team.privacy, TeamPrivacy.CLOSED)
        self.assertEqual(
            team.url, "https://api.github.com/organizations/321/team/123"
        )
        self.assertEqual(
            team.html_url, "https://github.com/orgs/foo/teams/devops"
        )
        self.assertEqual(
            team.members_url,
            "https://api.github.com/organizations/321/team/123/members{/member}",
        )
        self.assertEqual(
            team.repositories_url,
            "https://api.github.com/organizations/321/team/123/repos",
        )
        self.assertIsNone(team.parent)


class BranchProtectionTestCase(unittest.TestCase):
    def test_from_dict_minimal(self):
        data = {
            "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection",
            "required_signatures": {
                "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_signatures",
                "enabled": False,
            },
            "enforce_admins": {
                "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/enforce_admins",
                "enabled": False,
            },
            "required_linear_history": {"enabled": False},
            "allow_force_pushes": {"enabled": False},
            "allow_deletions": {"enabled": False},
            "block_creations": {"enabled": False},
            "required_conversation_resolution": {"enabled": False},
            "lock_branch": {"enabled": True},
            "allow_fork_syncing": {"enabled": False},
        }

        protection = BranchProtection.from_dict(data)

        self.assertEqual(
            protection.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection",
        )
        self.assertEqual(
            protection.required_signatures.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_signatures",
        )
        self.assertFalse(protection.required_signatures.enabled)
        self.assertEqual(
            protection.enforce_admins.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/enforce_admins",
        )
        self.assertFalse(protection.enforce_admins.enabled)
        self.assertFalse(protection.required_linear_history.enabled)
        self.assertFalse(protection.allow_force_pushes.enabled)
        self.assertFalse(protection.allow_deletions.enabled)
        self.assertFalse(protection.block_creations.enabled)
        self.assertFalse(protection.required_conversation_resolution.enabled)
        self.assertTrue(protection.lock_branch.enabled)
        self.assertFalse(protection.allow_fork_syncing.enabled)

        self.assertIsNone(protection.required_status_checks)
        self.assertIsNone(protection.required_pull_request_reviews)
        self.assertIsNone(protection.restrictions)

    def test_from_dict(self):
        data = {
            "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection",
            "required_status_checks": {
                "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_status_checks",
                "strict": True,
                "checks": [],
            },
            "restrictions": {
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
            },
            "required_pull_request_reviews": {
                "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_pull_request_reviews",
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": True,
                "require_last_push_approval": True,
                "required_approving_review_count": 1,
                "dismissal_restrictions": {
                    "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions",
                    "users_url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions/users",
                    "teams_url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions/teams",
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
                    "teams": [
                        {
                            "name": "devops",
                            "id": 123,
                            "node_id": "T_kwDOAegUqc4AUtL1",
                            "slug": "devops",
                            "description": "Team responsible for DevOps",
                            "privacy": "closed",
                            "url": "https://api.github.com/organizations/321/team/123",
                            "html_url": "https://github.com/orgs/foo/teams/devops",
                            "members_url": "https://api.github.com/organizations/321/team/123/members{/member}",
                            "repositories_url": "https://api.github.com/organizations/321/team/123/repos",
                            "permission": "pull",
                            "parent": None,
                        }
                    ],
                    "apps": [],
                },
            },
            "required_signatures": {
                "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_signatures",
                "enabled": True,
            },
            "enforce_admins": {
                "url": "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/enforce_admins",
                "enabled": True,
            },
            "required_linear_history": {"enabled": True},
            "allow_force_pushes": {"enabled": False},
            "allow_deletions": {"enabled": False},
            "block_creations": {"enabled": True},
            "required_conversation_resolution": {"enabled": True},
            "lock_branch": {"enabled": True},
            "allow_fork_syncing": {"enabled": False},
        }

        protection = BranchProtection.from_dict(data)

        self.assertEqual(
            protection.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection",
        )
        self.assertEqual(
            protection.required_signatures.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_signatures",
        )
        self.assertTrue(protection.required_signatures.enabled)
        self.assertEqual(
            protection.enforce_admins.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/enforce_admins",
        )
        self.assertTrue(protection.enforce_admins.enabled)
        self.assertTrue(protection.required_linear_history.enabled)
        self.assertFalse(protection.allow_force_pushes.enabled)
        self.assertFalse(protection.allow_deletions.enabled)
        self.assertTrue(protection.block_creations.enabled)
        self.assertTrue(protection.required_conversation_resolution.enabled)
        self.assertTrue(protection.lock_branch.enabled)
        self.assertFalse(protection.allow_fork_syncing.enabled)

        self.assertEqual(
            protection.required_status_checks.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_status_checks",
        )
        self.assertTrue(protection.required_status_checks.strict)
        self.assertEqual(protection.required_status_checks.checks, [])

        self.assertEqual(
            protection.required_pull_request_reviews.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/required_pull_request_reviews",
        )
        self.assertTrue(
            protection.required_pull_request_reviews.dismiss_stale_reviews
        )
        self.assertTrue(
            protection.required_pull_request_reviews.require_code_owner_reviews
        )
        self.assertTrue(
            protection.required_pull_request_reviews.require_last_push_approval
        )
        self.assertEqual(
            protection.required_pull_request_reviews.required_approving_review_count,
            1,
        )
        dismissal_restrictions = (
            protection.required_pull_request_reviews.dismissal_restrictions
        )
        self.assertEqual(
            dismissal_restrictions.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions",
        )
        self.assertEqual(
            dismissal_restrictions.users_url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions/users",
        )
        self.assertEqual(
            dismissal_restrictions.teams_url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/dismissal_restrictions/teams",
        )
        self.assertEqual(dismissal_restrictions.apps, [])
        user = dismissal_restrictions.users[0]
        self.assertEqual(len(dismissal_restrictions.users), 1)
        self.assertEqual(user.login, "greenbonebot")
        self.assertEqual(user.node_id, "MDQ6VXNlcjg1MjU0NjY2")
        self.assertEqual(
            user.avatar_url,
            "https://avatars.githubusercontent.com/u/85254666?v=4",
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/greenbonebot")
        self.assertEqual(user.html_url, "https://github.com/greenbonebot")
        self.assertEqual(
            user.followers_url,
            "https://api.github.com/users/greenbonebot/followers",
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/greenbonebot/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/greenbonebot/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/greenbonebot/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/greenbonebot/subscriptions",
        )
        self.assertEqual(
            user.organizations_url,
            "https://api.github.com/users/greenbonebot/orgs",
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/greenbonebot/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/greenbonebot/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/greenbonebot/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertEqual(user.site_admin, False)
        self.assertEqual(len(dismissal_restrictions.teams), 1)
        team = dismissal_restrictions.teams[0]
        self.assertEqual(team.name, "devops")
        self.assertEqual(team.id, 123)
        self.assertEqual(team.node_id, "T_kwDOAegUqc4AUtL1")
        self.assertEqual(team.slug, "devops")
        self.assertEqual(team.description, "Team responsible for DevOps")
        self.assertEqual(team.permission, Permission.PULL)
        self.assertEqual(team.privacy, TeamPrivacy.CLOSED)
        self.assertEqual(
            team.url, "https://api.github.com/organizations/321/team/123"
        )
        self.assertEqual(
            team.html_url, "https://github.com/orgs/foo/teams/devops"
        )
        self.assertEqual(
            team.members_url,
            "https://api.github.com/organizations/321/team/123/members{/member}",
        )
        self.assertEqual(
            team.repositories_url,
            "https://api.github.com/organizations/321/team/123/repos",
        )
        self.assertIsNone(team.parent)

        self.assertEqual(
            protection.restrictions.url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions",
        )
        self.assertEqual(
            protection.restrictions.users_url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions/users",
        )
        self.assertEqual(
            protection.restrictions.teams_url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions/teams",
        )
        self.assertEqual(
            protection.restrictions.apps_url,
            "https://api.github.com/repos/foo/bar/branches/branch_protection/protection/restrictions/apps",
        )
        user = protection.restrictions.users[0]
        self.assertEqual(len(protection.restrictions.users), 1)
        self.assertEqual(user.login, "greenbonebot")
        self.assertEqual(user.node_id, "MDQ6VXNlcjg1MjU0NjY2")
        self.assertEqual(
            user.avatar_url,
            "https://avatars.githubusercontent.com/u/85254666?v=4",
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/greenbonebot")
        self.assertEqual(user.html_url, "https://github.com/greenbonebot")
        self.assertEqual(
            user.followers_url,
            "https://api.github.com/users/greenbonebot/followers",
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/greenbonebot/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/greenbonebot/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/greenbonebot/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/greenbonebot/subscriptions",
        )
        self.assertEqual(
            user.organizations_url,
            "https://api.github.com/users/greenbonebot/orgs",
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/greenbonebot/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/greenbonebot/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/greenbonebot/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertEqual(user.site_admin, False)
        self.assertEqual(protection.restrictions.teams, [])
        self.assertEqual(protection.restrictions.apps, [])
