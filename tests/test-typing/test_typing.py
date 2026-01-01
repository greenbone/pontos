# SPDX-FileCopyrightText: 2023-2026 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest

from pontos.typing import SupportsStr


class SupportsStrTestCase(unittest.TestCase):
    def test_str(self):
        self.assertIsInstance("", SupportsStr)
        self.assertIsInstance(None, SupportsStr)

    def test_some_class(self):
        class Foo:
            def __str__(self) -> str:
                pass

        foo = Foo()

        self.assertIsInstance(foo, SupportsStr)
