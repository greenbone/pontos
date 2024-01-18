# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import unittest

from pontos.version import VersionError


class VersionErrorTestCase(unittest.TestCase):
    def test_should_print_message(self):
        err = VersionError("foo bar")
        self.assertEqual(str(err), "foo bar")

    def test_should_raise(self):
        with self.assertRaisesRegex(VersionError, "^foo bar$"):
            raise VersionError("foo bar")
