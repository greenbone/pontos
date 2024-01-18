# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest
from datetime import datetime

from pontos.version._errors import VersionError
from pontos.version.schemes._pep440 import PEP440Version as Version
from pontos.version.schemes._pep440 import (
    PEP440VersionCalculator as VersionCalculator,
)
from pontos.version.schemes._semantic import SemanticVersion


class PEP440VersionTestCase(unittest.TestCase):
    def test_parse_version(self):
        versions = [
            "0.0.1",
            "1.2.3",
            "1.2.3.post1",
            "1.2.3a1",
            "1.2.3b1",
            "1.2.3rc1",
            "1.2.3a1+dev1",
            "1.2.3a1.dev1",
            "22.4.1",
            "22.4.1.dev1",
            "22.4.1.dev3",
            "2022.4.1.dev3",
            "2022.4.1",
        ]
        for version in versions:
            self.assertEqual(Version.from_string(version), Version(version))

    def test_parse_version_from_semver(self):
        versions = [
            "0.0.1",
            "1.2.3",
            "1.2.3-post1.dev1",
            "1.2.3-a1",
            "1.2.3-b1",
            "1.2.3-rc1",
            "1.2.3-a1+dev1",
            "1.2.3-a1-dev1",
            "1.4.1",
            "2.4.1-dev1",
            "2.4.1-dev3",
        ]
        for version in versions:
            self.assertEqual(Version.from_string(version), Version(version))

    def test_parsed_version(self):
        versions = [
            "0.0.1",
            "1.2.3",
            "1.2.3-post1.dev1",
            "1.2.3-a1",
            "1.2.3-b1",
            "1.2.3-rc1",
            "1.2.3-a1+dev1",
            "1.2.3-a1-dev1",
            "1.4.1",
            "2.4.1-dev1",
            "2.4.1-dev3",
            "1.2.3.post1",
            "1.2.3a1",
            "1.2.3b1",
            "1.2.3rc1",
            "1.2.3a1+dev1",
            "1.2.3a1.dev1",
            "22.4.1.dev1",
            "22.4.1.dev3",
            "2022.4.1.dev3",
        ]
        for version in versions:
            self.assertEqual(
                Version.from_string(version).parsed_version, version
            )

        semver_version = SemanticVersion.from_string("22.4.1-dev1")
        pep440_version = Version.from_version(semver_version)

        self.assertEqual(str(pep440_version), "22.4.1.dev1")
        self.assertEqual(pep440_version.parsed_version, "22.4.1-dev1")

    def test_parse_error(self):
        versions = [
            "abc",
            "1.2.3d",
        ]

        for version in versions:
            with self.assertRaisesRegex(
                VersionError, "^Invalid version: '.*'$"
            ):
                Version.from_string(version)

    def test_equal(self):
        versions = [
            ("1.0.0", "1.0.0"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0.dev1", "1.0.0.dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0a1", "1.0.0-alpha1"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev1"),
            ("1.0.0a1.dev1", "1.0.0-alpha1-dev1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0b1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0rc1", "1.0.0-rc1"),
        ]
        for version1, version2 in versions:
            self.assertTrue(
                Version.from_string(version1) == Version.from_string(version2),
                f"{version1} does not equal {version2}",
            )

        versions = [
            ("1.0.0", "1.0.1"),
            ("1.0.0", "1.0.0+dev1"),
            ("1.0.0", "1.0.0.dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0.dev1", "1.0.0.dev2"),
            ("1.0.0+dev1", "1.0.0+dev2"),
            ("1.0.0-alpha1", "1.0.0-beta1"),
            ("1.0.0-alpha1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1-dev1"),
            ("1.0.0-alpha1-dev1", "1.0.0-alpha1-dev2"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1-dev1", "1.0.0-beta1-dev2"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1-dev1", "1.0.0-rc1-dev2"),
            ("1.0.0-rc1+dev1", "1.0.0-rc1+dev2"),
        ]
        for version1, version2 in versions:
            self.assertFalse(
                Version.from_string(version1) == Version.from_string(version2),
                f"{version1} equals {version2}",
            )

        versions = [
            ("1.0.0", "abc"),
            ("1.0.0", None),
        ]
        for version1, version2 in versions:
            self.assertFalse(Version.from_string(version1) == version2)

        versions = [
            ("1.0.0", object()),
            ("1.0.0", 1),
        ]
        for version1, version2 in versions:
            with self.assertRaisesRegex(ValueError, "Can't compare"):
                self.assertFalse(Version.from_string(version1) == version2)

    def test_equal_with_semantic_version(self):
        versions = [
            ("1.0.0", "1.0.0"),
            ("1.0.0.dev1", "1.0.0-dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-a1", "1.0.0-alpha1"),
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1-dev1"),
            ("1.0.0a1.dev1", "1.0.0-alpha1-dev1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-b1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0a1", "1.0.0-alpha1"),
            ("1.0.0b1", "1.0.0-beta1"),
            ("1.0.0rc1", "1.0.0-rc1"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0a1+dev1", "1.0.0-alpha1+dev1"),
            ("1.0.0b1+dev1", "1.0.0-beta1+dev1"),
            ("1.0.0rc1+dev1", "1.0.0-rc1+dev1"),
        ]
        for version1, version2 in versions:
            pep440 = Version.from_string(version1)
            semver = SemanticVersion.from_string(version2)
            self.assertTrue(
                pep440 == semver,
                f"{pep440!r} {version1} does not equal {semver!r} {version2}",
            )

        versions = []
        for version1, version2 in versions:
            pep440 = Version.from_string(version1)
            semver = SemanticVersion.from_string(version2)
            self.assertFalse(
                pep440 == semver,
                f"{pep440!r} {version1} equals {semver!r} {version2}",
            )

    def test_not_equal(self):
        versions = [
            ("1.0.0", "1.0.0"),
            ("1.0.0.dev1", "1.0.0.dev1"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev1"),
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
            ("1.0.0", "1.0.0.dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0.dev1", "1.0.0.dev2"),
            ("1.0.0+dev1", "1.0.0+dev2"),
            ("1.0.0-alpha1", "1.0.0-beta1"),
            ("1.0.0-alpha1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1.dev1"),
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev2"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1", "1.0.0-beta1.dev1"),
            ("1.0.0-beta1.dev1", "1.0.0-beta1.dev2"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1", "1.0.0-rc1.dev1"),
            ("1.0.0-rc1.dev1", "1.0.0-rc1.dev2"),
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
            ("1.0.0", "1.0.0.dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0", "1.0.0-rc1"),
            ("1.0.0-alpha1", "1.0.0-dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1.dev1"),
            ("1.0.0-alpha2", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-dev1"),
            ("1.0.0-beta1", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-beta1.dev1"),
            ("1.0.0-beta2", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-dev1"),
            ("1.0.0-rc1", "1.0.0-alpha1"),
            ("1.0.0-rc1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1.dev1"),
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
            ("1.0.0.dev1", "1.0.0.dev1"),
            ("1.0.0.dev1", "1.0.0.dev2"),
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
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev1"),
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev2"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-rc1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1.dev1", "1.0.0-beta1.dev1"),
            ("1.0.0-beta1.dev1", "1.0.0-beta1.dev2"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1.dev1", "1.0.0-rc1.dev1"),
            ("1.0.0-rc1.dev1", "1.0.0-rc1.dev2"),
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
            ("1.0.1", "1.0.0"),
            ("1.0.0", "1.0.0"),
            ("1.0.0", "1.0.0.dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0", "1.0.0-rc1"),
            ("1.0.0.dev1", "1.0.0.dev1"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0-alpha1", "1.0.0-dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1.dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-alpha2", "1.0.0-alpha1"),
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev1"),
            ("1.0.0-beta1", "1.0.0-dev1"),
            ("1.0.0-beta1", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-beta1", "1.0.0-beta1.dev1"),
            ("1.0.0-beta2", "1.0.0-beta1"),
            ("1.0.0-beta1.dev1", "1.0.0-beta1.dev1"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0-rc1", "1.0.0-dev1"),
            ("1.0.0-rc1", "1.0.0-alpha1"),
            ("1.0.0-rc1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1.dev1"),
            ("1.0.0-rc1.dev1", "1.0.0-rc1.dev1"),
            ("1.0.0-rc2", "1.0.0-rc1"),
        ]
        for version1, version2 in versions:
            self.assertTrue(
                Version.from_string(version1) >= Version.from_string(version2),
                f"{version1} should be greater or equal then {version2}",
            )

        versions = [
            ("1.0.0", "1.0.0+dev1"),
            ("1.0.0.dev1", "1.0.0.dev2"),
            ("1.0.0", "1.0.1"),
            ("1.0.0-dev1", "1.0.0"),
            ("1.0.0-dev1", "1.0.0-alpha1"),
            ("1.0.0-dev1", "1.0.0-beta1"),
            ("1.0.0-dev1", "1.0.0-rc1"),
            ("1.0.0+dev1", "1.0.0+dev2"),
            ("1.0.0-alpha1", "1.0.0-beta1"),
            ("1.0.0-alpha1", "1.0.0-rc1"),
            ("1.0.0-alpha1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev2"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-rc1"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1.dev1", "1.0.0-beta1.dev2"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1.dev1", "1.0.0-rc1.dev2"),
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
            ("1.0.0", "1.0.0.dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0", "1.0.0-rc1"),
            ("1.0.0-alpha1", "1.0.0-dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1.dev1"),
            ("1.0.0-alpha2", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-dev1"),
            ("1.0.0-beta1", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-beta1.dev1"),
            ("1.0.0-beta2", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-dev1"),
            ("1.0.0-rc1", "1.0.0-alpha1"),
            ("1.0.0-rc1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1.dev1"),
            ("1.0.0-rc2", "1.0.0-rc1"),
        ]
        for version2, version1 in versions:
            self.assertTrue(
                Version.from_string(version1) < Version.from_string(version2),
                f"{version1} should be less then {version2}",
            )

        versions = [
            ("1.0.0", "1.0.0"),
            ("1.0.0", "1.0.0+dev1"),
            ("1.0.0.dev1", "1.0.0.dev1"),
            ("1.0.0.dev1", "1.0.0.dev2"),
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
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev1"),
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev2"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-rc1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1.dev1", "1.0.0-beta1.dev1"),
            ("1.0.0-beta1.dev1", "1.0.0-beta1.dev2"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1.dev1", "1.0.0-rc1.dev1"),
            ("1.0.0-rc1.dev1", "1.0.0-rc1.dev2"),
            ("1.0.0-rc1+dev1", "1.0.0-rc1+dev2"),
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
            ("1.0.1", "1.0.0"),
            ("1.0.0", "1.0.0"),
            ("1.0.0", "1.0.0.dev1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-alpha1"),
            ("1.0.0", "1.0.0-beta1"),
            ("1.0.0", "1.0.0-rc1"),
            ("1.0.0.dev1", "1.0.0.dev1"),
            ("1.0.0+dev1", "1.0.0+dev1"),
            ("1.0.0-alpha1", "1.0.0-dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1.dev1"),
            ("1.0.0-alpha1", "1.0.0-alpha1"),
            ("1.0.0-alpha2", "1.0.0-alpha1"),
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev1"),
            ("1.0.0-beta1", "1.0.0-dev1"),
            ("1.0.0-beta1", "1.0.0-alpha1"),
            ("1.0.0-beta1", "1.0.0-beta1"),
            ("1.0.0-beta1", "1.0.0-beta1.dev1"),
            ("1.0.0-beta2", "1.0.0-beta1"),
            ("1.0.0-beta1.dev1", "1.0.0-beta1.dev1"),
            ("1.0.0-rc1", "1.0.0-rc1"),
            ("1.0.0-rc1", "1.0.0-dev1"),
            ("1.0.0-rc1", "1.0.0-alpha1"),
            ("1.0.0-rc1", "1.0.0-beta1"),
            ("1.0.0-rc1", "1.0.0-rc1.dev1"),
            ("1.0.0-rc1.dev1", "1.0.0-rc1.dev1"),
            ("1.0.0-rc2", "1.0.0-rc1"),
        ]
        for version2, version1 in versions:
            self.assertTrue(
                Version.from_string(version1) <= Version.from_string(version2),
                f"{version1} should be less or equal then {version2}",
            )

        versions = [
            ("1.0.0", "1.0.0+dev1"),
            ("1.0.0.dev1", "1.0.0.dev2"),
            ("1.0.0", "1.0.1"),
            ("1.0.0-dev1", "1.0.0"),
            ("1.0.0-dev1", "1.0.0-alpha1"),
            ("1.0.0-dev1", "1.0.0-beta1"),
            ("1.0.0-dev1", "1.0.0-rc1"),
            ("1.0.0+dev1", "1.0.0+dev2"),
            ("1.0.0-alpha1", "1.0.0-beta1"),
            ("1.0.0-alpha1", "1.0.0-rc1"),
            ("1.0.0-alpha1", "1.0.0-alpha1+dev1"),
            ("1.0.0-alpha1.dev1", "1.0.0-alpha1.dev2"),
            ("1.0.0-alpha1+dev1", "1.0.0-alpha1+dev2"),
            ("1.0.0-beta1", "1.0.0-rc1"),
            ("1.0.0-beta1", "1.0.0-beta1+dev1"),
            ("1.0.0-beta1.dev1", "1.0.0-beta1.dev2"),
            ("1.0.0-beta1+dev1", "1.0.0-beta1+dev2"),
            ("1.0.0-rc1", "1.0.0"),
            ("1.0.0-rc1", "1.0.0-rc1+dev1"),
            ("1.0.0-rc1.dev1", "1.0.0-rc1.dev2"),
            ("1.0.0-rc1+dev1", "1.0.0-rc1+dev2"),
        ]
        for version2, version1 in versions:
            self.assertFalse(
                Version.from_string(version1) <= Version.from_string(version2),
                f"{version1} should not be less or equal then {version2}",
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
            "1.0.0.dev1",
            "1.0.0dev1",
            "1.0.0-alpha1.dev1",
            "1.0.0-beta1.dev1",
            "1.0.0-rc1.dev1",
        ]
        for version in versions:
            self.assertTrue(
                Version.from_string(version).is_dev_release,
                f"{version} is not a dev release",
            )

        versions = [
            "1.0.0",
            "1.0.0+dev1",
            "1.0.0a1",
            "1.0.0b1",
            "1.0.0rc1",
            "1.0.0-alpha1",
            "1.0.0-beta1",
            "1.0.0-rc1",
            "1.0.0a1+dev1",
            "1.0.0b1+dev1",
            "1.0.0rc1+dev1",
        ]
        for version in versions:
            self.assertFalse(
                Version.from_string(version).is_dev_release,
                f"{version} is a dev release",
            )

    def test_is_alpha_release(self):
        versions = [
            "1.0.0-alpha1",
            "1.0.0-a1",
            "1.0.0a1",
            "1.0.0a1+foo",
            "1.0.0a1.dev1",
        ]
        for version in versions:
            self.assertTrue(
                Version.from_string(version).is_alpha_release,
                f"{version} is not an alpha release",
            )

        versions = [
            "1.0.0",
            "1.0.0.dev1",
            "1.0.0b1",
            "1.0.0rc1",
        ]
        for version in versions:
            self.assertFalse(
                Version.from_string(version).is_alpha_release,
                f"{version} is an alpha release",
            )

    def test_is_beta_release(self):
        versions = [
            "1.0.0-beta1",
            "1.0.0-b1",
            "1.0.0b1",
            "1.0.0b1+foo",
            "1.0.0b1.dev1",
        ]
        for version in versions:
            self.assertTrue(
                Version.from_string(version).is_beta_release,
                f"{version} is not a beta release",
            )

        versions = [
            "1.0.0",
            "1.0.0.dev1",
            "1.0.0a1",
            "1.0.0rc1",
        ]
        for version in versions:
            self.assertFalse(
                Version.from_string(version).is_beta_release,
                f"{version} is a beta release",
            )

    def test_is_release_candidate(self):
        versions = [
            "1.0.0-rc1",
            "1.0.0rc1",
            "1.0.0rc1+foo",
            "1.0.0rc1.dev1",
        ]
        for version in versions:
            self.assertTrue(
                Version.from_string(version).is_release_candidate,
                f"{version} is not a release candidate",
            )

        versions = [
            "1.0.0",
            "1.0.0.dev1",
            "1.0.0a1",
            "1.0.0b1",
        ]
        for version in versions:
            self.assertFalse(
                Version.from_string(version).is_release_candidate,
                f"{version} is a release candidate",
            )

    def test_pre(self):
        versions = [
            ("1.0.0", None),
            ("1.0.0.dev1", None),
            ("1.0.0-dev1", None),
            ("1.0.0a1", ("alpha", 1)),
            ("1.0.0-alpha1", ("alpha", 1)),
            ("1.0.0b1", ("beta", 1)),
            ("1.0.0-beta1", ("beta", 1)),
            ("1.0.0rc1", ("rc", 1)),
            ("1.0.0-rc1", ("rc", 1)),
            ("1.0.0rc1+foo1", ("rc", 1)),
            ("1.0.0a1.dev1", ("alpha", 1)),
            ("1.0.0a1.dev1", ("alpha", 1)),
            ("1.0.0b1.dev1", ("beta", 1)),
            ("1.0.0rc1.dev1", ("rc", 1)),
        ]

        for version, expected in versions:
            self.assertEqual(Version.from_string(version).pre, expected)

    def test_local(self):
        versions = [
            ("1.0.0", None),
            ("1.0.0+dev1", ("dev", 1)),
            ("1.0.0-dev1", None),
            ("1.0.0.dev1", None),
            ("1.0.0a1", None),
            ("1.0.0-alpha1", None),
            ("1.0.0b1", None),
            ("1.0.0-beta1", None),
            ("1.0.0rc1", None),
            ("1.0.0-rc1", None),
            ("1.0.0rc1+foo1", ("foo", 1)),
            ("1.0.0rc1+dev1", ("dev", 1)),
            ("1.0.01.dev1", None),
            ("1.0.0b1.dev1", None),
            ("1.0.0rc1.dev1", None),
        ]

        for version, expected in versions:
            version_local = Version.from_string(version).local
            self.assertEqual(
                version_local,
                expected,
                f"{version_local} does not match {expected} for version "
                f"{version}",
            )


class PEP440VersionCalculatorTestCase(unittest.TestCase):
    def test_next_patch_version(self):
        calculator = VersionCalculator()

        versions = [
            ("0.0.1", "0.0.2"),
            ("1.2.3", "1.2.4"),
            ("1.2.3.post1", "1.2.4"),
            ("1.2.3a1", "1.2.3"),
            ("1.2.3b1", "1.2.3"),
            ("1.2.3rc1", "1.2.3"),
            ("1.2.3a1.dev1", "1.2.3"),
            ("1.2.3b1.dev1", "1.2.3"),
            ("1.2.3rc1.dev1", "1.2.3"),
            ("22.4.1", "22.4.2"),
            ("22.4.1.dev1", "22.4.1"),
            ("22.4.1.dev3", "22.4.1"),
            ("2022.4.1.dev3", "2022.4.1"),
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
            "21.4.1.dev3",
            f"19.{today.month}.1.dev3",
            f"{year_short}.{today.month}.1.dev3",
            f"{year_short}.{today.month}.1",
            "2022.4.1",
            "2023.5.1",
            f"{today.year}.{today.month}.1.dev2",
            f"{today.year}.{today.month}.1",
        ]
        assert_versions = [
            f"{year_short}.{today.month}.0",
            f"{year_short}.{today.month}.0",
            f"{year_short}.{today.month}.1",
            f"{year_short}.{today.month}.2",
            f"{today.year}.{today.month}.0",
            f"{today.year}.{today.month}.0",
            f"{today.year}.{today.month}.1",
            f"{today.year}.{today.month}.2",
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

        with self.assertRaisesRegex(VersionError, "'.+' is higher than '.+'."):
            calculator.next_calendar_version(
                Version.from_string(f"{today.year + 1}.{today.month + 1}.0")
            )

    def test_next_minor_version(self):
        calculator = VersionCalculator()

        versions = [
            ("0.0.1", "0.1.0"),
            ("1.2.3", "1.3.0"),
            ("1.2.3.post1", "1.3.0"),
            ("1.2.3a1", "1.3.0"),
            ("1.2.3b1", "1.3.0"),
            ("1.2.3rc1", "1.3.0"),
            ("1.2.3a1.dev1", "1.3.0"),
            ("1.2.3b1.dev1", "1.3.0"),
            ("1.2.3rc1.dev1", "1.3.0"),
            ("22.4.1", "22.5.0"),
            ("22.4.1.dev1", "22.5.0"),
            ("22.4.1.dev3", "22.5.0"),
            ("1.0.0a1", "1.0.0"),
            ("1.1.0a1", "1.1.0"),
            ("1.0.0.dev1", "1.0.0"),
            ("1.1.0.dev1", "1.1.0"),
            ("2022.1.0.dev1", "2022.1.0"),
        ]

        for current_version, assert_version in versions:
            release_version = calculator.next_minor_version(
                Version.from_string(current_version),
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
            ("1.2.3.post1", "2.0.0"),
            ("1.2.3a1", "2.0.0"),
            ("1.2.3b1", "2.0.0"),
            ("1.2.3rc1", "2.0.0"),
            ("1.2.3a1.dev1", "2.0.0"),
            ("1.2.3b1.dev1", "2.0.0"),
            ("1.2.3rc1.dev1", "2.0.0"),
            ("22.4.1", "23.0.0"),
            ("22.4.1.dev1", "23.0.0"),
            ("22.4.1.dev3", "23.0.0"),
            ("1.0.0a1", "1.0.0"),
            ("1.1.0a1", "2.0.0"),
            ("1.0.0.dev1", "1.0.0"),
            ("1.1.0.dev1", "2.0.0"),
        ]
        for current_version, assert_version in versions:
            release_version = calculator.next_major_version(
                Version.from_string(current_version),
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
            ("0.0.1", "0.0.2a1"),
            ("1.2.3", "1.2.4a1"),
            ("1.2.3.post1", "1.2.4a1"),
            ("1.2.3a1", "1.2.3a2"),
            ("1.2.3b1", "1.2.4a1"),
            ("1.2.3rc1", "1.2.4a1"),
            ("1.2.3a1.dev1", "1.2.3a1"),
            ("1.2.3b1.dev1", "1.2.4a1"),
            ("1.2.3rc1.dev1", "1.2.4a1"),
            ("22.4.1", "22.4.2a1"),
            ("22.4.1.dev1", "22.4.1a1"),
            ("22.4.1.dev3", "22.4.1a1"),
            ("1.0.0a1", "1.0.0a2"),
            ("1.1.0a1", "1.1.0a2"),
            ("1.0.0.dev1", "1.0.0a1"),
            ("1.1.0.dev1", "1.1.0a1"),
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
            ("0.0.1", "0.0.2b1"),
            ("1.2.3", "1.2.4b1"),
            ("1.2.3.post1", "1.2.4b1"),
            ("1.2.3a1", "1.2.3b1"),
            ("1.2.3b1", "1.2.3b2"),
            ("1.2.3rc1", "1.2.4b1"),
            ("1.2.3a1.dev1", "1.2.3b1"),
            ("1.2.3b1.dev1", "1.2.3b1"),
            ("1.2.3rc1.dev1", "1.2.4b1"),
            ("22.4.1", "22.4.2b1"),
            ("22.4.1.dev1", "22.4.1b1"),
            ("22.4.1.dev3", "22.4.1b1"),
            ("1.0.0a1", "1.0.0b1"),
            ("1.1.0a1", "1.1.0b1"),
            ("1.0.0.dev1", "1.0.0b1"),
            ("1.1.0.dev1", "1.1.0b1"),
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
            ("0.0.1", "0.0.2rc1"),
            ("1.2.3", "1.2.4rc1"),
            ("1.2.3.post1", "1.2.4rc1"),
            ("1.2.3a1", "1.2.3rc1"),
            ("1.2.3b1", "1.2.3rc1"),
            ("1.2.3rc1", "1.2.3rc2"),
            ("1.2.3a1.dev1", "1.2.3rc1"),
            ("1.2.3b1.dev1", "1.2.3rc1"),
            ("1.2.3rc1.dev1", "1.2.3rc1"),
            ("22.4.1", "22.4.2rc1"),
            ("22.4.1.dev1", "22.4.1rc1"),
            ("22.4.1.dev3", "22.4.1rc1"),
            ("1.0.0a1", "1.0.0rc1"),
            ("1.1.0a1", "1.1.0rc1"),
            ("1.0.0.dev1", "1.0.0rc1"),
            ("1.1.0.dev1", "1.1.0rc1"),
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
            ("0.0.1", "0.0.2.dev1"),
            ("1.2.3", "1.2.4.dev1"),
            ("1.2.3.dev1", "1.2.3.dev2"),
            ("1.2.3.post1", "1.2.4.dev1"),
            ("1.2.3a1", "1.2.3a2.dev1"),
            ("1.2.3b1", "1.2.3b2.dev1"),
            ("1.2.3rc1", "1.2.3rc2.dev1"),
            ("1.2.3a1.dev1", "1.2.3a1.dev2"),
            ("1.2.3b1.dev1", "1.2.3b1.dev2"),
            ("1.2.3rc1.dev1", "1.2.3rc1.dev2"),
            ("22.4.1", "22.4.2.dev1"),
            ("22.4.1.dev1", "22.4.1.dev2"),
            ("22.4.1.dev3", "22.4.1.dev4"),
            ("1.0.0a1", "1.0.0a2.dev1"),
            ("1.1.0a1", "1.1.0a2.dev1"),
            ("1.0.0.dev1", "1.0.0.dev2"),
            ("1.1.0.dev1", "1.1.0.dev2"),
        ]

        for current_version, assert_version in versions:
            release_version = calculator.next_dev_version(
                Version.from_string(current_version)
            )
            self.assertEqual(
                release_version,
                Version.from_string(assert_version),
                f"{release_version} is not the next expected dev version "
                f"{assert_version} for {current_version}",
            )
