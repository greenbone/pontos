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

# pylint: disable=protected-access

import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient

from pontos.nvd.api import NVDApi, convert_camel_case, format_date, sleep
from tests import IsolatedAsyncioTestCase


class ConvertCamelCaseTestCase(unittest.TestCase):
    def test_convert(self):
        data = {
            "someValue": 123,
            "otherValue": "bar",
        }

        converted = convert_camel_case(data)
        self.assertEqual(converted["some_value"], 123)
        self.assertEqual(converted["other_value"], "bar")


class FormatDateTestCase(unittest.TestCase):
    def test_format_date(self):
        dt = datetime(2022, 12, 10, 10, 0, 12, 123)
        fd = format_date(dt)

        self.assertEqual(fd, "2022-12-10T10:00:12")


class NVDApiTestCase(IsolatedAsyncioTestCase):
    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    async def test_context_manager(self, async_client: MagicMock):
        http_client = AsyncMock()
        async_client.return_value = http_client
        api = NVDApi("https://foo.bar/baz", token="token")

        async with api:
            pass

        http_client.__aenter__.assert_awaited_once()
        http_client.__aexit__.assert_awaited_once()

    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    async def test_get_without_token(self, async_client: MagicMock):
        http_client = AsyncMock()
        async_client.return_value = http_client
        api = NVDApi("https://foo.bar/baz")

        await api._get()

        http_client.get.assert_awaited_once_with(
            "https://foo.bar/baz", headers={}, params=None
        )

    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    async def test_get_with_token(self, async_client: MagicMock):
        http_client = AsyncMock()
        async_client.return_value = http_client
        api = NVDApi("https://foo.bar/baz", token="token")

        await api._get()

        http_client.get.assert_awaited_once_with(
            "https://foo.bar/baz", headers={"apiKey": "token"}, params=None
        )

    @patch("pontos.nvd.api.sleep", spec=sleep)
    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    async def test_rate_limit(
        self, async_client: MagicMock, sleep_mock: MagicMock
    ):
        http_client = AsyncMock()
        async_client.return_value = http_client
        api = NVDApi("https://foo.bar/baz")

        await api._get()
        await api._get()
        await api._get()
        await api._get()
        await api._get()

        sleep_mock.assert_not_called()

        await api._get()

        sleep_mock.assert_called_once_with()

    @patch("pontos.nvd.api.sleep", spec=sleep)
    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    async def test_no_rate_limit(
        self, async_client: MagicMock, sleep_mock: MagicMock
    ):
        http_client = AsyncMock()
        async_client.return_value = http_client
        api = NVDApi("https://foo.bar/baz", rate_limit=False)

        await api._get()
        await api._get()
        await api._get()
        await api._get()
        await api._get()

        sleep_mock.assert_not_called()

        await api._get()

        sleep_mock.assert_not_called()
