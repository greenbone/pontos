# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=too-many-lines, redefined-builtin, line-too-long

from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock

import httpx

from pontos.github.api.errors import GitHubApiError
from pontos.github.api.organizations import (
    GitHubAsyncRESTOrganizations,
    InvitationRole,
    MemberFilter,
    MemberRole,
)
from pontos.github.models.organization import RepositoryType
from tests import AsyncIteratorMock, aiter, anext
from tests.github.api import GitHubAsyncRESTTestCase, create_response

here = Path(__file__).parent

REPOSITORY_DICT = {
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
    "forks": 1,
    "open_issues": 0,
    "watchers": 1,
}

MEMBER_DICT = {
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


class GitHubAsyncRESTOrganizationsTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTOrganizations

    async def test_exists(self):
        response = create_response(is_success=True)
        self.client.get.return_value = response

        self.assertTrue(await self.api.exists("foo"))

        self.client.get.assert_awaited_once_with("/orgs/foo")

    async def test_not_exists(self):
        response = create_response(is_success=False, status_code=404)
        self.client.get.return_value = response

        self.assertFalse(await self.api.exists("foo"))

        self.client.get.assert_awaited_once_with("/orgs/foo")

    async def test_exists_error(self):
        response = create_response(is_success=False, status_code=403)
        error = httpx.HTTPStatusError(
            "403", request=MagicMock(), response=response
        )
        response.raise_for_status.side_effect = error

        self.client.get.return_value = response

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.exists("foo")
        self.client.get.assert_awaited_once_with("/orgs/foo")

    async def test_get_repositories(self):
        response1 = create_response()
        response1.json.return_value = [REPOSITORY_DICT]
        response2 = create_response()
        repository_dict2 = deepcopy(REPOSITORY_DICT)
        repository_dict2["id"] = 2
        repository_dict3 = deepcopy(REPOSITORY_DICT)
        repository_dict3["id"] = 3
        response2.json.return_value = [repository_dict2, repository_dict3]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.get_repositories("foo"))
        repo = await anext(async_it)
        self.assertEqual(repo.id, 1)
        repo = await anext(async_it)
        self.assertEqual(repo.id, 2)
        repo = await anext(async_it)
        self.assertEqual(repo.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/repos",
            params={"per_page": "100", "type": "all"},
        )

    async def test_get_private_repositories(self):
        response1 = create_response()
        response1.json.return_value = [REPOSITORY_DICT]
        response2 = create_response()
        repository_dict2 = deepcopy(REPOSITORY_DICT)
        repository_dict2["id"] = 2
        repository_dict3 = deepcopy(REPOSITORY_DICT)
        repository_dict3["id"] = 3
        response2.json.return_value = [repository_dict2, repository_dict3]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(
            self.api.get_repositories(
                "foo", repository_type=RepositoryType.PRIVATE
            )
        )
        repo = await anext(async_it)
        self.assertEqual(repo.id, 1)
        repo = await anext(async_it)
        self.assertEqual(repo.id, 2)
        repo = await anext(async_it)
        self.assertEqual(repo.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/repos",
            params={"per_page": "100", "type": "private"},
        )

    async def test_members(self):
        response1 = create_response()
        response1.json.return_value = [MEMBER_DICT]
        response2 = create_response()
        member_dict2 = deepcopy(MEMBER_DICT)
        member_dict2["id"] = 2
        member_dict3 = deepcopy(MEMBER_DICT)
        member_dict3["id"] = 3
        response2.json.return_value = [member_dict2, member_dict3]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.members("foo"))
        member = await anext(async_it)
        self.assertEqual(member.id, 1)
        member = await anext(async_it)
        self.assertEqual(member.id, 2)
        member = await anext(async_it)
        self.assertEqual(member.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/members",
            params={"per_page": "100", "filter": "all", "role": "all"},
        )

    async def test_members_admins(self):
        response1 = create_response()
        response1.json.return_value = [MEMBER_DICT]
        response2 = create_response()
        member_dict2 = deepcopy(MEMBER_DICT)
        member_dict2["id"] = 2
        member_dict3 = deepcopy(MEMBER_DICT)
        member_dict3["id"] = 3
        response2.json.return_value = [member_dict2, member_dict3]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.members("foo", role=MemberRole.ADMIN))
        member = await anext(async_it)
        self.assertEqual(member.id, 1)
        member = await anext(async_it)
        self.assertEqual(member.id, 2)
        member = await anext(async_it)
        self.assertEqual(member.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/members",
            params={"per_page": "100", "filter": "all", "role": "admin"},
        )

    async def test_members_filter(self):
        response1 = create_response()
        response1.json.return_value = [MEMBER_DICT]
        response2 = create_response()
        member_dict2 = deepcopy(MEMBER_DICT)
        member_dict2["id"] = 2
        member_dict3 = deepcopy(MEMBER_DICT)
        member_dict3["id"] = 3
        response2.json.return_value = [member_dict2, member_dict3]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(
            self.api.members("foo", member_filter=MemberFilter.TWO_FA_DISABLED)
        )
        member = await anext(async_it)
        self.assertEqual(member.id, 1)
        member = await anext(async_it)
        self.assertEqual(member.id, 2)
        member = await anext(async_it)
        self.assertEqual(member.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/members",
            params={"per_page": "100", "filter": "2fa_disabled", "role": "all"},
        )

    async def test_invite_email(self):
        response = create_response(is_success=False)
        self.client.post.return_value = response

        await self.api.invite(
            "foo",
            email="foo@bar.com",
        )

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/invitations",
            data={"role": "direct_member", "email": "foo@bar.com"},
        )

    async def test_invite_invitee(self):
        response = create_response(is_success=False)
        self.client.post.return_value = response

        await self.api.invite(
            "foo",
            invitee_id="foo",
        )

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/invitations",
            data={"role": "direct_member", "invitee_id": "foo"},
        )

    async def test_invite_missing_user(self):
        response = create_response(is_success=False)
        self.client.post.return_value = response

        with self.assertRaises(GitHubApiError):
            await self.api.invite("foo")

    async def test_invite_with_teams(self):
        response = create_response(is_success=False)
        self.client.post.return_value = response

        await self.api.invite("foo", email="foo@bar.com", team_ids=("1", "2"))

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/invitations",
            data={
                "role": "direct_member",
                "email": "foo@bar.com",
                "team_ids": ["1", "2"],
            },
        )

    async def test_invite_with_role(self):
        response = create_response(is_success=False)
        self.client.post.return_value = response

        await self.api.invite(
            "foo", email="foo@bar.com", role=InvitationRole.ADMIN
        )

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/invitations",
            data={
                "role": "admin",
                "email": "foo@bar.com",
            },
        )

    async def test_remove_member(self):
        response = create_response(is_success=False)
        self.client.delete.return_value = response

        await self.api.remove_member("foo", "bar")

        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/memberships/bar",
        )

    async def test_remove_member_failure(self):
        response = create_response()
        self.client.delete.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.remove_member("foo", "bar")

        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/memberships/bar",
        )

    async def test_outside_collaborators(self):
        response1 = create_response()
        response1.json.return_value = [MEMBER_DICT]
        response2 = create_response()
        member_dict2 = deepcopy(MEMBER_DICT)
        member_dict2["id"] = 2
        member_dict3 = deepcopy(MEMBER_DICT)
        member_dict3["id"] = 3
        response2.json.return_value = [member_dict2, member_dict3]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.outside_collaborators("foo"))
        member = await anext(async_it)
        self.assertEqual(member.id, 1)
        member = await anext(async_it)
        self.assertEqual(member.id, 2)
        member = await anext(async_it)
        self.assertEqual(member.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/outside_collaborators",
            params={"per_page": "100", "filter": "all"},
        )

    async def test_outside_collaborators_filter(self):
        response1 = create_response()
        response1.json.return_value = [MEMBER_DICT]
        response2 = create_response()
        member_dict2 = deepcopy(MEMBER_DICT)
        member_dict2["id"] = 2
        member_dict3 = deepcopy(MEMBER_DICT)
        member_dict3["id"] = 3
        response2.json.return_value = [member_dict2, member_dict3]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(
            self.api.outside_collaborators(
                "foo", member_filter=MemberFilter.TWO_FA_DISABLED
            )
        )
        member = await anext(async_it)
        self.assertEqual(member.id, 1)
        member = await anext(async_it)
        self.assertEqual(member.id, 2)
        member = await anext(async_it)
        self.assertEqual(member.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/outside_collaborators",
            params={"per_page": "100", "filter": "2fa_disabled"},
        )

    async def test_remove_outside_collaborator(self):
        response = create_response(is_success=False)
        self.client.delete.return_value = response

        await self.api.remove_outside_collaborator("foo", "bar")

        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/outside_collaborators/bar",
        )

    async def test_remove_outside_collaborator_failure(self):
        response = create_response()
        self.client.delete.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.remove_outside_collaborator("foo", "bar")

        self.client.delete.assert_awaited_once_with(
            "/orgs/foo/outside_collaborators/bar",
        )
