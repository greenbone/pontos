# Copyright (C) 2023 Greenbone Networks GmbH
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

import unittest
from datetime import datetime

from pontos.version.calculator import VersionCalculator
from pontos.version.errors import VersionError


class VersionCalculatorTestCase(unittest.TestCase):
    def test_next_patch_version(self):
        calculator = VersionCalculator()
        today = datetime.today()

        current_versions = [
            "20.4.1.dev3",
            f"{str(today.year % 100)}.4.1.dev3",
            f"19.{str(today.month)}.1.dev3",
            f"{str(today.year % 100)}.{str(today.month)}.1",
            "20.6.1",
        ]
        assert_versions = [
            "20.4.1",
            f"{str(today.year % 100)}.4.1",
            f"19.{str(today.month)}.1",
            f"{str(today.year % 100)}.{str(today.month)}.2",
            "20.6.2",
        ]

        for current_version, assert_version in zip(
            current_versions, assert_versions
        ):
            release_version = calculator.next_patch_version(current_version)

            self.assertEqual(release_version, assert_version)

    def test_next_patch_version_invalid_version(self):
        calculator = VersionCalculator()

        with self.assertRaisesRegex(VersionError, "Invalid version: 'abc'"):
            calculator.next_patch_version("abc")

    def test_next_calendar_versions(self):
        calculator = VersionCalculator()
        today = datetime.today()
        year_short = today.year % 100

        current_versions = [
            "21.4.1.dev3",
            f"19.{today.month}.1.dev3",
            f"{year_short}.{today.month}.1.dev3",
            f"{year_short}.{today.month}.1",
        ]
        assert_versions = [
            f"{year_short}.{today.month}.0",
            f"{year_short}.{today.month}.0",
            f"{year_short}.{today.month}.1",
            f"{year_short}.{today.month}.2",
        ]

        for current_version, assert_version in zip(
            current_versions, assert_versions
        ):
            release_version = calculator.next_calendar_version(current_version)
            self.assertEqual(release_version, assert_version)

    def test_next_calendar_version_error(self):
        calculator = VersionCalculator()
        today = datetime.today()
        year_short = today.year % 100

        with self.assertRaisesRegex(VersionError, "'.+' is higher than '.+'."):
            calculator.next_calendar_version(f"{year_short  + 1}.1.0")

        with self.assertRaisesRegex(VersionError, "'.+' is higher than '.+'."):
            calculator.next_calendar_version(
                f"{year_short}.{today.month + 1}.0"
            )