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

# pylint: disable=arguments-differ

import sys
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, call, patch

from pontos.github.api.client import GitHubAsyncRESTClient
from pontos.github.api.helper import DEFAULT_GITHUB_API_URL

if sys.version_info.minor < 10:
    # aiter and anext have been added in Python 3.10

    def aiter(obj):  # pylint: disable=redefined-builtin
        return obj.__aiter__()

    def anext(obj):  # pylint: disable=redefined-builtin
        return obj.__anext__()


class GitHubAsyncRESTClientTestCase(IsolatedAsyncioTestCase):
    @patch("pontos.github.api.client.httpx.AsyncClient")
    def setUp(self, async_client: MagicMock) -> None:
        self.async_client_instance = AsyncMock()
        async_client.return_value = self.async_client_instance
        self.client = GitHubAsyncRESTClient("token")

    async def test_get(self):
        await self.client.get("/foo/bar")

        self.async_client_instance.get.assert_awaited_once_with(
            f"{DEFAULT_GITHUB_API_URL}/foo/bar",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token token",
            },
            params=None,
            follow_redirects=True,
        )

    async def test_get_all(self):
        url = "https://foo.bar"
        response1 = MagicMock(links={"next": {"url": url}})
        response2 = MagicMock(links=None)

        self.async_client_instance.get.side_effect = [
            response1,
            response2,
        ]
        it = aiter(self.client.get_all("/foo/bar"))

        await anext(it)
        await anext(it)

        with self.assertRaises(StopAsyncIteration):
            await anext(it)

        self.async_client_instance.get.assert_has_awaits(
            [
                call(
                    f"{DEFAULT_GITHUB_API_URL}/foo/bar",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token token",
                    },
                    params=None,
                    follow_redirects=True,
                ),
                call(
                    f"{url}",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": "token token",
                    },
                    params=None,
                    follow_redirects=True,
                ),
            ]
        )

    async def test_delete(self):
        await self.client.delete("/foo/bar")

        self.async_client_instance.delete.assert_awaited_once_with(
            f"{DEFAULT_GITHUB_API_URL}/foo/bar",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token token",
            },
            params=None,
        )

    async def test_post(self):
        await self.client.delete("/foo/bar")

        self.async_client_instance.delete.assert_awaited_once_with(
            f"{DEFAULT_GITHUB_API_URL}/foo/bar",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token token",
            },
            params=None,
        )

    async def test_context_manager(self):
        async with self.client:
            pass

        self.async_client_instance.__aenter__.assert_awaited_once()
        self.async_client_instance.__aexit__.assert_awaited_once()
