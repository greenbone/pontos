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

        current_versions = [
            "0.0.1",
            "1.2.3",
            "1.2.3.post1",
            "1.2.3a1",
            "1.2.3b1",
            "1.2.3rc1",
            "22.4.1",
            "22.4.1.dev1",
            "22.4.1.dev3",
        ]
        assert_versions = [
            "0.0.2",
            "1.2.4",
            "1.2.4",
            "1.2.3",
            "1.2.3",
            "1.2.3",
            "22.4.2",
            "22.4.1",
            "22.4.1",
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

    def test_next_minor_version(self):
        calculator = VersionCalculator()

        current_versions = [
            "0.0.1",
            "1.2.3",
            "1.2.3.post1",
            "1.2.3a1",
            "1.2.3b1",
            "1.2.3rc1",
            "22.4.1",
            "22.4.1.dev1",
            "22.4.1.dev3",
        ]
        assert_versions = [
            "0.1.0",
            "1.3.0",
            "1.3.0",
            "1.3.0",
            "1.3.0",
            "1.3.0",
            "22.5.0",
            "22.5.0",
            "22.5.0",
        ]

        for current_version, assert_version in zip(
            current_versions, assert_versions
        ):
            release_version = calculator.next_minor_version(current_version)
            self.assertEqual(release_version, assert_version)

    def test_next_minor_version_error(self):
        calculator = VersionCalculator()
        with self.assertRaisesRegex(VersionError, "Invalid version: 'abc'"):
            calculator.next_minor_version("abc")

    def test_next_major_version(self):
        calculator = VersionCalculator()

        current_versions = [
            "0.0.1",
            "1.2.3",
            "1.2.3.post1",
            "1.2.3a1",
            "1.2.3b1",
            "1.2.3rc1",
            "22.4.1",
            "22.4.1.dev1",
            "22.4.1.dev3",
        ]
        assert_versions = [
            "1.0.0",
            "2.0.0",
            "2.0.0",
            "2.0.0",
            "2.0.0",
            "2.0.0",
            "23.0.0",
            "23.0.0",
            "23.0.0",
        ]

        for current_version, assert_version in zip(
            current_versions, assert_versions
        ):
            release_version = calculator.next_major_version(current_version)
            self.assertEqual(release_version, assert_version)

    def test_next_major_version_error(self):
        calculator = VersionCalculator()
        with self.assertRaisesRegex(VersionError, "Invalid version: 'abc'"):
            calculator.next_major_version("abc")
