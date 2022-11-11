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

# pylint: disable=redefined-builtin

from unittest.mock import MagicMock

import httpx

from pontos.github.api.teams import GitHubAsyncRESTTeams, TeamPrivacy, TeamRole
from tests import AsyncIteratorMock, aiter, anext
from tests.github.api import GitHubAsyncRESTTestCase, create_response


class GitHubAsyncRESTTeamsTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTTeams

    async def test_get_all(self):
        response1 = create_response()
        response1.json.return_value = [{"id": 1}]
        response2 = create_response()
        response2.json.return_value = [{"id": 2}, {"id": 3}]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.get_all("foo"))
        team = await anext(async_it)
        self.assertEqual(team["id"], 1)
        team = await anext(async_it)
        self.assertEqual(team["id"], 2)
        team = await anext(async_it)
        self.assertEqual(team["id"], 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/teams",
            params={"per_page": "100"},
        )

    async def test_create(self):
        response = create_response()
        self.client.post.return_value = response

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
        self.client.get.return_value = response

        await self.api.get("foo", "bar")

        self.client.get.assert_awaited_once_with(
            "/orgs/foo/teams/bar",
        )

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
        self.client.post.return_value = response

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
        response1.json.return_value = [{"id": 1}]
        response2 = create_response()
        response2.json.return_value = [{"id": 2}, {"id": 3}]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.members("foo", "bar"))
        member = await anext(async_it)
        self.assertEqual(member["id"], 1)
        member = await anext(async_it)
        self.assertEqual(member["id"], 2)
        member = await anext(async_it)
        self.assertEqual(member["id"], 3)

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
        response1.json.return_value = [{"id": 1}]
        response2 = create_response()
        response2.json.return_value = [{"id": 2}, {"id": 3}]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.repositories("foo", "bar"))
        repo = await anext(async_it)
        self.assertEqual(repo["id"], 1)
        repo = await anext(async_it)
        self.assertEqual(repo["id"], 2)
        repo = await anext(async_it)
        self.assertEqual(repo["id"], 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/teams/bar/repos",
            params={"per_page": "100"},
        )
