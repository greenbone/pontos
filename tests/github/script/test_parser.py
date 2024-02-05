# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest
from unittest.mock import patch

from pontos.github.api.helper import DEFAULT_TIMEOUT
from pontos.github.script._parser import create_parser


class CreateParserTestCase(unittest.TestCase):
    def test_create_parser(self):
        parser = create_parser()
        args = parser.parse_args(
            ["--token", "123", "--timeout", "456", "my_script"]
        )

        self.assertEqual(args.token, "123")
        self.assertEqual(args.timeout, 456)
        self.assertEqual(args.script, "my_script")

    @patch.dict("os.environ", {"GITHUB_TOKEN": "987"})
    def test_parse_token(self):
        parser = create_parser()
        args = parser.parse_args(["my_script"])
        self.assertEqual(args.token, "987")
        self.assertEqual(args.script, "my_script")

        args = parser.parse_args(["--token", "123", "my_script"])

        self.assertEqual(args.token, "123")
        self.assertEqual(args.script, "my_script")

    def test_parse_timeout(self):
        parser = create_parser()
        args = parser.parse_args(["my_script"])
        self.assertEqual(args.script, "my_script")
        self.assertEqual(args.timeout, DEFAULT_TIMEOUT)

        args = parser.parse_args(["--timeout", "666", "my_script"])

        self.assertEqual(args.timeout, 666)
        self.assertEqual(args.script, "my_script")
