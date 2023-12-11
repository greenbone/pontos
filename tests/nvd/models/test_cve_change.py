# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# pylint: disable=line-too-long
# ruff: noqa: E501

import unittest
from datetime import datetime, timezone
from uuid import UUID

from pontos.nvd.models.cve_change import CVEChange, Detail, EventName
from tests.nvd import get_cve_change_data


class CVEChangeTestCase(unittest.TestCase):
    def test_required_only(self):
        cve_change = CVEChange.from_dict(get_cve_change_data())

        self.assertEqual(cve_change.cve_id, "CVE-2022-0001")
        self.assertEqual(cve_change.event_name, "Initial Analysis")
        self.assertEqual(
            cve_change.cve_change_id,
            UUID("5160FDEB-0FF0-457B-AA36-0AEDCAB2522E"),
        )
        self.assertEqual(cve_change.source_identifier, "nvd@nist.gov")
        self.assertEqual(
            cve_change.created,
            datetime(2022, 3, 18, 20, 13, 8, 123000, tzinfo=timezone.utc),
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


class EventNameTestCase(unittest.TestCase):
    def test_init(self):
        self.assertEqual(
            EventName("Initial Analysis"), EventName.INITIAL_ANALYSIS
        )

    def test__str__(self):
        self.assertEqual(str(EventName.INITIAL_ANALYSIS), "Initial Analysis")
