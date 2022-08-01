# Copyright (C) 2020-2022 Greenbone Networks GmbH
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

from pontos.version.helper import (
    VersionError,
    is_version_pep440_compliant,
    safe_version,
    strip_version,
)


class IsVersionPep440CompliantTestCase(unittest.TestCase):
    def test_is_compliant(self):
        self.assertTrue(is_version_pep440_compliant("1.2.3.dev1"))
        self.assertTrue(is_version_pep440_compliant("1.2.3.dev0"))
        self.assertTrue(is_version_pep440_compliant("20.4"))
        self.assertTrue(is_version_pep440_compliant("1.2"))
        self.assertTrue(is_version_pep440_compliant("1.2.0a0"))
        self.assertTrue(is_version_pep440_compliant("1.2.0a1"))
        self.assertTrue(is_version_pep440_compliant("1.2.0b0"))
        self.assertTrue(is_version_pep440_compliant("1.2.0b1"))

    def test_is_not_compliant(self):
        self.assertFalse(is_version_pep440_compliant("1.2.3dev1"))
        self.assertFalse(is_version_pep440_compliant("1.2.3dev"))
        self.assertFalse(is_version_pep440_compliant("1.2.3dev0"))
        self.assertFalse(is_version_pep440_compliant("1.2.3alpha"))
        self.assertFalse(is_version_pep440_compliant("1.2.3alpha0"))
        self.assertFalse(is_version_pep440_compliant("1.2.3.a0"))
        self.assertFalse(is_version_pep440_compliant("1.2.3beta"))
        self.assertFalse(is_version_pep440_compliant("1.2.3beta0"))
        self.assertFalse(is_version_pep440_compliant("1.2.3.b0"))
        self.assertFalse(is_version_pep440_compliant("20.04"))


class SafeVersionTestCase(unittest.TestCase):
    def test_dev_versions(self):
        self.assertEqual(safe_version("1.2.3dev"), "1.2.3.dev0")
        self.assertEqual(safe_version("1.2.3dev1"), "1.2.3.dev1")
        self.assertEqual(safe_version("1.2.3.dev"), "1.2.3.dev0")

    def test_alpha_versions(self):
        self.assertEqual(safe_version("1.2.3alpha"), "1.2.3a0")
        self.assertEqual(safe_version("1.2.3.alpha"), "1.2.3a0")
        self.assertEqual(safe_version("1.2.3a"), "1.2.3a0")
        self.assertEqual(safe_version("1.2.3.a1"), "1.2.3a1")
        self.assertEqual(safe_version("1.2.3a1"), "1.2.3a1")

    def test_beta_versions(self):
        self.assertEqual(safe_version("1.2.3beta"), "1.2.3b0")
        self.assertEqual(safe_version("1.2.3.beta"), "1.2.3b0")
        self.assertEqual(safe_version("1.2.3b"), "1.2.3b0")
        self.assertEqual(safe_version("1.2.3.b1"), "1.2.3b1")
        self.assertEqual(safe_version("1.2.3b1"), "1.2.3b1")

    def test_caldav_versions(self):
        self.assertEqual(safe_version("22.04"), "22.4")
        self.assertEqual(safe_version("22.4"), "22.4")
        self.assertEqual(safe_version("22.10"), "22.10")
        self.assertEqual(safe_version("22.04dev1"), "22.4.dev1")
        self.assertEqual(safe_version("22.10dev1"), "22.10.dev1")

    def test_release_versions(self):
        self.assertEqual(safe_version("1"), "1")
        self.assertEqual(safe_version("1.2"), "1.2")
        self.assertEqual(safe_version("1.2.3"), "1.2.3")
        self.assertEqual(safe_version("22.4"), "22.4")


class StripVersionTestCase(unittest.TestCase):
    def test_version_string_without_v(self):
        self.assertEqual(strip_version("1.2.3"), "1.2.3")
        self.assertEqual(strip_version("1.2.3dev"), "1.2.3dev")

    def test_version_string_with_v(self):
        self.assertEqual(strip_version("v1.2.3"), "1.2.3")
        self.assertEqual(strip_version("v1.2.3dev"), "1.2.3dev")


class VersionErrorTestCase(unittest.TestCase):
    def test_should_print_message(self):
        err = VersionError("foo bar")
        self.assertEqual(str(err), "foo bar")

    def test_should_raise(self):
        with self.assertRaisesRegex(VersionError, "^foo bar$"):
            raise VersionError("foo bar")
