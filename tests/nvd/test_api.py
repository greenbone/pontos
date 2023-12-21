# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=protected-access

import unittest
from datetime import datetime
from typing import Any, Iterator
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient, Response

from pontos.nvd.api import (
    JSON,
    InvalidState,
    NoMoreResults,
    NVDApi,
    NVDResults,
    convert_camel_case,
    format_date,
)
from tests import IsolatedAsyncioTestCase, aiter, anext


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

    @patch("pontos.nvd.api.time.monotonic", autospec=True)
    @patch("pontos.nvd.api.asyncio.sleep", autospec=True)
    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    async def test_rate_limit(
        self,
        async_client: MagicMock,
        sleep_mock: MagicMock,
        monotonic_mock: MagicMock,
    ):
        http_client = AsyncMock()
        async_client.return_value = http_client
        monotonic_mock.side_effect = [0.0, 10.0, 11.0]

        api = NVDApi("https://foo.bar/baz")

        await api._get()
        await api._get()
        await api._get()
        await api._get()
        await api._get()

        sleep_mock.assert_not_called()

        await api._get()

        sleep_mock.assert_called_once_with(20.0)

    @patch("pontos.nvd.api.asyncio.sleep", autospec=True)
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


class Result:
    def __init__(self, value: int) -> None:
        self.value = value


def result_func(data: JSON) -> Iterator[Result]:
    return (Result(d) for d in data["values"])  # type: ignore


