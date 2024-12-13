# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# pylint: disable=line-too-long
# ruff: noqa: E501

import unittest
from datetime import datetime, timezone
from uuid import UUID

from pontos.nvd.models.cpe_match_string import CPEMatch, CPEMatchString
from tests.nvd import get_cpe_match_data


class CPEMatchTestCase(unittest.TestCase):

    def test_required_only(self):
        """
        Test the required attributes of a CPEMatchString
        """
        data = get_cpe_match_data()
        data.__delitem__("matches")
        data.__delitem__("version_end_including")
        data.__delitem__("cpe_last_modified")

        cpe_match_string = CPEMatchString.from_dict(data)

        self.assertEqual(
            UUID("EAB2C9C2-F685-450B-9980-553966FC3B63"),
            cpe_match_string.match_criteria_id,
        )
        self.assertEqual(
            "cpe:2.3:a:sun:jre:*:update3:*:*:*:*:*:*",
            cpe_match_string.criteria,
        )
        self.assertEqual(
            "Active",
            cpe_match_string.status,
        )
        self.assertEqual(
            datetime(2019, 6, 17, 9, 16, 33, 960000, tzinfo=timezone.utc),
            cpe_match_string.created,
        )
        self.assertEqual(
            datetime(2019, 6, 17, 9, 16, 44, 0, tzinfo=timezone.utc),
            cpe_match_string.last_modified,
        )

        self.assertEqual([], cpe_match_string.matches)

        self.assertIsNone(cpe_match_string.cpe_last_modified)
        self.assertIsNone(cpe_match_string.version_start_excluding)
        self.assertIsNone(cpe_match_string.version_end_excluding)
        self.assertIsNone(cpe_match_string.version_start_including)
        self.assertIsNone(cpe_match_string.version_end_including)

    def test_cpe_last_modified(self):
        data = get_cpe_match_data()
        cpe_match_string = CPEMatchString.from_dict(data)

        self.assertEqual(
            datetime(2019, 7, 22, 16, 37, 38, 133000, tzinfo=timezone.utc),
            cpe_match_string.cpe_last_modified,
        )

    def test_matches(self):
        """
        Test the matches list of a CPEMatchString
        """
        cpe_match_string = CPEMatchString.from_dict(get_cpe_match_data())

        self.assertEqual(5, len(cpe_match_string.matches))

        self.assertEqual(
            CPEMatch(
                "cpe:2.3:a:sun:jre:1.3.0:update3:*:*:*:*:*:*",
                UUID("2d284534-da21-43d5-9d89-07f19ae400ea"),
            ),
            cpe_match_string.matches[0],
        )

        self.assertEqual(
            CPEMatch(
                "cpe:2.3:a:sun:jre:1.6.0:update3:*:*:*:*:*:*",
                UUID("c518a954-369e-453e-8e17-2af639150115"),
            ),
            cpe_match_string.matches[-1],
        )

    def test_including_version_limits(self):
        """
        Test the including version limits of a CPEMatchString
        """
        data = get_cpe_match_data({"version_start_including": "1.3.0"})
        cpe_match_string = CPEMatchString.from_dict(data)

        self.assertEqual("1.3.0", cpe_match_string.version_start_including)
        self.assertEqual("1.6.0", cpe_match_string.version_end_including)
        self.assertIsNone(cpe_match_string.version_start_excluding)
        self.assertIsNone(cpe_match_string.version_end_excluding)

    def test_excluding_version_limits(self):
        """
        Test the excluding version limits of a CPEMatchString
        """
        data = get_cpe_match_data(
            {
                "version_start_excluding": "1.2.0",
                "version_end_excluding": "1.7.0",
            }
        )
        data.__delitem__("version_end_including")
        cpe_match_string = CPEMatchString.from_dict(data)

        self.assertEqual("1.2.0", cpe_match_string.version_start_excluding)
        self.assertEqual("1.7.0", cpe_match_string.version_end_excluding)
        self.assertIsNone(cpe_match_string.version_start_including)
        self.assertIsNone(cpe_match_string.version_end_including)
