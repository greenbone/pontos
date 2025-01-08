# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=line-too-long, arguments-differ, redefined-builtin
# ruff: noqa: E501

from datetime import datetime
from typing import Any, Optional
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

from httpx import AsyncClient, Response

from pontos.errors import PontosError
from pontos.nvd.api import now
from pontos.nvd.cpe_match.api import MAX_CPE_MATCHES_PER_PAGE, CPEMatchApi
from tests import AsyncMock, IsolatedAsyncioTestCase, aiter, anext
from tests.nvd import get_cpe_match_data


def uuid_replace_str(uuid: UUID, iteration: int, number: int) -> str:
    id_str = str(uuid).rsplit("-", 2)
    return f"{id_str[0]}-{iteration:04}-{number:012}"


def uuid_replace(uuid: UUID, iteration: int, number: int) -> UUID:
    return UUID(uuid_replace_str(uuid, iteration, number))


def generate_cpe_name(iteration: int, number: int) -> str:
    return f"cpe:2.3:a:acme:test-app:1.{iteration-1}.{number-1}:*:*:*:*:*:*:*"


def create_cpe_match_response(
    match_criteria_id: UUID,
    cpe_name_id: UUID,
    *,
    update: Optional[dict[str, Any]] = None,
    results: int = 1,
    iteration: int = 1,
) -> MagicMock:
    match_strings = [
        {
            "match_string": get_cpe_match_data(
                {
                    "match_criteria_id": f"{uuid_replace_str(match_criteria_id, iteration, i)}",
                    "criteria": generate_cpe_name(iteration, i),
                    "matches": [
                        {
                            "cpe_name": generate_cpe_name(iteration, i),
                            "cpe_name_id": f"{uuid_replace_str(cpe_name_id, iteration, i)}",
                        }
                    ],
                }
            )
        }
        for i in range(1, results + 1)
    ]

    data = {
        "match_strings": match_strings,
        "results_per_page": results,
    }
    if update:
        data.update(update)

    response = MagicMock(spec=Response)
    response.json.return_value = data
    return response


def create_cpe_match_responses(
    match_criteria_id: UUID,
    cpe_name_id: UUID,
    responses: int = 2,
    results_per_response: int = 1,
) -> list[MagicMock]:
    return [
        create_cpe_match_response(
            match_criteria_id=match_criteria_id,
            cpe_name_id=cpe_name_id,
            update={"total_results": responses * results_per_response},
            results=results_per_response,
            iteration=i,
        )
        for i in range(1, responses + 1)
    ]


