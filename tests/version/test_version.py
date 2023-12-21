# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest

from pontos.version.schemes._pep440 import PEP440Version
from pontos.version.schemes._semantic import SemanticVersion


class VersionTestCase(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(PEP440Version("22.2.2"), PEP440Version("22.2.2"))
        self.assertNotEqual(PEP440Version("22.2.1"), PEP440Version("22.2.2"))
        self.assertNotEqual(SemanticVersion("22.2.2"), "22.2.2")
        self.assertNotEqual(
            SemanticVersion("22.2.1"), SemanticVersion("22.2.2")
        )
        self.assertNotEqual(PEP440Version("22.2.2"), "22.2.2")

    def test_equal_other(self):
        self.assertEqual(PEP440Version("22.2.2"), SemanticVersion("22.2.2"))

    def test_equal_other_other_way_around(self):
        self.assertEqual(SemanticVersion("22.2.2"), PEP440Version("22.2.2"))

    def test_equal_raises(self):
        with self.assertRaises(ValueError):
            self.assertNotEqual(SemanticVersion("22.2.2"), 22)

        with self.assertRaises(ValueError):
            self.assertNotEqual(PEP440Version("22.2.2"), 22)
