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

# pylint: disable=arguments-differ,redefined-builtin

from unittest.mock import MagicMock, call, patch

from pontos.github.api.client import (
    DEFAULT_ACCEPT_HEADER,
    GITHUB_API_VERSION,
    GitHubAsyncRESTClient,
)
from pontos.github.api.helper import DEFAULT_GITHUB_API_URL
from tests import AsyncMock, IsolatedAsyncioTestCase, aiter, anext


class GitHubAsyncRESTClientTestCase(IsolatedAsyncioTestCase):
    @patch("pontos.github.api.client.httpx.AsyncClient")
    def setUp(self, async_client: MagicMock) -> None:
        self.http_client = AsyncMock()
        async_client.return_value = self.http_client
        self.client = GitHubAsyncRESTClient("token")

    async def test_get(self):
        await self.client.get("/foo/bar")

        self.http_client.get.assert_awaited_once_with(
            f"{DEFAULT_GITHUB_API_URL}/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            params=None,
            follow_redirects=True,
        )

    async def test_get_url(self):
        await self.client.get("https://github.com/foo/bar")

        self.http_client.get.assert_awaited_once_with(
            "https://github.com/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            params=None,
            follow_redirects=True,
        )

    async def test_get_all(self):
        url = "https://foo.bar"
        response1 = MagicMock(links={"next": {"url": url}})
        response2 = MagicMock(links=None)

        self.http_client.get.side_effect = [
            response1,
            response2,
        ]
        it = aiter(self.client.get_all("/foo/bar"))

        await anext(it)
        await anext(it)

        with self.assertRaises(StopAsyncIteration):
            await anext(it)

        self.http_client.get.assert_has_awaits(
            [
                call(
                    f"{DEFAULT_GITHUB_API_URL}/foo/bar",
                    headers={
                        "Accept": DEFAULT_ACCEPT_HEADER,
                        "Authorization": "token token",
                        "X-GitHub-Api-Version": GITHUB_API_VERSION,
                    },
                    params=None,
                    follow_redirects=True,
                ),
                call(
                    f"{url}",
                    headers={
                        "Accept": DEFAULT_ACCEPT_HEADER,
                        "Authorization": "token token",
                        "X-GitHub-Api-Version": GITHUB_API_VERSION,
                    },
                    params=None,
                    follow_redirects=True,
                ),
            ]
        )

    async def test_delete(self):
        await self.client.delete("/foo/bar")

        self.http_client.delete.assert_awaited_once_with(
            f"{DEFAULT_GITHUB_API_URL}/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            params=None,
        )

    async def test_delete_url(self):
        await self.client.delete("https://github.com/foo/bar")

        self.http_client.delete.assert_awaited_once_with(
            "https://github.com/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            params=None,
        )

    async def test_post(self):
        await self.client.post("/foo/bar", data={"foo": "bar"})

        self.http_client.post.assert_awaited_once_with(
            f"{DEFAULT_GITHUB_API_URL}/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            json={"foo": "bar"},
            params=None,
            content=None,
        )

    async def test_post_url(self):
        await self.client.post(
            "https://github.com/foo/bar", data={"foo": "bar"}
        )

        self.http_client.post.assert_awaited_once_with(
            "https://github.com/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            json={"foo": "bar"},
            params=None,
            content=None,
        )

    async def test_post_with_content_length(self):
        await self.client.post(
            "/foo/bar", data={"foo": "bar"}, content_length=123
        )

        self.http_client.post.assert_awaited_once_with(
            f"{DEFAULT_GITHUB_API_URL}/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
                "Content-Length": "123",
            },
            json={"foo": "bar"},
            params=None,
            content=None,
        )

    async def test_put(self):
        await self.client.put("/foo/bar", data={"foo": "bar"})

        self.http_client.put.assert_awaited_once_with(
            f"{DEFAULT_GITHUB_API_URL}/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            json={"foo": "bar"},
            params=None,
            content=None,
        )

    async def test_put_url(self):
        await self.client.put("https://github.com/foo/bar", data={"foo": "bar"})

        self.http_client.put.assert_awaited_once_with(
            "https://github.com/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            json={"foo": "bar"},
            params=None,
            content=None,
        )

    async def test_patch(self):
        await self.client.patch("/foo/bar", data={"foo": "bar"})

        self.http_client.patch.assert_awaited_once_with(
            f"{DEFAULT_GITHUB_API_URL}/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            json={"foo": "bar"},
            params=None,
            content=None,
        )

    async def test_patch_url(self):
        await self.client.patch(
            "https://github.com/foo/bar", data={"foo": "bar"}
        )

        self.http_client.patch.assert_awaited_once_with(
            "https://github.com/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            json={"foo": "bar"},
            params=None,
            content=None,
        )

    async def test_stream(self):
        response = MagicMock()
        response.__aenter__.return_value = MagicMock()
        self.http_client.stream = MagicMock()
        self.http_client.stream.return_value = response

        async with self.client.stream("/foo/bar"):
            pass

        self.http_client.stream.assert_called_once_with(
            "GET",
            f"{DEFAULT_GITHUB_API_URL}/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            follow_redirects=True,
        )

    async def test_stream_url(self):
        response = MagicMock()
        response.__aenter__.return_value = MagicMock()
        self.http_client.stream = MagicMock()
        self.http_client.stream.return_value = response

        async with self.client.stream("https://github.com/foo/bar"):
            pass

        self.http_client.stream.assert_called_once_with(
            "GET",
            "https://github.com/foo/bar",
            headers={
                "Accept": DEFAULT_ACCEPT_HEADER,
                "Authorization": "token token",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            follow_redirects=True,
        )

    async def test_context_manager(self):
        async with self.client:
            pass

        self.http_client.__aenter__.assert_awaited_once()
        self.http_client.__aexit__.assert_awaited_once()
