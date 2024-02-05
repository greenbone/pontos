# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest
from argparse import ArgumentTypeError

from pontos.enum import StrEnum, enum_type


class EnumTypeTestCase(unittest.TestCase):
    def test_enum_type(self):
        class FooEnum(StrEnum):
            ALL = "all"
            NONE = "none"

        func = enum_type(FooEnum)

        self.assertEqual(func("all"), FooEnum.ALL)
        self.assertEqual(func("none"), FooEnum.NONE)

        self.assertEqual(func(FooEnum.ALL), FooEnum.ALL)
        self.assertEqual(func(FooEnum.NONE), FooEnum.NONE)

    def test_enum_type_error(self):
        class FooEnum(StrEnum):
            ALL = "all"
            NONE = "none"

        func = enum_type(FooEnum)

        with self.assertRaisesRegex(
            ArgumentTypeError,
            r"invalid value foo. Expected one of all, none",
        ):
            func("foo")
