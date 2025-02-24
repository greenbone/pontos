# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later


from datetime import datetime, timezone
from typing import Any, Optional
from unittest.mock import MagicMock, patch

from httpx import AsyncClient, Response

from pontos.nvd.models.source import AcceptanceLevel
from pontos.nvd.source.api import MAX_SOURCES_PER_PAGE, SourceApi
from tests import AsyncMock, IsolatedAsyncioTestCase, aiter, anext
from tests.nvd import get_source_data


def create_source_response(
    name: str, update: Optional[dict[str, Any]] = None
) -> MagicMock:
    data = {
        "sources": [get_source_data({"name": name})],
        "results_per_page": 1,
    }
    if update:
        data.update(update)

    response = MagicMock(spec=Response)
    response.json.return_value = data
    return response


def create_source_responses(count: int = 2) -> list[MagicMock]:
    return [
        create_source_response(f"MITRE-{i}", {"total_results": count})
        for i in range(1, count + 1)
    ]


class SourceAPITestCase(IsolatedAsyncioTestCase):
    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    def setUp(self, async_client: MagicMock) -> None:
        self.http_client = AsyncMock()
        async_client.return_value = self.http_client
        self.api = SourceApi(token="token")

    async def test_sources(self):
        self.http_client.get.side_effect = create_source_responses()

        it = aiter(self.api.sources())
        source = await anext(it)

        self.assertEqual(source.name, "MITRE-1")
        self.assertEqual(
            source.contact_email,
            "cve@mitre.org",
        )
        self.assertEqual(
            source.source_identifiers,
            [
                "cve@mitre.org",
                "8254265b-2729-46b6-b9e3-3dfca2d5bfca",
            ],
        )
        self.assertEqual(
            source.last_modified,
            datetime(2019, 9, 9, 16, 18, 45, 930000, tzinfo=timezone.utc),
        )
        self.assertEqual(
            source.created,
            datetime(2019, 9, 9, 16, 18, 45, 930000, tzinfo=timezone.utc),
        )
        self.assertIsNone(source.v2_acceptance_level)
        self.assertEqual(
            source.v3_acceptance_level,
            AcceptanceLevel(
                "Contributor",
                datetime(2025, 1, 30, 0, 0, 20, 107000, tzinfo=timezone.utc),
            ),
        )
        self.assertEqual(
            source.cwe_acceptance_level,
            AcceptanceLevel(
                "Reference",
                datetime(2025, 1, 24, 0, 0, 0, 43000, tzinfo=timezone.utc),
            ),
        )

        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/source/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "resultsPerPage": MAX_SOURCES_PER_PAGE,
            },
        )

        self.http_client.get.reset_mock()

        source = await anext(it)
        self.assertEqual(source.name, "MITRE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/source/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 1, "resultsPerPage": 1},
        )

        with self.assertRaises(StopAsyncIteration):
            await anext(it)

    async def test_sources_change_dates(self):
        self.http_client.get.side_effect = create_source_responses()

        it = aiter(
            self.api.sources(
                last_modified_start_date=datetime(2025, 1, 1),
                last_modified_end_date=datetime(2025, 1, 31),
            )
        )
        source = await anext(it)

        self.assertEqual(source.name, "MITRE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/source/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "lastModStartDate": "2025-01-01T00:00:00",
                "lastModEndDate": "2025-01-31T00:00:00",
                "resultsPerPage": MAX_SOURCES_PER_PAGE,
            },
        )

        self.http_client.get.reset_mock()

        source = await anext(it)

        self.assertEqual(source.name, "MITRE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/source/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "lastModStartDate": "2025-01-01T00:00:00",
                "lastModEndDate": "2025-01-31T00:00:00",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            source = await anext(it)

    async def test_sources_source_identifier(self):
        self.http_client.get.side_effect = create_source_responses()

        it = aiter(self.api.sources(source_identifier="cve@mitre.org"))
        source = await anext(it)
        self.assertEqual(source.name, "MITRE-1")

        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/source/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "resultsPerPage": MAX_SOURCES_PER_PAGE,
                "sourceIdentifier": "cve@mitre.org",
            },
        )

        self.http_client.get.reset_mock()

        source = await anext(it)
        self.assertEqual(source.name, "MITRE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/source/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "resultsPerPage": 1,
                "sourceIdentifier": "cve@mitre.org",
            },
        )

        with self.assertRaises(StopAsyncIteration):
            await anext(it)

    async def test_context_manager(self):
        async with self.api:
            pass

        self.http_client.__aenter__.assert_awaited_once()
        self.http_client.__aexit__.assert_awaited_once()
