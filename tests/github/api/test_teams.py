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
from unittest.mock import MagicMock

import httpx

from pontos.github.api.teams import GitHubAsyncRESTTeams, TeamPrivacy
from tests import AsyncIteratorMock
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

        repos = await self.api.get_all("foo")

        self.assertEqual(len(repos), 3)
        self.assertEqual(repos, [{"id": 1}, {"id": 2}, {"id": 3}])

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
