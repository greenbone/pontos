# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from pontos.models import StrEnum


class FooEnum(StrEnum):
    A = "a"
    B = "b"


class StrEnumTestCase(unittest.TestCase):
    def test_str(self):
        self.assertEqual(str(FooEnum.A), "a")
        self.assertEqual(str(FooEnum.B), "b")

    def test_str_append(self):
        self.assertEqual("say " + FooEnum.A, "say a")
        self.assertEqual("say " + FooEnum.B, "say b")

    def test_f_string(self):
        self.assertEqual(f"say {FooEnum.A}", "say a")
        self.assertEqual(f"say {FooEnum.B}", "say b")
