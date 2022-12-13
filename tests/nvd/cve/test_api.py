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

# pylint: disable=line-too-long, arguments-differ, redefined-builtin

from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

from httpx import AsyncClient, Response

from pontos.errors import PontosError
from pontos.nvd.api import now, sleep
from pontos.nvd.cve.api import CVEApi
from pontos.nvd.models import cvss_v2, cvss_v3
from tests import AsyncMock, IsolatedAsyncioTestCase, aiter, anext
from tests.nvd import get_cve_data


def create_cve_response(
    cve_id: str, update: Optional[Dict[str, Any]] = None
) -> MagicMock:
    data = {
        "vulnerabilities": [{"cve": get_cve_data({"id": cve_id})}],
        "results_per_page": 1,
    }
    if update:
        data.update(update)

    response = MagicMock(spec=Response)
    response.json.return_value = data
    return response


def create_cves_responses(count: int = 2) -> List[MagicMock]:
    return [
        create_cve_response(f"CVE-{i}", {"total_results": count})
        for i in range(1, count + 1)
    ]


class CVEApiTestCase(IsolatedAsyncioTestCase):
    @patch("pontos.nvd.api.AsyncClient", spec=AsyncClient)
    def setUp(self, async_client: MagicMock) -> None:
        self.http_client = AsyncMock()
        async_client.return_value = self.http_client
        self.api = CVEApi(token="token")

    async def test_no_cve_id(self):
        with self.assertRaises(PontosError):
            await self.api.cve(None)

    async def test_no_cve(self):
        data = {
            "vulnerabilities": [],
            "results_per_page": 1,
        }
        response = MagicMock(spec=Response)
        response.json.return_value = data
        self.http_client.get.return_value = response

        with self.assertRaises(PontosError):
            await self.api.cve("CVE-1")

    async def test_cve(self):
        data = {"vulnerabilities": [{"cve": get_cve_data()}]}
        response = MagicMock(spec=Response)
        response.json.return_value = data
        self.http_client.get.return_value = response

        cve = await self.api.cve("FOO-BAR")

        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"cveId": "FOO-BAR"},
        )

        self.assertEqual(cve.id, "CVE-2022-45536")
        self.assertEqual(cve.source_identifier, "cve@mitre.org")
        self.assertEqual(
            cve.published, datetime(2022, 11, 22, 21, 15, 11, 103000)
        )
        self.assertEqual(
            cve.last_modified, datetime(2022, 11, 23, 16, 2, 7, 367000)
        )
        self.assertEqual(len(cve.descriptions), 1)
        self.assertEqual(len(cve.references), 2)
        self.assertEqual(len(cve.weaknesses), 0)
        self.assertEqual(len(cve.configurations), 0)
        self.assertEqual(len(cve.vendor_comments), 0)
        self.assertIsNone(cve.metrics)
        self.assertIsNone(cve.evaluator_comment)
        self.assertIsNone(cve.evaluator_solution)
        self.assertIsNone(cve.evaluator_impact)
        self.assertIsNone(cve.cisa_exploit_add)
        self.assertIsNone(cve.cisa_action_due)
        self.assertIsNone(cve.cisa_required_action)
        self.assertIsNone(cve.cisa_vulnerability_name)

    async def test_cves(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves())
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0},
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 1, "resultsPerPage": 1},
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    @patch("pontos.nvd.cve.api.now", spec=now)
    async def test_cves_last_modified_start_date(self, now_mock: MagicMock):
        now_mock.return_value = datetime(2022, 12, 31)
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(
            self.api.cves(last_modified_start_date=datetime(2022, 12, 1))
        )
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "lastModStartDate": "2022-12-01T00:00:00",
                "lastModEndDate": "2022-12-31T00:00:00",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "lastModStartDate": "2022-12-01T00:00:00",
                "lastModEndDate": "2022-12-31T00:00:00",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_last_modified_end_date(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(
            self.api.cves(
                last_modified_start_date=datetime(2022, 12, 1),
                last_modified_end_date=datetime(2022, 12, 31),
            )
        )
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "lastModStartDate": "2022-12-01T00:00:00",
                "lastModEndDate": "2022-12-31T00:00:00",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "lastModStartDate": "2022-12-01T00:00:00",
                "lastModEndDate": "2022-12-31T00:00:00",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    @patch("pontos.nvd.cve.api.now", spec=now)
    async def test_cves_published_start_date(self, now_mock: MagicMock):
        now_mock.return_value = datetime(2022, 12, 31)
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(published_start_date=datetime(2022, 12, 1)))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "pubStartDate": "2022-12-01T00:00:00",
                "pubEndDate": "2022-12-31T00:00:00",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "pubStartDate": "2022-12-01T00:00:00",
                "pubEndDate": "2022-12-31T00:00:00",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_published_end_date(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(
            self.api.cves(
                published_start_date=datetime(2022, 12, 1),
                published_end_date=datetime(2022, 12, 31),
            )
        )
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "pubStartDate": "2022-12-01T00:00:00",
                "pubEndDate": "2022-12-31T00:00:00",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "pubStartDate": "2022-12-01T00:00:00",
                "pubEndDate": "2022-12-31T00:00:00",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_cpe_name(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(cpe_name="foo-bar"))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0, "cpeName": "foo-bar"},
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "cpeName": "foo-bar",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_is_vulnerable(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(cpe_name="foo-bar", is_vulnerable=True))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0, "cpeName": "foo-bar", "isVulnerable": ""},
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "cpeName": "foo-bar",
                "isVulnerable": "",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_cvss_v2_vector(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(cvss_v2_vector="AV:N/AC:M/Au:N/C:N/I:P/A:N"))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "cvssV2Metrics": "AV:N/AC:M/Au:N/C:N/I:P/A:N",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "resultsPerPage": 1,
                "cvssV2Metrics": "AV:N/AC:M/Au:N/C:N/I:P/A:N",
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_cvss_v3_vector(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(
            self.api.cves(
                cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N"
            )
        )
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "cvssV3Metrics": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "resultsPerPage": 1,
                "cvssV3Metrics": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N",
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_cvss_v2_severity(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(cvss_v2_severity=cvss_v2.Severity.HIGH))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "cvssV2Severity": "HIGH",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "resultsPerPage": 1,
                "cvssV2Severity": "HIGH",
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_cvss_v3_severity(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(cvss_v3_severity=cvss_v3.Severity.HIGH))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "cvssV3Severity": "HIGH",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "resultsPerPage": 1,
                "cvssV3Severity": "HIGH",
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_keywords(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(keywords=["Mac OS X", "kernel"]))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "keywordSearch": "Mac OS X kernel",
                "keywordExactMatch": "",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "resultsPerPage": 1,
                "keywordSearch": "Mac OS X kernel",
                "keywordExactMatch": "",
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_keyword(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(keywords="Windows"))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "keywordSearch": "Windows",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "resultsPerPage": 1,
                "keywordSearch": "Windows",
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_cwe(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(cwe_id="CWE-1"))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0, "cweId": "CWE-1"},
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 1, "resultsPerPage": 1, "cweId": "CWE-1"},
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_source_identifier(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(source_identifier="nvd@nist.gov"))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "sourceIdentifier": "nvd@nist.gov",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "sourceIdentifier": "nvd@nist.gov",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_virtual_match_string(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(virtual_match_string="foo-bar"))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 0,
                "virtualMatchString": "foo-bar",
            },
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "virtualMatchString": "foo-bar",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_has_cert_alerts(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(has_cert_alerts=True))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0, "hasCertAlerts": ""},
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "hasCertAlerts": "",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_has_cert_notes(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(has_cert_notes=True))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0, "hasCertNotes": ""},
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "hasCertNotes": "",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_has_kev(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(has_kev=True))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0, "hasKev": ""},
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "hasKev": "",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_cves_has_oval(self):
        self.http_client.get.side_effect = create_cves_responses()

        it = aiter(self.api.cves(has_oval=True))
        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-1")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={"startIndex": 0, "hasOval": ""},
        )

        self.http_client.get.reset_mock()

        cve = await anext(it)

        self.assertEqual(cve.id, "CVE-2")
        self.http_client.get.assert_awaited_once_with(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            headers={"apiKey": "token"},
            params={
                "startIndex": 1,
                "hasOval": "",
                "resultsPerPage": 1,
            },
        )

        with self.assertRaises(StopAsyncIteration):
            cve = await anext(it)

    async def test_context_manager(self):
        async with self.api:
            pass

        self.http_client.__aenter__.assert_awaited_once()
        self.http_client.__aexit__.assert_awaited_once()

    @patch("pontos.nvd.api.sleep", spec=sleep)
    async def test_rate_limit(self, sleep_mock: MagicMock):
        self.http_client.get.side_effect = create_cves_responses(6)
        self.api._rate_limit = 5  # pylint: disable=protected-access

        it = aiter(self.api.cves())
        await anext(it)
        await anext(it)
        await anext(it)
        await anext(it)
        await anext(it)

        sleep_mock.assert_not_called()

        await anext(it)

        sleep_mock.assert_called_once_with()
