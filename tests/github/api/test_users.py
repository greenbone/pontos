# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

from pontos.github.api.users import GitHubAsyncRESTUsers
from tests import AsyncIteratorMock, aiter, anext
from tests.github.api import GitHubAsyncRESTTestCase, create_response


class GitHubAsyncRESTUsersTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTUsers

    async def test_users(self):
        response = create_response()
        response.json.return_value = [
            {
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
            }
        ]

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.users())
        user = await anext(async_it)
        self.assertEqual(user.id, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/users",
            params={"per_page": "100"},
        )

    async def test_user(self):
        response = create_response()
        response.json.return_value = {
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
            "name": "monalisa octocat",
            "company": "GitHub",
            "blog": "https://github.com/blog",
            "location": "San Francisco",
            "email": "octocat@github.com",
            "hireable": False,
            "bio": "There once was...",
            "twitter_username": "monatheoctocat",
            "public_repos": 2,
            "public_gists": 1,
            "followers": 20,
            "following": 0,
            "created_at": "2008-01-14T04:33:35Z",
            "updated_at": "2008-01-14T04:33:35Z",
        }
        self.client.get.return_value = response

        user = await self.api.user(
            "octocat",
        )

        self.client.get.assert_awaited_once_with(
            "/users/octocat",
        )

        self.assertEqual(user.id, 1)

    async def test_current_user(self):
        response = create_response()
        response.json.return_value = {
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
            "name": "monalisa octocat",
            "company": "GitHub",
            "blog": "https://github.com/blog",
            "location": "San Francisco",
            "email": "octocat@github.com",
            "hireable": False,
            "bio": "There once was...",
            "twitter_username": "monatheoctocat",
            "public_repos": 2,
            "public_gists": 1,
            "followers": 20,
            "following": 0,
            "created_at": "2008-01-14T04:33:35Z",
            "updated_at": "2008-01-14T04:33:35Z",
        }
        self.client.get.return_value = response

        user = await self.api.current_user()

        self.client.get.assert_awaited_once_with("/user")

        self.assertEqual(user.id, 1)

    async def test_user_keys(self):
        response = create_response()
        response.json.return_value = [{"id": 1, "key": "ssh-rsa AAA..."}]

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.user_keys("foo"))
        key = await anext(async_it)
        self.assertEqual(key.id, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/users/foo/keys",
            params={"per_page": "100"},
        )

    async def test_keys(self):
        response = create_response()
        response.json.return_value = [{"id": 1, "key": "ssh-rsa AAA..."}]

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.keys())
        key = await anext(async_it)
        self.assertEqual(key.id, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/user/keys",
            params={"per_page": "100"},
        )

    async def test_emails(self):
        response = create_response()
        response.json.return_value = [
            {
                "email": "octocat@github.com",
                "verified": True,
                "primary": True,
                "visibility": "public",
            }
        ]

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.emails())
        email = await anext(async_it)
        self.assertEqual(email.email, "octocat@github.com")

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/user/emails",
            params={"per_page": "100"},
        )

    async def test_key(self):
        response = create_response()
        response.json.return_value = {
            "key": "2Sg8iYjAxxmI2LvUXpJjkYrMxURPc8r+dB7TJyvv1234",
            "id": 2,
            "url": "https://api.github.com/user/keys/2",
            "title": "ssh-rsa AAAAB3NzaC1yc2EAAA",
            "created_at": "2020-06-11T21:31:57Z",
            "verified": False,
            "read_only": False,
        }
        self.client.get.return_value = response

        key = await self.api.key(2)

        self.client.get.assert_awaited_once_with(
            "/user/keys/2",
        )

        self.assertEqual(key.id, 2)

    async def test_delete_key(self):
        response = create_response()
        self.client.get.return_value = response

        await self.api.delete_key(2)

        self.client.delete.assert_awaited_once_with(
            "/user/keys/2",
        )

    async def test_create_key(self):
        response = create_response()
        response.json.return_value = {
            "key": "2Sg8iYjAxxmI2LvUXpJjkYrMxURPc8r+dB7TJyvv1234",
            "id": 2,
            "url": "https://api.github.com/user/keys/2",
            "title": "ssh-rsa AAAAB3NzaC1yc2EAAA",
            "created_at": "2020-06-11T21:31:57Z",
            "verified": False,
            "read_only": False,
        }
        self.client.post.return_value = response

        key = await self.api.create_key(
            "ssh-rsa AAAAB3NzaC1yc2EAAA",
            "2Sg8iYjAxxmI2LvUXpJjkYrMxURPc8r+dB7TJyvv1234",
        )

        self.client.post.assert_awaited_once_with(
            "/user/keys",
            data={
                "title": "ssh-rsa AAAAB3NzaC1yc2EAAA",
                "key": "2Sg8iYjAxxmI2LvUXpJjkYrMxURPc8r+dB7TJyvv1234",
            },
        )

        self.assertEqual(key.id, 2)
