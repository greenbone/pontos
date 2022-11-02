# Copyright (C) 2022 Greenbone Networks GmbH
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
from unittest.mock import patch

from pontos.github.api.helper import DEFAULT_TIMEOUT
from pontos.github.script.parser import create_parser


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
