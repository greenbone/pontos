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

from pontos.github.api.labels import GitHubAsyncRESTLabels
from tests import AsyncIteratorMock, aiter, anext
from tests.github.api import GitHubAsyncRESTTestCase, create_response


class GitHubAsyncRESTLabelsTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTLabels

    async def test_get_all(self):
        response1 = create_response()
        response1.json.return_value = [{"id": 1, "name": "a"}]
        response2 = create_response()
        response2.json.return_value = [
            {"id": 2, "name": "b"},
            {"id": 3, "name": "c"},
        ]

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.get_all("foo/bar", 123))
        label = await anext(async_it)
        self.assertEqual(label, "a")
        label = await anext(async_it)
        self.assertEqual(label, "b")
        label = await anext(async_it)
        self.assertEqual(label, "c")

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/issues/123/labels",
            params={"per_page": "100"},
        )

    async def test_set_all(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.set_all("foo/bar", 123, ["a", "b"])

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/issues/123/labels", data={"labels": ["a", "b"]}
        )

    async def test_set_labels_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.set_all("foo/bar", 123, ["a", "b"])

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/issues/123/labels", data={"labels": ["a", "b"]}
        )