class CPEMatchApiTestCase(IsolatedAsyncioTestCase):
    @patch("pontos.nvd.api.time.monotonic", autospec=True)
    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    def setUp(self, async_client: MagicMock, monotonic_mock: MagicMock) -> None:
        self.http_client = AsyncMock()
        async_client.return_value = self.http_client
        monotonic_mock.return_value = 0
        self.api = CPEMatchApi()

    async def test_no_match_criteria_id(self):
        with self.assertRaises(PontosError):
            await self.api.cpe_match(None)

    async def test_no_match_strings(self):
        data = {
            "match_strings": [],
            "results_per_page": 1,
        }
        response = MagicMock(spec=Response)
        response.json.return_value = data
        self.http_client.get.return_value = response

        with self.assertRaises(PontosError):
            await self.api.cpe_match("DOES-NOT-EXIST")

    async def test_cpe_match(self):
        match_criteria_id = uuid_replace(uuid4(), 1, 1)
        cpe_name_id = uuid_replace(uuid4(), 1, 1)

        self.http_client.get.return_value = create_cpe_match_response(
            match_criteria_id, cpe_name_id
        )

        cpe_match_string = await self.api.cpe_match(match_criteria_id)

        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={"matchCriteriaId": str(match_criteria_id)},
        )

        self.assertEqual(
            match_criteria_id,
            cpe_match_string.match_criteria_id,
        )
        self.assertEqual(
            generate_cpe_name(1, 1),
            cpe_match_string.criteria,
        )
        self.assertEqual(
            cpe_name_id,
            cpe_match_string.matches[0].cpe_name_id,
        )
        self.assertEqual(
            generate_cpe_name(1, 1),
            cpe_match_string.matches[0].cpe_name,
        )

    @patch("pontos.nvd.cpe_match.api.now", spec=now)
    async def test_cpe_matches_last_modified_start_date(
        self, now_mock: MagicMock
    ):
        match_criteria_id = uuid4()
        cpe_name_id = uuid4()

        now_mock.return_value = datetime(2019, 8, 30)
        self.http_client.get.side_effect = create_cpe_match_responses(
            match_criteria_id, cpe_name_id
        )

        it = aiter(
            self.api.cpe_matches(last_modified_start_date=datetime(2019, 6, 1))
        )
        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 1, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={
                "startIndex": 0,
                "lastModStartDate": "2019-06-01T00:00:00",
                "lastModEndDate": "2019-08-30T00:00:00",
                "resultsPerPage": MAX_CPE_MATCHES_PER_PAGE,
            },
        )

        self.http_client.get.reset_mock()

        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 2, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={
                "startIndex": 1,
                "lastModStartDate": "2019-06-01T00:00:00",
                "lastModEndDate": "2019-08-30T00:00:00",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cpe_match = await anext(it)

    @patch("pontos.nvd.cpe_match.api.now", spec=now)
    async def test_cpe_matches_last_modified_end_date(
        self, now_mock: MagicMock
    ):
        match_criteria_id = uuid4()
        cpe_name_id = uuid4()

        now_mock.return_value = datetime(2019, 8, 30)
        self.http_client.get.side_effect = create_cpe_match_responses(
            match_criteria_id, cpe_name_id
        )

        it = aiter(
            self.api.cpe_matches(last_modified_end_date=datetime(2019, 8, 1))
        )
        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 1, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={
                "startIndex": 0,
                "lastModEndDate": "2019-08-01T00:00:00",
                "resultsPerPage": MAX_CPE_MATCHES_PER_PAGE,
            },
        )

        self.http_client.get.reset_mock()

        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 2, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={
                "startIndex": 1,
                "lastModEndDate": "2019-08-01T00:00:00",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cpe_match = await anext(it)

    async def test_cpe_matches_cve_id(self):
        match_criteria_id = uuid4()
        cpe_name_id = uuid4()

        self.http_client.get.side_effect = create_cpe_match_responses(
            match_criteria_id, cpe_name_id
        )

        it = aiter(self.api.cpe_matches(cve_id="CVE-2010-3574"))
        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 1, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={
                "startIndex": 0,
                "cveId": "CVE-2010-3574",
                "resultsPerPage": MAX_CPE_MATCHES_PER_PAGE,
            },
        )

        self.http_client.get.reset_mock()

        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 2, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={
                "startIndex": 1,
                "cveId": "CVE-2010-3574",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cpe_match = await anext(it)

    async def test_cpe_matches_match_string_search(self):
        match_criteria_id = uuid4()
        cpe_name_id = uuid4()

        self.http_client.get.side_effect = create_cpe_match_responses(
            match_criteria_id, cpe_name_id
        )

        it = aiter(
            self.api.cpe_matches(
                match_string_search="cpe:2.3:a:sun:jre:*:*:*:*:*:*:*:*"
            )
        )
        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 1, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={
                "startIndex": 0,
                "matchStringSearch": "cpe:2.3:a:sun:jre:*:*:*:*:*:*:*:*",
                "resultsPerPage": MAX_CPE_MATCHES_PER_PAGE,
            },
        )

        self.http_client.get.reset_mock()

        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 2, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={
                "startIndex": 1,
                "matchStringSearch": "cpe:2.3:a:sun:jre:*:*:*:*:*:*:*:*",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cpe_match = await anext(it)

    async def test_cpe_matches_request_results(self):
        match_criteria_id = uuid4()
        cpe_name_id = uuid4()

        self.http_client.get.side_effect = create_cpe_match_responses(
            match_criteria_id=match_criteria_id,
            cpe_name_id=cpe_name_id,
            results_per_response=2,
        )

        it = aiter(self.api.cpe_matches(request_results=10))
        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 1, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={
                "startIndex": 0,
                "resultsPerPage": 10,
            },
        )

        self.http_client.get.reset_mock()
        cpe_match = await anext(it)
        self.assertEqual(
            uuid_replace(match_criteria_id, 1, 2), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_not_called()

        self.http_client.get.reset_mock()

        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 2, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={},
            params={
                "startIndex": 2,
                "resultsPerPage": 2,
            },
        )

        self.http_client.get.reset_mock()
        cpe_match = await anext(it)
        self.assertEqual(
            uuid_replace(match_criteria_id, 2, 2), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_not_called()

        with self.assertRaises(Exception):
            cpe_match = await anext(it)

    async def test_cpe_match_caching(self):
        match_criteria_id = uuid4()
        cpe_name_id = uuid4()

        responses = create_cpe_match_responses(
            match_criteria_id=match_criteria_id,
            cpe_name_id=cpe_name_id,
            results_per_response=3,
        )
        self.http_client.get.side_effect = responses
        response_matches = [
            [
                match_string["match_string"]["matches"]
                for match_string in response.json.return_value["match_strings"]
            ]
            for response in responses
        ]

        # Make matches of first match_string identical in each response
        response_matches[1][0][0]["cpe_name"] = response_matches[0][0][0][
            "cpe_name"
        ]
        response_matches[1][0][0]["cpe_name_id"] = response_matches[0][0][0][
            "cpe_name_id"
        ]
        # Make matches of second match_string only have the same cpe_name_id
        response_matches[1][1][0]["cpe_name_id"] = response_matches[0][1][0][
            "cpe_name_id"
        ]
        # Leave matches of third match_string different from each other

        it = aiter(self.api.cpe_matches(request_results=10))
        received = [item async for item in it]

        # First matches in each response of three items must be identical objects
        self.assertIs(received[0].matches[0], received[3].matches[0])

        # Second matches in each response of three items must only have same cpe_name_id
        self.assertIsNot(received[1].matches[0], received[4].matches[0])
        self.assertEqual(
            received[1].matches[0].cpe_name_id,
            received[4].matches[0].cpe_name_id,
        )
        self.assertNotEqual(
            received[1].matches[0].cpe_name, received[4].matches[0].cpe_name
        )

        # Third matches in each response of three items must be different
        self.assertIsNot(received[2].matches[0], received[5].matches[0])
        self.assertNotEqual(
            received[2].matches[0].cpe_name_id,
            received[5].matches[0].cpe_name_id,
        )
        self.assertNotEqual(
            received[2].matches[0].cpe_name, received[5].matches[0].cpe_name
        )

    async def test_context_manager(self):
        async with self.api:
            pass

        self.http_client.__aenter__.assert_awaited_once()
        self.http_client.__aexit__.assert_awaited_once()


class CPEMatchApiWithTokenTestCase(IsolatedAsyncioTestCase):
    @patch("pontos.nvd.api.time.monotonic", autospec=True)
    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    def setUp(self, async_client: MagicMock, monotonic_mock: MagicMock) -> None:
        self.http_client = AsyncMock()
        async_client.return_value = self.http_client
        monotonic_mock.return_value = 0
        self.api = CPEMatchApi(token="token123")

    async def test_cpe_matches_request_results_with_token(self):
        match_criteria_id = uuid4()
        cpe_name_id = uuid4()

        self.http_client.get.side_effect = create_cpe_match_responses(
            match_criteria_id=match_criteria_id,
            cpe_name_id=cpe_name_id,
            results_per_response=2,
        )

        it = aiter(self.api.cpe_matches(request_results=10))
        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 1, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={"apiKey": "token123"},
            params={
                "startIndex": 0,
                "resultsPerPage": 10,
            },
        )

        self.http_client.get.reset_mock()
        cpe_match = await anext(it)
        self.assertEqual(
            uuid_replace(match_criteria_id, 1, 2), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_not_called()

        self.http_client.get.reset_mock()

        cpe_match = await anext(it)

        self.assertEqual(
            uuid_replace(match_criteria_id, 2, 1), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cpematch/2.0",
            headers={"apiKey": "token123"},
            params={
                "startIndex": 2,
                "resultsPerPage": 2,
            },
        )

        self.http_client.get.reset_mock()
        cpe_match = await anext(it)
        self.assertEqual(
            uuid_replace(match_criteria_id, 2, 2), cpe_match.match_criteria_id
        )
        self.http_client.get.assert_not_called()

        with self.assertRaises(Exception):
            cpe_match = await anext(it)

    @patch("pontos.nvd.api.time.monotonic", autospec=True)
    @patch("pontos.nvd.api.asyncio.sleep", autospec=True)
    async def test_rate_limit_with_token(
        self,
        sleep_mock: MagicMock,
        monotonic_mock: MagicMock,
    ):
        match_criteria_id = uuid4()
        cpe_name_id = uuid4()
        self.http_client.get.side_effect = create_cpe_match_responses(
            match_criteria_id, cpe_name_id, 8
        )
        monotonic_mock.side_effect = [10, 11]

        it = aiter(self.api.cpe_matches())
        await anext(it)
        await anext(it)
        await anext(it)
        await anext(it)
        await anext(it)

        sleep_mock.assert_not_called()

        await anext(it)

        sleep_mock.assert_not_called()