class NVDResultsTestCase(IsolatedAsyncioTestCase):
    async def test_items(self):
        response_mock = MagicMock(spec=Response)
        response_mock.json.side_effect = [
            {
                "values": [1, 2, 3],
                "total_results": 6,
                "results_per_page": 3,
            },
            {
                "values": [4, 5, 6],
                "total_results": 6,
                "results_per_page": 3,
            },
        ]
        api_mock = AsyncMock(spec=NVDApi)
        api_mock._get.return_value = response_mock

        results: NVDResults[Result] = NVDResults(
            api_mock,
            {},
            result_func,
        )

        it = aiter(results.items())

        result = await anext(it)
        self.assertEqual(result.value, 1)

        result = await anext(it)
        self.assertEqual(result.value, 2)

        result = await anext(it)
        self.assertEqual(result.value, 3)

        result = await anext(it)
        self.assertEqual(result.value, 4)

        result = await anext(it)
        self.assertEqual(result.value, 5)

        result = await anext(it)
        self.assertEqual(result.value, 6)

        with self.assertRaises(StopAsyncIteration):
            await anext(it)

    async def test_aiter(self):
        response_mock = MagicMock(spec=Response)
        response_mock.json.side_effect = [
            {
                "values": [1, 2, 3],
                "total_results": 6,
                "results_per_page": 3,
            },
            {
                "values": [4, 5, 6],
                "total_results": 6,
                "results_per_page": 3,
            },
        ]
        api_mock = AsyncMock(spec=NVDApi)
        api_mock._get.return_value = response_mock

        results: NVDResults[Result] = NVDResults(
            api_mock,
            {},
            result_func,
        )

        it = aiter(results)

        result = await anext(it)
        self.assertEqual(result.value, 1)

        result = await anext(it)
        self.assertEqual(result.value, 2)

        result = await anext(it)
        self.assertEqual(result.value, 3)

        result = await anext(it)
        self.assertEqual(result.value, 4)

        result = await anext(it)
        self.assertEqual(result.value, 5)

        result = await anext(it)
        self.assertEqual(result.value, 6)

        with self.assertRaises(StopAsyncIteration):
            await anext(it)

    async def test_len(self):
        response_mock = MagicMock(spec=Response)
        response_mock.json.return_value = {
            "values": [1, 2, 3],
            "total_results": 3,
            "results_per_page": 3,
        }
        api_mock = AsyncMock(spec=NVDApi)
        api_mock._get.return_value = response_mock

        results: NVDResults[Result] = NVDResults(
            api_mock,
            {},
            result_func,
        )

        with self.assertRaisesRegex(
            InvalidState, "NVDResults has not been awaited yet"
        ):
            len(results)

        await results

        self.assertEqual(len(results), 3)

    async def test_chunks(self):
        response_mock = MagicMock(spec=Response)
        response_mock.json.side_effect = [
            {
                "values": [1, 2, 3],
                "total_results": 6,
                "results_per_page": 3,
            },
            {
                "values": [4, 5, 6],
                "total_results": 6,
                "results_per_page": 3,
            },
        ]
        api_mock = AsyncMock(spec=NVDApi)
        api_mock._get.return_value = response_mock

        nvd_results: NVDResults[Result] = NVDResults(
            api_mock,
            {},
            result_func,
        )

        it = aiter(nvd_results.chunks())

        results = await anext(it)
        self.assertEqual([result.value for result in results], [1, 2, 3])

        results = await anext(it)
        self.assertEqual([result.value for result in results], [4, 5, 6])

        with self.assertRaises(StopAsyncIteration):
            await anext(it)

    async def test_json(self):
        response_mock = MagicMock(spec=Response)
        response_mock.json.side_effect = [
            {
                "values": [1, 2, 3],
                "total_results": 6,
                "results_per_page": 3,
            },
            {
                "values": [4, 5, 6],
                "total_results": 6,
                "results_per_page": 3,
            },
        ]
        api_mock = AsyncMock(spec=NVDApi)
        api_mock._get.return_value = response_mock

        nvd_results: NVDResults[Result] = NVDResults(
            api_mock,
            {},
            result_func,
        )

        json: dict[str, Any] = await nvd_results.json()  # type: ignore
        self.assertEqual(json["values"], [1, 2, 3])
        self.assertEqual(json["total_results"], 6)
        self.assertEqual(json["results_per_page"], 3)

        json: dict[str, Any] = await nvd_results.json()  # type: ignore
        self.assertEqual(json["values"], [4, 5, 6])
        self.assertEqual(json["total_results"], 6)
        self.assertEqual(json["results_per_page"], 3)

        self.assertIsNone(await nvd_results.json())

    async def test_await(self):
        response_mock = MagicMock(spec=Response)
        response_mock.json.side_effect = [
            {
                "values": [1, 2, 3],
                "total_results": 6,
                "results_per_page": 3,
            },
            {
                "values": [4, 5, 6],
                "total_results": 6,
                "results_per_page": 3,
            },
        ]
        api_mock = AsyncMock(spec=NVDApi)
        api_mock._get.return_value = response_mock

        nvd_results: NVDResults[Result] = NVDResults(
            api_mock,
            {},
            result_func,
        )

        await nvd_results
        self.assertEqual(len(nvd_results), 6)

        json: dict[str, Any] = await nvd_results.json()  # type: ignore
        self.assertEqual(json["values"], [1, 2, 3])
        self.assertEqual(json["total_results"], 6)
        self.assertEqual(json["results_per_page"], 3)

        await nvd_results
        json: dict[str, Any] = await nvd_results.json()  # type: ignore
        self.assertEqual(json["values"], [4, 5, 6])
        self.assertEqual(json["total_results"], 6)
        self.assertEqual(json["results_per_page"], 3)

        with self.assertRaises(NoMoreResults):
            await nvd_results

    async def test_mix_and_match(self):
        response_mock = MagicMock(spec=Response)
        response_mock.json.side_effect = [
            {
                "values": [1, 2, 3],
                "total_results": 6,
                "results_per_page": 3,
            },
            {
                "values": [4, 5, 6],
                "total_results": 6,
                "results_per_page": 3,
            },
        ]
        api_mock = AsyncMock(spec=NVDApi)
        api_mock._get.return_value = response_mock

        nvd_results: NVDResults[Result] = NVDResults(
            api_mock,
            {},
            result_func,
        )

        await nvd_results
        self.assertEqual(len(nvd_results), 6)

        json: dict[str, Any] = await nvd_results.json()  # type: ignore
        self.assertEqual(json["values"], [1, 2, 3])
        self.assertEqual(json["total_results"], 6)
        self.assertEqual(json["results_per_page"], 3)

        self.assertEqual(
            [result.value async for result in nvd_results], [1, 2, 3, 4, 5, 6]
        )

        json: dict[str, Any] = await nvd_results.json()  # type: ignore
        self.assertEqual(json["values"], [4, 5, 6])
        self.assertEqual(json["total_results"], 6)
        self.assertEqual(json["results_per_page"], 3)

    async def test_response_error(self):
        response_mock = MagicMock(spec=Response)
        response_mock.json.side_effect = [
            {
                "values": [1, 2, 3],
                "total_results": 6,
                "results_per_page": 3,
            },
        ]
        api_mock = AsyncMock(spec=NVDApi)
        api_mock._get.return_value = response_mock

        nvd_results: NVDResults[Result] = NVDResults(
            api_mock,
            {},
            result_func,
        )

        json = await nvd_results.json()
        self.assertEqual(json["values"], [1, 2, 3])  # type: ignore

        api_mock._get.assert_called_once_with(params={"startIndex": 0})

        response_mock.raise_for_status.side_effect = Exception("Server Error")

        api_mock.reset_mock()

        with self.assertRaises(Exception):
            json = await nvd_results.json()

        api_mock._get.assert_called_once_with(
            params={
                "startIndex": 3,
                "resultsPerPage": 3,
            }
        )

        response_mock.reset_mock(return_value=True, side_effect=True)
        api_mock.reset_mock()

        response_mock.json.side_effect = [
            {
                "values": [4, 5, 6],
                "total_results": 6,
                "results_per_page": 3,
            },
        ]

        json = await nvd_results.json()
        self.assertEqual(json["values"], [4, 5, 6])  # type: ignore

        api_mock._get.assert_called_once_with(
            params={
                "startIndex": 3,
                "resultsPerPage": 3,
            }
        )

    async def test_request_results_limit(self):
        response_mock = MagicMock(spec=Response)
        response_mock.json.side_effect = [
            {
                "values": [1, 2, 3, 4],
                "total_results": 5,
                "results_per_page": 4,
            },
            {
                "values": [5],
                "total_results": 5,
                "results_per_page": 1,
            },
        ]
        api_mock = AsyncMock(spec=NVDApi)
        api_mock._get.return_value = response_mock

        nvd_results: NVDResults[Result] = NVDResults(
            api_mock,
            {},
            result_func,
            request_results=5,
        )

        json: dict[str, Any] = await nvd_results.json()  # type: ignore
        self.assertEqual(json["values"], [1, 2, 3, 4])
        self.assertEqual(json["total_results"], 5)
        self.assertEqual(json["results_per_page"], 4)

        api_mock._get.assert_called_once_with(params={"startIndex": 0})
        api_mock.reset_mock()

        json: dict[str, Any] = await nvd_results.json()  # type: ignore
        self.assertEqual(json["values"], [5])
        self.assertEqual(json["total_results"], 5)
        self.assertEqual(json["results_per_page"], 1)

        api_mock._get.assert_called_once_with(
            params={"startIndex": 4, "resultsPerPage": 1}
        )

    async def test_repr(self):
        response_mock = MagicMock(spec=Response)
        response_mock.json.side_effect = [
            {
                "values": [1, 2, 3, 4],
                "total_results": 5,
                "results_per_page": 4,
            },
            {
                "values": [5],
                "total_results": 5,
                "results_per_page": 1,
            },
        ]
        response_mock.url = "https://some.url&startIndex=0"
        api_mock = AsyncMock(spec=NVDApi)
        api_mock._get.return_value = response_mock

        nvd_results: NVDResults[Result] = NVDResults(
            api_mock,
            {},
            result_func,
        )

        await nvd_results

        self.assertEqual(
            repr(nvd_results),
            '<NVDResults url="https://some.url&startIndex=0" '
            "total_results=5 start_index=0 current_index=4 "
            "results_per_page=None>",
        )
