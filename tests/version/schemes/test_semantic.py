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

from pontos.version.errors import VersionError
from pontos.version.schemes._pep440 import PEP440Version
from pontos.version.schemes._semantic import SemanticVersion as Version
from pontos.version.schemes._semantic import (
    SemanticVersionCalculator as VersionCalculator,
)


class SemanticVersionTestCase(unittest.TestCase):
    def test_parse_version(self):
        versions = [
            "0.0.1",
            "1.2.3",
            "1.2.3-foo1",
            "1.2.3-a1",
            "1.2.3-alpha1",
            "1.2.3-alpha1-dev1",
            "1.2.3-b1",
            "1.2.3-beta1",
            "1.2.3-beta1-dev1",
            "1.2.3-rc1",
            "1.2.3-rc1-dev1",
            "1.2.3-dev1",
            "1.2.3+foo1",
            "22.4.1",
            "22.4.1-dev1",
            "22.4.1-dev3",
        ]
        for version in versions:
            self.assertEqual(Version.from_string(version), Version(version))

    def test_parsed_version(self):
        versions = [
            "0.0.1",
            "1.2.3",
            "1.2.3-foo1",
            "1.2.3-a1",
            "1.2.3-alpha1",
            "1.2.3-alpha1-dev1",
            "1.2.3-b1",
            "1.2.3-beta1",
            "1.2.3-beta1-dev1",
            "1.2.3-rc1",
            "1.2.3-rc1-dev1",
            "1.2.3-dev1",
            "1.2.3+foo1",
            "22.4.1",
            "22.4.1-dev1",
            "22.4.1-dev3",
        ]
        for version in versions:
            self.assertEqual(
                Version.from_string(version).parsed_version, version
            )

        pep440_version = PEP440Version.from_string("22.4.1.dev1")
        semver_version = Version.from_version(pep440_version)

        self.assertEqual(str(semver_version), "22.4.1-dev1")
        self.assertEqual(semver_version.parsed_version, "22.4.1.dev1")

    def test_parse_error(self):
        versions = [
            "abc",
            "1.2.3d",
            "1.2.3.post1",
            "1.2.3a1",
            "1.2.3b1",
            "1.2.3rc1",
            "1.2.3a1+dev1",
            "22.4.1.dev1",
            "22.4.1.dev3",
        ]

        for version in versions:
            with self.assertRaisesRegex(
                VersionError, "^.* is not valid SemVer string$"
            ):
                Version.from_string(version)

    def test_parse_prerelease_error(self):
        versions = [
            "1.2.3-pos1t1",
            "1.2.3-dev1-dev1",
        ]

        for version in versions:
            with self.assertRaisesRegex(
                VersionError, f"^Invalid prerelease .* in {version}"
            ):
                Version.from_string(version)

    def test_equal(self):
        versions = [
            ("1.0.0", "1.0.0"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0-dev1", "1.0.0-dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev1"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1-dev1"),
        ]
        for version1, version2 in versions:
            self.assertTrue(
                Version.from_string(version1) == Version.from_string(version2),
                f"{version1} does not equal {version2}",
            )

        versions = [
            ("1.0.0", "1.0.1"),
            ("1.0.0", "1.0.0+dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0+dev1", "1.0.0-dev1"),
            ("1.0.0+dev1", "1.0.0+dev2"),
            ("1.0.0-alpha1", "1.0.0-beta1"),
            ("1.0.0-alpha1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1+dev1", "1.0.0-rc1+dev2"),
        ]
        for version1, version2 in versions:
            self.assertFalse(
                Version.from_string(version1) == Version.from_string(version2),
                f"{version1} equals {version2}",
            )

        other = None
        self.assertFalse(Version.from_string("1.0.0") == other)

        versions = [
            ("1.0.0", object()),
            ("1.0.0", 1),
            ("1.0.0", True),
        ]
        for version1, version2 in versions:
            with self.assertRaisesRegex(ValueError, "Can't compare"):
                self.assertFalse(Version.from_string(version1) == version2)

    def test_equal_pep440_version(self):
        versions = [
            ("1.0.0", "1.0.0"),
            ("1.0.0-dev1", "1.0.0-dev1"),
            ("1.0.0-dev1", "1.0.0.dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-alpha1", "1.0.0a1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev1"),
            ("1.0.0-alpha1-dev1", "1.0.0a1.dev1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-beta1", "1.0.0b1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev1"),
            ("1.0.0-beta1-dev1", "1.0.0b1.dev1"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1.dev1"),
            ("1.0.0-rc1-dev1", "1.0.0rc1.dev1"),
        ]
        for version1, version2 in versions:
            semver = Version.from_string(version1)
            pep440 = PEP440Version.from_string(version2)
            self.assertTrue(
                semver == pep440,
                f"{semver!r} {version1} does not equal {pep440!r} {version2}",
            )

    def test_not_equal(self):
        versions = [
            ("1.0.0", "1.0.0"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1"),
        ]
        for version1, version2 in versions:
            self.assertFalse(
                Version.from_string(version1) != Version.from_string(version2),
                f"{version1} does not equal {version2}",
            )

        versions = [
            ("1.0.0", "1.0.1"),
            ("1.0.0", "1.0.0+dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0+dev1", "1.0.0+dev2"),
            ("1.0.0-alpha1", "1.0.0-beta1"),
            ("1.0.0-alpha1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1+dev1", "1.0.0-rc1+dev2"),
        ]
        for version1, version2 in versions:
            self.assertTrue(
                Version.from_string(version1) != Version.from_string(version2),
                f"{version1} equals {version2}",
            )

        versions = [
            ("1.0.0", "abc"),
            ("1.0.0", None),
        ]
        for version1, version2 in versions:
            self.assertTrue(Version.from_string(version1) != version2)

        versions = [
            ("1.0.0", object()),
            ("1.0.0", 1),
            ("1.0.0", True),
        ]
        for version1, version2 in versions:
            with self.assertRaisesRegex(ValueError, "Can't compare"):
                self.assertFalse(Version.from_string(version1) != version2)

    def test_greater_then(self):
        versions = [
            ("1.0.0", "0.9.9999"),
            ("1.0.1", "1.0.0"),
            ("1.0.0", "1.0.0-dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0", "1.0.0-rc1"),
            ("1.0.0-alpha1", "1.0.0-dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1-dev1"),
            ("1.0.0-alpha2", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-dev1"),
            ("1.0.0-beta1", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-beta1-dev1"),
            ("1.0.0-beta2", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-dev1"),
            ("1.0.0-rc1", "1.0.0-alpha1"),
            ("1.0.0-rc1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1-dev1"),
            ("1.0.0-rc2", "1.0.0-rc1"),
        ]
        for version1, version2 in versions:
            self.assertTrue(
                Version.from_string(version1) > Version.from_string(version2),
                f"{version1} should be greater then {version2}",
            )

        versions = [
            ("1.0.0", "1.0.0"),
            ("1.0.0", "1.0.0+dev1"),
            ("1.0.0-dev1", "1.0.0-dev1"),
            ("1.0.0-dev1", "1.0.0-dev2"),
            ("1.0.0", "1.0.1"),
            ("1.0.0-dev1", "1.0.0"),
            ("1.0.0-dev1", "1.0.0-alpha1"),
            ("1.0.0-dev1", "1.0.0-beta1"),
            ("1.0.0-dev1", "1.0.0-rc1"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0+dev1", "1.0.0+dev2"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-alpha1", "1.0.0-beta1"),
            ("1.0.0-alpha1", "1.0.0-rc1"),
            ("1.0.0-alpha1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev2"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-rc1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev2"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1-dev1"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1-dev2"),
            ("1.0.0-rc1+dev1", "1.0.0-rc1+dev2"),
        ]
        for version1, version2 in versions:
            self.assertFalse(
                Version.from_string(version1) > Version.from_string(version2),
                f"{version1} should not be greater then {version2}",
            )

        versions = [
            ("1.0.0", object()),
            ("1.0.0", 1),
            ("1.0.0", True),
        ]
        for version1, version2 in versions:
            with self.assertRaisesRegex(ValueError, "Can't compare"):
                self.assertFalse(Version.from_string(version1) > version2)

    def test_greater_or_equal_then(self):
        versions = [
            ("1.0.0", "0.9.9999"),
            ("1.0.0", "1.0.0"),
            ("1.0.1", "1.0.0"),
            ("1.0.0", "1.0.0-dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0", "1.0.0-rc1"),
            ("1.0.0-dev1", "1.0.0-dev1"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0-alpha1", "1.0.0-dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-alpha1", "1.0.0-alpha1-dev1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev1"),
            ("1.0.0-alpha2", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-dev1"),
            ("1.0.0-beta1", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-beta1", "1.0.0-beta1-dev1"),
            ("1.0.0-beta2", "1.0.0-beta1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev1"),
            ("1.0.0-rc1", "1.0.0-dev1"),
            ("1.0.0-rc1", "1.0.0-alpha1"),
            ("1.0.0-rc1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0-rc1", "1.0.0-rc1-dev1"),
            ("1.0.0-rc2", "1.0.0-rc1"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1-dev1"),
        ]
        for version1, version2 in versions:
            self.assertTrue(
                Version.from_string(version1) >= Version.from_string(version2),
                f"{version1} should be greater or equal then {version2}",
            )

        versions = [
            ("1.0.0", "1.0.0+dev1"),
            ("1.0.0-dev1", "1.0.0-dev2"),
            ("1.0.0", "1.0.1"),
            ("1.0.0-dev1", "1.0.0"),
            ("1.0.0-dev1", "1.0.0-alpha1"),
            ("1.0.0-dev1", "1.0.0-beta1"),
            ("1.0.0-dev1", "1.0.0-rc1"),
            ("1.0.0+dev1", "1.0.0+dev2"),
            ("1.0.0-alpha1", "1.0.0-beta1"),
            ("1.0.0-alpha1", "1.0.0-rc1"),
            ("1.0.0-alpha1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev2"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-rc1"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev2"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1-dev2"),
            ("1.0.0-rc1+dev1", "1.0.0-rc1+dev2"),
        ]
        for version1, version2 in versions:
            self.assertFalse(
                Version.from_string(version1) >= Version.from_string(version2),
                f"{version1} should not be greater or equal then {version2}",
            )

        versions = [
            ("1.0.0", object()),
            ("1.0.0", 1),
            ("1.0.0", True),
        ]
        for version1, version2 in versions:
            with self.assertRaisesRegex(ValueError, "Can't compare"):
                self.assertFalse(Version.from_string(version1) >= version2)

    def test_less_then(self):
        versions = [
            ("1.0.0", "0.9.9999"),
            ("1.0.1", "1.0.0"),
            ("1.0.0", "1.0.0-dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0", "1.0.0-rc1"),
            ("1.0.0-alpha1", "1.0.0-dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1-dev1"),
            ("1.0.0-alpha2", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-dev1"),
            ("1.0.0-beta1", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-beta1-dev1"),
            ("1.0.0-beta2", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-dev1"),
            ("1.0.0-rc1", "1.0.0-alpha1"),
            ("1.0.0-rc1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1-dev1"),
            ("1.0.0-rc2", "1.0.0-rc1"),
            # the following ones are strange with current semver implementation
            # because they are both less then and greater then at the same time
            ("1.0.0", "1.0.0+dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1+dev1"),
            ("1.0.0+dev1", "1.0.0+dev2"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1+dev1", "1.0.0-rc1+dev2"),
        ]
        for version2, version1 in versions:
            self.assertTrue(
                Version.from_string(version1) < Version.from_string(version2),
                f"{version1} should be less then {version2}",
            )

        versions = [
            ("1.0.0", "1.0.0"),
            ("1.0.0-dev1", "1.0.0-dev1"),
            ("1.0.0-dev1", "1.0.0-dev2"),
            ("1.0.0", "1.0.1"),
            ("1.0.0-dev1", "1.0.0"),
            ("1.0.0-dev1", "1.0.0-alpha1"),
            ("1.0.0-dev1", "1.0.0-beta1"),
            ("1.0.0-dev1", "1.0.0-rc1"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-alpha1", "1.0.0-beta1"),
            ("1.0.0-alpha1", "1.0.0-rc1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev2"),
            ("1.0.0-beta1", "1.0.0-rc1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev2"),
            ("1.0.0-rc1", "1.0.0"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1-dev1"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1-dev2"),
        ]
        for version2, version1 in versions:
            self.assertFalse(
                Version.from_string(version1) < Version.from_string(version2),
                f"{version1} should not be less then {version2}",
            )

        versions = [
            ("1.0.0", object()),
            ("1.0.0", 1),
            ("1.0.0", True),
        ]
        for version1, version2 in versions:
            with self.assertRaisesRegex(ValueError, "Can't compare"):
                self.assertFalse(Version.from_string(version1) < version2)

    def test_less_or_equal_then(self):
        versions = [
            ("1.0.0", "0.9.9999"),
            ("1.0.0", "1.0.0"),
            ("1.0.1", "1.0.0"),
            ("1.0.0", "1.0.0-dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0", "1.0.0-rc1"),
            ("1.0.0-dev1", "1.0.0-dev1"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0-alpha1", "1.0.0-dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-alpha1", "1.0.0-alpha1-dev1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev1"),
            ("1.0.0-alpha2", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-dev1"),
            ("1.0.0-beta1", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-beta1", "1.0.0-beta1-dev1"),
            ("1.0.0-beta2", "1.0.0-beta1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev1"),
            ("1.0.0-rc1", "1.0.0-dev1"),
            ("1.0.0-rc1", "1.0.0-alpha1"),
            ("1.0.0-rc1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0-rc1", "1.0.0-rc1-dev1"),
            ("1.0.0-rc2", "1.0.0-rc1"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1-dev1"),
            # the strange ones
            ("1.0.0", "1.0.0+dev1"),
            ("1.0.0+dev1", "1.0.0+dev2"),
            ("1.0.0-alpha1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1+dev1", "1.0.0-rc1+dev2"),
        ]
        for version2, version1 in versions:
            self.assertTrue(
                Version.from_string(version1) <= Version.from_string(version2),
                f"{version1} should be greater or equal then {version2}",
            )

        versions = [
            ("1.0.0-dev1", "1.0.0-dev2"),
            ("1.0.0", "1.0.1"),
            ("1.0.0-dev1", "1.0.0"),
            ("1.0.0-dev1", "1.0.0-alpha1"),
            ("1.0.0-dev1", "1.0.0-beta1"),
            ("1.0.0-dev1", "1.0.0-rc1"),
            ("1.0.0-alpha1", "1.0.0-beta1"),
            ("1.0.0-alpha1", "1.0.0-rc1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev2"),
            ("1.0.0-beta1", "1.0.0-rc1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev2"),
            ("1.0.0-rc1", "1.0.0"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1-dev2"),
        ]
        for version2, version1 in versions:
            self.assertFalse(
                Version.from_string(version1) <= Version.from_string(version2),
                f"{version1} should not be greater or equal then {version2}",
            )

        versions = [
            ("1.0.0", object()),
            ("1.0.0", 1),
            ("1.0.0", True),
        ]
        for version1, version2 in versions:
            with self.assertRaisesRegex(ValueError, "Can't compare"):
                self.assertFalse(Version.from_string(version1) <= version2)

    def test_is_dev_release(self):
        versions = [
            "1.0.0-dev1",
            "1.0.0-alpha1-dev1",
            "1.0.0-beta1-dev1",
            "1.0.0-rc1-dev1",
        ]
        for version in versions:
            self.assertTrue(
                Version.from_string(version).is_dev_release,
                f"{version} is not a dev release",
            )

        versions = [
            "1.0.0",
            "1.0.0+foo1",
            "1.0.0+dev1",
            "1.0.0-alpha1",
            "1.0.0-beta1",
            "1.0.0-rc1",
            "1.0.0-alpha1+dev1",
            "1.0.0-beta1+dev1",
            "1.0.0-rc1+dev1",
        ]
        for version in versions:
            self.assertFalse(
                Version.from_string(version).is_dev_release,
                f"{version} is a dev release",
            )

    def test_is_alpha_release(self):
        versions = [
            "1.0.0-alpha1",
            "1.0.0-alpha1+foo1",
            "1.0.0-alpha1-foo1",
            "1.0.0-alpha1+dev1",
            "1.0.0-alpha1-dev1",
        ]
        for version in versions:
            self.assertTrue(
                Version.from_string(version).is_alpha_release,
                f"{version} is not an alpha release",
            )

        versions = [
            "1.0.0",
            "1.0.0+dev1",
            "1.0.0-dev1",
            "1.0.0-a1",
            "1.0.0-b1",
            "1.0.0-rc1",
        ]
        for version in versions:
            self.assertFalse(
                Version.from_string(version).is_alpha_release,
                f"{version} is an alpha release",
            )

    def test_is_beta_release(self):
        versions = [
            "1.0.0-beta1",
            "1.0.0-beta1+foo1",
            "1.0.0-beta1-foo1",
            "1.0.0-beta1+dev1",
            "1.0.0-beta1-dev1",
        ]
        for version in versions:
            self.assertTrue(
                Version.from_string(version).is_beta_release,
                f"{version} is not a beta release",
            )

        versions = [
            "1.0.0",
            "1.0.0-dev1",
            "1.0.0+dev1",
            "1.0.0-alpha1",
            "1.0.0-b1",
            "1.0.0-rc1",
        ]
        for version in versions:
            self.assertFalse(
                Version.from_string(version).is_beta_release,
                f"{version} is a beta release",
            )

    def test_is_release_candidate(self):
        versions = [
            "1.0.0-rc1",
            "1.0.0-rc1+foo1",
            "1.0.0-rc1-foo1",
            "1.0.0-rc1+dev1",
            "1.0.0-rc1-dev1",
        ]
        for version in versions:
            self.assertTrue(
                Version.from_string(version).is_release_candidate,
                f"{version} is not a release candidate",
            )

        versions = [
            "1.0.0",
            "1.0.0+dev1",
            "1.0.0-dev1",
            "1.0.0-alpha1",
            "1.0.0-beta1",
        ]
        for version in versions:
            self.assertFalse(
                Version.from_string(version).is_release_candidate,
                f"{version} is a release candidate",
            )

    def test_pre(self):
        versions = [
            ("1.0.0", None),
            ("1.0.0+dev1", None),
            ("1.0.0-dev1", None),
            ("1.0.0-alpha1", ("alpha", 1)),
            ("1.0.0-beta1", ("beta", 1)),
            ("1.0.0-rc1", ("rc", 1)),
            ("1.0.0-rc1+foo1", ("rc", 1)),
            ("1.0.0-alpha1+dev1", ("alpha", 1)),
            ("1.0.0-beta1+dev1", ("beta", 1)),
            ("1.0.0-rc1+dev1", ("rc", 1)),
            ("1.0.0-alpha1-dev1", ("alpha", 1)),
            ("1.0.0-beta1-dev1", ("beta", 1)),
            ("1.0.0-rc1-dev1", ("rc", 1)),
        ]

        for version, expected in versions:
            self.assertEqual(Version.from_string(version).pre, expected)

    def test_local(self):
        versions = [
            ("1.0.0", None),
            ("1.0.0+foo1", ("foo", 1)),
            ("1.0.0+dev1", ("dev", 1)),
            ("1.0.0-dev1", None),
            ("1.0.0-alpha1", None),
            ("1.0.0-beta1", None),
            ("1.0.0-rc1", None),
            ("1.0.0-rc1+foo1", ("foo", 1)),
            ("1.0.0-alpha1+dev1", ("dev", 1)),
            ("1.0.0-beta1+dev1", ("dev", 1)),
            ("1.0.0-rc1+dev1", ("dev", 1)),
            ("1.0.0-alpha1-dev1", None),
            ("1.0.0-beta1-dev1", None),
            ("1.0.0-rc1-dev1", None),
        ]

        for version, expected in versions:
            local = Version.from_string(version).local
            self.assertEqual(
                local,
                expected,
                f"{version} has not the expected local {expected}. Instead it "
                f"is {local}",
            )


class SemanticVersionCalculatorTestCase(unittest.TestCase):
    def test_next_patch_version(self):
        calculator = VersionCalculator()

        versions = [
            ("0.0.1", "0.0.2"),
            ("1.2.3", "1.2.4"),
            ("1.2.3+dev1", "1.2.4"),
            ("1.2.3-dev1", "1.2.3"),
            ("1.2.3-foo1", "1.2.3"),
            ("1.2.3-alpha1", "1.2.3"),
            ("1.2.3-beta1", "1.2.3"),
            ("1.2.3-rc1", "1.2.3"),
            ("1.2.3-alpha1+dev1", "1.2.3"),
            ("1.2.3-beta1+dev1", "1.2.3"),
            ("1.2.3-rc1+dev1", "1.2.3"),
            ("1.2.3-alpha1-dev1", "1.2.3"),
            ("1.2.3-beta1-dev1", "1.2.3"),
            ("1.2.3-rc1-dev1", "1.2.3"),
            ("22.4.1", "22.4.2"),
            ("22.4.1+dev3", "22.4.2"),
            ("22.4.1-dev1", "22.4.1"),
            ("22.4.1-dev3", "22.4.1"),
            ("1.0.0-a1", "1.0.0"),
            ("1.1.0-alpha1", "1.1.0"),
            ("1.0.0+dev1", "1.0.1"),
            ("1.1.0+dev1", "1.1.1"),
            ("1.0.0-dev1", "1.0.0"),
            ("1.1.0-dev1", "1.1.0"),
        ]

        for current_version, assert_version in versions:
            release_version = calculator.next_patch_version(
                Version.from_string(current_version)
            )

            self.assertEqual(
                release_version,
                Version.from_string(assert_version),
                f"{release_version} is not the expected next patch version "
                f"{assert_version} for {current_version}",
            )

    def test_next_calendar_versions(self):
        calculator = VersionCalculator()
        today = datetime.today()
        year_short = today.year % 100

        current_versions = [
            "21.4.1-dev3",
            f"19.{today.month}.1-dev3",
            f"{year_short}.{today.month}.1-dev3",
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
            release_version = calculator.next_calendar_version(
                Version.from_string(current_version)
            )
            self.assertEqual(
                release_version, Version.from_string(assert_version)
            )

    def test_next_calendar_version_error(self):
        calculator = VersionCalculator()
        today = datetime.today()
        year_short = today.year % 100

        with self.assertRaisesRegex(VersionError, "'.+' is higher than '.+'."):
            calculator.next_calendar_version(
                Version.from_string(f"{year_short  + 1}.1.0")
            )

        with self.assertRaisesRegex(VersionError, "'.+' is higher than '.+'."):
            calculator.next_calendar_version(
                Version.from_string(f"{year_short}.{today.month + 1}.0")
            )

    def test_next_minor_version(self):
        calculator = VersionCalculator()

        versions = [
            ("0.0.1", "0.1.0"),
            ("1.2.3", "1.3.0"),
            ("1.2.3+dev1", "1.3.0"),
            ("1.2.3-dev1", "1.3.0"),
            ("1.2.3-foo1", "1.3.0"),
            ("1.2.3-alpha1", "1.3.0"),
            ("1.2.3-beta1", "1.3.0"),
            ("1.2.3-rc1", "1.3.0"),
            ("1.2.3-alpha1+dev1", "1.3.0"),
            ("1.2.3-beta1+dev1", "1.3.0"),
            ("1.2.3-rc1+dev1", "1.3.0"),
            ("22.4.1", "22.5.0"),
            ("22.4.1+dev3", "22.5.0"),
            ("22.4.1-dev1", "22.5.0"),
            ("22.4.1-dev3", "22.5.0"),
            ("1.0.0-a1", "1.0.0"),
            ("1.1.0-alpha1", "1.1.0"),
            ("1.0.0+dev1", "1.1.0"),
            ("1.1.0+dev1", "1.2.0"),
            ("1.0.0-dev1", "1.0.0"),
            ("1.1.0-dev1", "1.1.0"),
        ]
        for current_version, assert_version in versions:
            release_version = calculator.next_minor_version(
                Version.from_string(current_version)
            )
            self.assertEqual(
                release_version,
                Version.from_string(assert_version),
                f"{release_version} is not the expected next minor version "
                f"{assert_version} for {current_version}",
            )

    def test_next_major_version(self):
        calculator = VersionCalculator()

        versions = [
            ("0.0.1", "1.0.0"),
            ("1.2.3", "2.0.0"),
            ("1.2.3+dev1", "2.0.0"),
            ("1.2.3-dev1", "2.0.0"),
            ("1.2.3-foo1", "2.0.0"),
            ("1.2.3-alpha1", "2.0.0"),
            ("1.2.3-beta1", "2.0.0"),
            ("1.2.3-rc1", "2.0.0"),
            ("1.2.3-alpha1+dev1", "2.0.0"),
            ("1.2.3-beta1+dev1", "2.0.0"),
            ("1.2.3-rc1+dev1", "2.0.0"),
            ("1.2.3-alpha1-dev1", "2.0.0"),
            ("1.2.3-beta1-dev1", "2.0.0"),
            ("1.2.3-rc1-dev1", "2.0.0"),
            ("22.4.1", "23.0.0"),
            ("22.4.1+dev3", "23.0.0"),
            ("22.4.1-dev1", "23.0.0"),
            ("22.4.1-dev3", "23.0.0"),
            ("1.0.0-a1", "1.0.0"),
            ("1.0.0-beta1", "1.0.0"),
            ("1.1.0-alpha1", "2.0.0"),
            ("1.0.0+dev1", "2.0.0"),
            ("1.1.0+dev1", "2.0.0"),
            ("1.0.0-dev1", "1.0.0"),
            ("1.1.0-dev1", "2.0.0"),
        ]

        for current_version, assert_version in versions:
            release_version = calculator.next_major_version(
                Version.from_string(current_version)
            )
            self.assertEqual(
                release_version,
                Version.from_string(assert_version),
                f"{release_version} is not the expected next major version "
                f"{assert_version} for {current_version}",
            )

    def test_next_alpha_version(self):
        calculator = VersionCalculator()

        versions = [
            ("0.0.1", "0.0.2-alpha1"),
            ("1.2.3", "1.2.4-alpha1"),
            ("1.2.3+dev1", "1.2.4-alpha1"),
            ("1.2.3-dev1", "1.2.3-alpha1"),
            ("1.2.3-post1", "1.2.4-alpha1"),
            ("1.2.3-alpha1", "1.2.3-alpha2"),
            ("1.2.3-beta1", "1.2.4-alpha1"),
            ("1.2.3-rc1", "1.2.4-alpha1"),
            ("1.2.3-alpha1+dev1", "1.2.3-alpha2"),
            ("1.2.3-beta1+dev1", "1.2.4-alpha1"),
            ("1.2.3-rc1+dev1", "1.2.4-alpha1"),
            ("1.2.3-alpha1-dev1", "1.2.3-alpha1"),
            ("1.2.3-beta1-dev1", "1.2.4-alpha1"),
            ("1.2.3-beta1-dev1", "1.2.4-alpha1"),
            ("22.4.1", "22.4.2-alpha1"),
            ("22.4.1+dev3", "22.4.2-alpha1"),
            ("22.4.1-dev1", "22.4.1-alpha1"),
            ("22.4.1-dev3", "22.4.1-alpha1"),
            ("1.0.0-a1", "1.0.1-alpha1"),
            ("1.0.0-beta1", "1.0.1-alpha1"),
            ("1.1.0-alpha1", "1.1.0-alpha2"),
            ("1.0.0+dev1", "1.0.1-alpha1"),
            ("1.1.0+dev1", "1.1.1-alpha1"),
            ("1.0.0-dev1", "1.0.0-alpha1"),
            ("1.1.0-dev1", "1.1.0-alpha1"),
        ]

        for current_version, assert_version in versions:
            release_version = calculator.next_alpha_version(
                Version.from_string(current_version)
            )
            self.assertEqual(
                release_version,
                Version.from_string(assert_version),
                f"{release_version} is not the expected next alpha version "
                f"{assert_version} for {current_version}",
            )

    def test_next_beta_version(self):
        calculator = VersionCalculator()

        versions = [
            ("0.0.1", "0.0.2-beta1"),
            ("1.2.3", "1.2.4-beta1"),
            ("1.2.3+dev1", "1.2.4-beta1"),
            ("1.2.3-dev1", "1.2.3-beta1"),
            ("1.2.3-foo1", "1.2.4-beta1"),
            ("1.2.3-alpha1", "1.2.3-beta1"),
            ("1.2.3-beta1", "1.2.3-beta2"),
            ("1.2.3-rc1", "1.2.4-beta1"),
            ("1.2.3-alpha1+dev1", "1.2.3-beta1"),
            ("1.2.3-beta1+dev1", "1.2.3-beta2"),
            ("1.2.3-rc1+dev1", "1.2.4-beta1"),
            ("1.2.3-alpha1-dev1", "1.2.3-beta1"),
            ("1.2.3-beta1-dev1", "1.2.3-beta1"),
            ("1.2.3-rc1-dev1", "1.2.4-beta1"),
            ("22.4.1", "22.4.2-beta1"),
            ("22.4.1+dev3", "22.4.2-beta1"),
            ("22.4.1-dev1", "22.4.1-beta1"),
            ("22.4.1-dev3", "22.4.1-beta1"),
            # actually 1.0.0-beta1 would also be ok, but it would require to
            # to add extra code for not used versioning
            ("1.0.0-a1", "1.0.1-beta1"),
            ("1.0.0-beta1", "1.0.0-beta2"),
            ("1.1.0-alpha1", "1.1.0-beta1"),
            ("1.0.0+dev1", "1.0.1-beta1"),
            ("1.1.0+dev1", "1.1.1-beta1"),
            ("1.0.0-dev1", "1.0.0-beta1"),
            ("1.1.0-dev1", "1.1.0-beta1"),
        ]

        for current_version, assert_version in versions:
            release_version = calculator.next_beta_version(
                Version.from_string(current_version)
            )
            self.assertEqual(
                release_version,
                Version.from_string(assert_version),
                f"{release_version} is not the expected next beta version "
                f"{assert_version} for {current_version}",
            )

    def test_next_release_candidate_version(self):
        calculator = VersionCalculator()

        versions = [
            ("0.0.1", "0.0.2-rc1"),
            ("1.2.3", "1.2.4-rc1"),
            ("1.2.3+dev1", "1.2.4-rc1"),
            ("1.2.3-dev1", "1.2.3-rc1"),
            ("1.2.3-foo1", "1.2.4-rc1"),
            ("1.2.3-alpha1", "1.2.3-rc1"),
            ("1.2.3-beta1", "1.2.3-rc1"),
            ("1.2.3-rc1", "1.2.3-rc2"),
            ("1.2.3-alpha1+dev1", "1.2.3-rc1"),
            ("1.2.3-beta1+dev1", "1.2.3-rc1"),
            ("1.2.3-rc1+dev1", "1.2.3-rc2"),
            ("1.2.3-alpha1-dev1", "1.2.3-rc1"),
            ("1.2.3-beta1-dev1", "1.2.3-rc1"),
            ("1.2.3-rc1-dev1", "1.2.3-rc1"),
            ("22.4.1", "22.4.2-rc1"),
            ("22.4.1+dev3", "22.4.2-rc1"),
            ("22.4.1-dev1", "22.4.1-rc1"),
            ("22.4.1-dev3", "22.4.1-rc1"),
            ("1.0.0-a1", "1.0.1-rc1"),
            ("1.0.0-beta1", "1.0.0-rc1"),
            ("1.1.0-alpha1", "1.1.0-rc1"),
            ("1.0.0+dev1", "1.0.1-rc1"),
            ("1.1.0+dev1", "1.1.1-rc1"),
            ("1.0.0-dev1", "1.0.0-rc1"),
            ("1.1.0-dev1", "1.1.0-rc1"),
        ]

        for current_version, assert_version in versions:
            release_version = calculator.next_release_candidate_version(
                Version.from_string(current_version)
            )
            self.assertEqual(
                release_version,
                Version.from_string(assert_version),
                f"{release_version} is not the expected next rc version "
                f"{assert_version} for {current_version}",
            )

    def test_next_dev_version(self):
        calculator = VersionCalculator()

        versions = [
            ("0.0.1", "0.0.2-dev1"),
            ("1.2.3", "1.2.4-dev1"),
            ("1.2.3+dev1", "1.2.4-dev1"),
            ("1.2.3-dev1", "1.2.3-dev2"),
            ("1.2.3-foo1", "1.2.3-foo2-dev1"),
            ("1.2.3-alpha1", "1.2.3-alpha2-dev1"),
            ("1.2.3-beta1", "1.2.3-beta2-dev1"),
            ("1.2.3-rc1", "1.2.3-rc2-dev1"),
            ("1.2.3-alpha1+dev1", "1.2.3-alpha2-dev1"),
            ("1.2.3-beta1+dev1", "1.2.3-beta2-dev1"),
            ("1.2.3-rc1+dev1", "1.2.3-rc2-dev1"),
            ("1.2.3-alpha1-dev1", "1.2.3-alpha1-dev2"),
            ("1.2.3-beta1-dev1", "1.2.3-beta1-dev2"),
            ("1.2.3-rc1-dev1", "1.2.3-rc1-dev2"),
            ("22.4.1", "22.4.2-dev1"),
            ("22.4.1+dev3", "22.4.2-dev1"),
            ("22.4.1-dev1", "22.4.1-dev2"),
            ("22.4.1-dev3", "22.4.1-dev4"),
            ("1.0.0-a1", "1.0.0-a2-dev1"),
            ("1.0.0-beta1", "1.0.0-beta2-dev1"),
            ("1.1.0-alpha1", "1.1.0-alpha2-dev1"),
            ("1.0.0+dev1", "1.0.1-dev1"),
            ("1.1.0+dev1", "1.1.1-dev1"),
            ("1.0.0-dev1", "1.0.0-dev2"),
            ("1.1.0-dev1", "1.1.0-dev2"),
        ]

        for current_version, assert_version in versions:
            release_version = calculator.next_dev_version(
                Version.from_string(current_version)
            )
            self.assertEqual(
                release_version,
                Version.from_string(assert_version),
                f"{release_version} is not the expected next development "
                f"version {assert_version} for {current_version}",
            )
