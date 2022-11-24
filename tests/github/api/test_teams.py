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

# pylint: disable=redefined-builtin, line-too-long

from unittest.mock import MagicMock

import httpx

from pontos.github.api.teams import GitHubAsyncRESTTeams, TeamPrivacy, TeamRole
from pontos.github.models.base import Permission
from tests import AsyncIteratorMock, aiter, anext
from tests.github.api import GitHubAsyncRESTTestCase, create_response


class GitHubAsyncRESTTeamsTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTTeams

    async def test_get_all(self):
        response1 = create_response()
        response1.json.return_value = [
            {
                "id": 1,
                "node_id": "MDQ6VGVhbTE=",
                "url": "https://api.github.com/teams/1",
                "html_url": "https://github.com/orgs/github/teams/justice-league",
                "name": "Justice League",
                "slug": "justice-league",
                "description": "A great team.",
                "privacy": "closed",
                "permission": "admin",
                "members_url": "https://api.github.com/teams/1/members{/member}",
                "repositories_url": "https://api.github.com/teams/1/repos",
                "parent": None,
            }
        ]
        response2 = create_response()
        response2.json.return_value = [
            {
                "id": 2,
                "node_id": "MDQ6VGVhbTE=",
                "url": "https://api.github.com/teams/1",
                "html_url": "https://github.com/orgs/github/teams/justice-league",
                "name": "Justice League",
                "slug": "justice-league",
                "description": "A great team.",
                "privacy": "closed",
                "permission": "admin",
                "members_url": "https://api.github.com/teams/1/members{/member}",
                "repositories_url": "https://api.github.com/teams/1/repos",
                "parent": None,
            },
            {
                "id": 3,
                "node_id": "MDQ6VGVhbTE=",
                "url": "https://api.github.com/teams/1",
                "html_url": "https://github.com/orgs/github/teams/justice-league",
                "name": "Justice League",
                "slug": "justice-league",
                "description": "A great team.",
                "privacy": "closed",
                "permission": "admin",
                "members_url": "https://api.github.com/teams/1/members{/member}",
                "repositories_url": "https://api.github.com/teams/1/repos",
                "parent": None,
            },
        ]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.get_all("foo"))
        team = await anext(async_it)
        self.assertEqual(team.id, 1)
        team = await anext(async_it)
        self.assertEqual(team.id, 2)
        team = await anext(async_it)
        self.assertEqual(team.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/teams",
            params={"per_page": "100"},
        )

    async def test_create(self):
        response = create_response()
        response.json.return_value = {
            "id": 1,
            "node_id": "MDQ6VGVhbTE=",
            "url": "https://api.github.com/teams/1",
            "html_url": "https://github.com/orgs/github/teams/justice-league",
            "name": "Justice League",
            "slug": "justice-league",
            "description": "A great team.",
            "privacy": "closed",
            "permission": "admin",
            "members_url": "https://api.github.com/teams/1/members{/member}",
            "repositories_url": "https://api.github.com/teams/1/repos",
            "parent": None,
        }
        self.client.post.return_value = response

        team = await self.api.create(
            "foo",
            "bar",
            description="A description",
            maintainers=["foo", "bar"],
            repo_names=["foo/bar", "foo/baz"],
            privacy=TeamPrivacy.CLOSED,
            parent_team_id="123",
        )

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/teams",
            data={
                "name": "bar",
                "description": "A description",
                "maintainers": ["foo", "bar"],
                "repo_names": ["foo/bar", "foo/baz"],
                "privacy": "closed",
                "parent_team_id": "123",
            },
        )

        self.assertEqual(team.id, 1)

    async def test_create_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.create(
                "foo",
                "bar",
                description="A description",
                maintainers=["foo", "bar"],
                repo_names=["foo/bar", "foo/baz"],
                privacy=TeamPrivacy.CLOSED,
                parent_team_id="123",
            )

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/teams",
            data={
                "name": "bar",
                "description": "A description",
                "maintainers": ["foo", "bar"],
                "repo_names": ["foo/bar", "foo/baz"],
                "privacy": "closed",
                "parent_team_id": "123",
            },
        )

    async def test_get(self):
        response = create_response()
        response.json.return_value = {
            "id": 1,
            "node_id": "MDQ6VGVhbTE=",
            "url": "https://api.github.com/teams/1",
            "html_url": "https://github.com/orgs/github/teams/justice-league",
            "name": "Justice League",
            "slug": "justice-league",
            "description": "A great team.",
            "privacy": "closed",
            "permission": "admin",
            "members_url": "https://api.github.com/teams/1/members{/member}",
            "repositories_url": "https://api.github.com/teams/1/repos",
            "parent": None,
        }
        self.client.get.return_value = response

        team = await self.api.get("foo", "bar")

        self.client.get.assert_awaited_once_with(
            "/orgs/foo/teams/bar",
        )

        self.assertEqual(team.id, 1)

    async def test_get_failure(self):
        response = create_response()
        self.client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.get("foo", "bar")

        self.client.get.assert_awaited_once_with(
            "/orgs/foo/teams/bar",
        )

    async def test_update(self):
        response = create_response()
        response.json.return_value = {
            "id": 1,
            "node_id": "MDQ6VGVhbTE=",
            "url": "https://api.github.com/teams/1",
            "html_url": "https://github.com/orgs/github/teams/justice-league",
            "name": "baz",
            "slug": "justice-league",
            "description": "A description",
            "privacy": "closed",
            "permission": "admin",
            "members_url": "https://api.github.com/teams/1/members{/member}",
            "repositories_url": "https://api.github.com/teams/1/repos",
            "parent": None,
        }
        self.client.post.return_value = response

        team = await self.api.update(
            "foo",
            "bar",
            name="baz",
            description="A description",
            privacy=TeamPrivacy.CLOSED,
            parent_team_id="123",
        )

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/teams/bar",
            data={
                "name": "baz",
                "description": "A description",
                "privacy": "closed",
                "parent_team_id": "123",
            },
        )

        self.assertEqual(team.id, 1)

    async def test_update_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.update(
                "foo",
                "bar",
                name="baz",
                description="A description",
                privacy=TeamPrivacy.CLOSED,
                parent_team_id="123",
            )

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/teams/bar",
            data={
                "name": "baz",
                "description": "A description",
                "privacy": "closed",
                "parent_team_id": "123",
            },
        )

    async def test_delete(self):
        response = create_response()
        self.client.delete.return_value = response

        await self.api.delete("foo", "bar")

        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/teams/bar",
        )

    async def test_delete_failure(self):
        response = create_response()
        self.client.delete.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.delete("foo", "bar")

        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/teams/bar",
        )

    async def test_members(self):
        response1 = create_response()
        response1.json.return_value = [
            {
                "id": 1,
                "login": "octocat",
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
            }
        ]
        response2 = create_response()
        response2.json.return_value = [
            {
                "id": 2,
                "login": "octocat2",
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
            {
                "id": 3,
                "login": "octocat3",
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
        ]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.members("foo", "bar"))
        member = await anext(async_it)
        self.assertEqual(member.id, 1)
        member = await anext(async_it)
        self.assertEqual(member.id, 2)
        member = await anext(async_it)
        self.assertEqual(member.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/teams/bar/members",
            params={"per_page": "100"},
        )

    async def test_update_member(self):
        response = create_response()
        self.client.put.return_value = response

        await self.api.update_member(
            "foo", "bar", "baz", role=TeamRole.MAINTAINER
        )

        self.client.put.assert_awaited_once_with(
            "/orgs/foo/teams/bar/memberships/baz", data={"role": "maintainer"}
        )

    async def test_add_member(self):
        response = create_response()
        self.client.put.return_value = response

        await self.api.add_member("foo", "bar", "baz", role=TeamRole.MAINTAINER)

        self.client.put.assert_awaited_once_with(
            "/orgs/foo/teams/bar/memberships/baz", data={"role": "maintainer"}
        )

    async def test_update_member_failure(self):
        response = create_response()
        self.client.put.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.update_member("foo", "bar", "baz")

        self.client.put.assert_awaited_once_with(
            "/orgs/foo/teams/bar/memberships/baz", data={"role": "member"}
        )

    async def test_remove_member(self):
        response = create_response()
        self.client.delete.return_value = response

        await self.api.remove_member("foo", "bar", "baz")

        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/teams/bar/memberships/baz"
        )

    async def test_remove_member_failure(self):
        response = create_response()
        self.client.delete.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.remove_member("foo", "bar", "baz")

        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/teams/bar/memberships/baz"
        )

    async def test_repositories(self):
        response1 = create_response()
        response1.json.return_value = [
            {
                "id": 1,
                "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
                "name": "Hello-World",
                "full_name": "octocat/Hello-World",
                "owner": {
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
                "private": False,
                "html_url": "https://github.com/octocat/Hello-World",
                "description": "This your first repo!",
                "fork": False,
                "url": "https://api.github.com/repos/octocat/Hello-World",
                "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
                "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
                "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
                "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
                "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
                "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
                "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
                "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
                "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
                "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
                "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
                "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
                "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
                "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
                "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
                "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
                "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
                "git_url": "git:github.com/octocat/Hello-World.git",
                "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
                "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
                "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
                "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
                "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
                "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
                "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
                "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
                "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
                "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
                "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
                "ssh_url": "git@github.com:octocat/Hello-World.git",
                "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
                "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
                "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
                "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
                "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
                "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
                "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
                "clone_url": "https://github.com/octocat/Hello-World.git",
                "mirror_url": "git:git.example.com/octocat/Hello-World",
                "hooks_url": "https://api.github.com/repos/octocat/Hello-World/hooks",
                "svn_url": "https://svn.github.com/octocat/Hello-World",
                "homepage": "https://github.com",
                "language": None,
                "forks_count": 9,
                "stargazers_count": 80,
                "watchers_count": 80,
                "size": 108,
                "default_branch": "master",
                "open_issues_count": 0,
                "is_template": False,
                "topics": ["octocat", "atom", "electron", "api"],
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True,
                "has_pages": False,
                "has_downloads": True,
                "has_discussions": False,
                "archived": False,
                "disabled": False,
                "visibility": "public",
                "pushed_at": "2011-01-26T19:06:43Z",
                "created_at": "2011-01-26T19:01:12Z",
                "updated_at": "2011-01-26T19:14:43Z",
                "permissions": {"admin": False, "push": False, "pull": True},
            }
        ]
        response2 = create_response()
        response2.json.return_value = [
            {
                "id": 2,
                "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
                "name": "Hello-World",
                "full_name": "octocat/Hello-World",
                "owner": {
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
                "private": False,
                "html_url": "https://github.com/octocat/Hello-World",
                "description": "This your first repo!",
                "fork": False,
                "url": "https://api.github.com/repos/octocat/Hello-World",
                "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
                "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
                "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
                "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
                "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
                "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
                "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
                "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
                "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
                "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
                "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
                "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
                "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
                "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
                "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
                "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
                "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
                "git_url": "git:github.com/octocat/Hello-World.git",
                "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
                "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
                "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
                "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
                "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
                "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
                "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
                "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
                "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
                "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
                "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
                "ssh_url": "git@github.com:octocat/Hello-World.git",
                "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
                "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
                "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
                "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
                "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
                "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
                "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
                "clone_url": "https://github.com/octocat/Hello-World.git",
                "mirror_url": "git:git.example.com/octocat/Hello-World",
                "hooks_url": "https://api.github.com/repos/octocat/Hello-World/hooks",
                "svn_url": "https://svn.github.com/octocat/Hello-World",
                "homepage": "https://github.com",
                "language": None,
                "forks_count": 9,
                "stargazers_count": 80,
                "watchers_count": 80,
                "size": 108,
                "default_branch": "master",
                "open_issues_count": 0,
                "is_template": False,
                "topics": ["octocat", "atom", "electron", "api"],
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True,
                "has_pages": False,
                "has_downloads": True,
                "has_discussions": False,
                "archived": False,
                "disabled": False,
                "visibility": "public",
                "pushed_at": "2011-01-26T19:06:43Z",
                "created_at": "2011-01-26T19:01:12Z",
                "updated_at": "2011-01-26T19:14:43Z",
                "permissions": {"admin": False, "push": False, "pull": True},
            },
            {
                "id": 3,
                "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
                "name": "Hello-World",
                "full_name": "octocat/Hello-World",
                "owner": {
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
                "private": False,
                "html_url": "https://github.com/octocat/Hello-World",
                "description": "This your first repo!",
                "fork": False,
                "url": "https://api.github.com/repos/octocat/Hello-World",
                "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
                "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
                "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
                "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
                "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
                "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
                "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
                "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
                "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
                "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
                "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
                "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
                "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
                "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
                "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
                "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
                "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
                "git_url": "git:github.com/octocat/Hello-World.git",
                "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
                "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
                "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
                "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
                "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
                "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
                "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
                "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
                "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
                "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
                "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
                "ssh_url": "git@github.com:octocat/Hello-World.git",
                "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
                "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
                "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
                "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
                "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
                "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
                "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
                "clone_url": "https://github.com/octocat/Hello-World.git",
                "mirror_url": "git:git.example.com/octocat/Hello-World",
                "hooks_url": "https://api.github.com/repos/octocat/Hello-World/hooks",
                "svn_url": "https://svn.github.com/octocat/Hello-World",
                "homepage": "https://github.com",
                "language": None,
                "forks_count": 9,
                "stargazers_count": 80,
                "watchers_count": 80,
                "size": 108,
                "default_branch": "master",
                "open_issues_count": 0,
                "is_template": False,
                "topics": ["octocat", "atom", "electron", "api"],
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True,
                "has_pages": False,
                "has_downloads": True,
                "has_discussions": False,
                "archived": False,
                "disabled": False,
                "visibility": "public",
                "pushed_at": "2011-01-26T19:06:43Z",
                "created_at": "2011-01-26T19:01:12Z",
                "updated_at": "2011-01-26T19:14:43Z",
                "permissions": {"admin": False, "push": False, "pull": True},
            },
        ]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.repositories("foo", "bar"))
        repo = await anext(async_it)
        self.assertEqual(repo.id, 1)
        repo = await anext(async_it)
        self.assertEqual(repo.id, 2)
        repo = await anext(async_it)
        self.assertEqual(repo.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/teams/bar/repos",
            params={"per_page": "100"},
        )

    async def test_update_permissions(self):
        response = create_response()
        self.client.put.return_value = response

        await self.api.update_permission("foo", "bar", "baz", Permission.TRIAGE)

        self.client.put.assert_awaited_once_with(
            "/orgs/foo/teams/bar/repos/foo/baz", data={"permission": "triage"}
        )

    async def test_add_permissions(self):
        response = create_response()
        self.client.put.return_value = response

        await self.api.add_permission("foo", "bar", "baz", Permission.ADMIN)

        self.client.put.assert_awaited_once_with(
            "/orgs/foo/teams/bar/repos/foo/baz", data={"permission": "admin"}
        )

    async def test_update_permissions_failure(self):
        response = create_response()
        self.client.put.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.update_permission(
                "foo", "bar", "baz", Permission.TRIAGE
            )

        self.client.put.assert_awaited_once_with(
            "/orgs/foo/teams/bar/repos/foo/baz", data={"permission": "triage"}
        )
