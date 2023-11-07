# Copyright (C) 2023 Greenbone AG
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


from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from httpx import AsyncClient, Response

from pontos.nvd.cve_change_history.api import CVEChangeHistoryApi
from pontos.nvd.models.cve_change import Detail, EventName
from tests.nvd import get_cve_change_data


def create_cve_changes_response(
    cve_id: str, update: Optional[Dict[str, Any]] = None
) -> MagicMock:
    data = {
        "cve_changes": [{"change": get_cve_change_data({"cve_id": cve_id})}],
        "results_per_page": 1,
    }
    if update:
        data.update(update)

    response = MagicMock(spec=Response)
    response.json.return_value = data
    return response


def create_cve_changes_responses(count: int = 2) -> List[MagicMock]:
    return [
        create_cve_changes_response(f"CVE-{i}", {"total_results": count})
        for i in range(1, count + 1)
    ]


class CVEChangeHistoryApiTestCase(IsolatedAsyncioTestCase):
    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    def setUp(self, async_client: MagicMock) -> None:
        self.http_client = AsyncMock()
        async_client.return_value = self.http_client
        self.api = CVEChangeHistoryApi(token="token")

    async def test_cve_changes(self):
        self.http_client.get.side_effect = create_cve_changes_responses()

        it = aiter(self.api.cve_changes())
        cve_change = await anext(it)

        self.assertEqual(cve_change.cve_id, "CVE-1")
        self.assertEqual(cve_change.event_name, EventName.INITAL_ANALYSIS)
        self.assertEqual(
            cve_change.cve_change_id,
            UUID("5160FDEB-0FF0-457B-AA36-0AEDCAB2522E"),
        )
        self.assertEqual(cve_change.source_identifier, "nvd@nist.gov")
        self.assertEqual(
            cve_change.created, datetime(2022, 3, 18, 20, 13, 8, 123000)
        )
        self.assertEqual(
            cve_change.details,
            [
                Detail(
                    action="Added",
                    type="CVSS V2",
                    new_value="NIST (AV:L/AC:L/Au:N/C:P/I:N/A:N)",
                ),
                Detail(
                    action="Added",
                    type="CVSS V3.1",
                    new_value="NIST AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N",
                ),
                Detail(
                    action="Changed",
                    type="Reference Type",
                    old_value="http://www.openwall.com/lists/oss-security/2022/03/18/2 No Types Assigned",
                    new_value="http://www.openwall.com/lists/oss-security/2022/03/18/2 Mailing List, Third Party Advisory",
                ),
            ],
        )

        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cvehistory/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0},
        )

        self.http_client.get.reset_mock()

        cve_change = await anext(it)
        self.assertEqual(cve_change.cve_id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cvehistory/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 1, "resultsPerPage": 1},
        )

        with self.assertRaises(StopAsyncIteration):
            cve_change = await anext(it)

    async def test_cve_changes_change_dates(self):
        self.http_client.get.side_effect = create_cve_changes_responses()

        it = aiter(
            self.api.cve_changes(
                change_start_date=datetime(2022, 12, 1),
                change_end_date=datetime(2022, 12, 31),
            )
        )
        cve_changes = await anext(it)

        self.assertEqual(cve_changes.cve_id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cvehistory/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "changeStartDate": "2022-12-01T00:00:00",
                "changeEndDate": "2022-12-31T00:00:00",
            },
        )

        self.http_client.get.reset_mock()

        cve_changes = await anext(it)

        self.assertEqual(cve_changes.cve_id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cvehistory/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "changeStartDate": "2022-12-01T00:00:00",
                "changeEndDate": "2022-12-31T00:00:00",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve_changes = await anext(it)

    async def test_cve_changes_cve_id(self):
        self.http_client.get.side_effect = create_cve_changes_responses()

        it = aiter(self.api.cve_changes(cve_id="CVE-1"))
        cve_changes = await anext(it)

        self.assertEqual(cve_changes.cve_id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cvehistory/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0, "cveId": "CVE-1"},
        )

        self.http_client.get.reset_mock()

        cve_changes = await anext(it)

        self.assertEqual(cve_changes.cve_id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cvehistory/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "cveId": "CVE-1",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve_changes = await anext(it)

    async def test_cve_changes_event_name(self):
        self.http_client.get.side_effect = create_cve_changes_responses()

        it = aiter(self.api.cve_changes(event_name=EventName.INITAL_ANALYSIS))
        cve_changes = await anext(it)

        self.assertEqual(cve_changes.cve_id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cvehistory/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0, "eventName": "Initial Analysis"},
        )

        self.http_client.get.reset_mock()

        cve_changes = await anext(it)

        self.assertEqual(cve_changes.cve_id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cvehistory/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "eventName": "Initial Analysis",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve_changes = await anext(it)

    async def test_context_manager(self):
        async with self.api:
            pass

        self.http_client.__aenter__.assert_awaited_once()
        self.http_client.__aexit__.assert_awaited_once()
