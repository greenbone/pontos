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

from argparse import Namespace
from pathlib import Path
import unittest
from unittest.mock import Mock

from pontos.github.argparser import parse_args
from pontos.github.cmds import pull_request


class TestArgparsing(unittest.TestCase):
    def setUp(self):
        self.term = Mock()

    def test_parse_args(self):
        argv = [
            "pr",
            "foo/bar",
            "baz",
            "main",
            "baz in main",
        ]

        parsed_args = parse_args(argv)

        template = Path().cwd() / 'pontos/github/pr_template.md'

        expected_args = Namespace(
            body=template.read_text(encoding='utf-8'),
            command='pr',
            func=pull_request,
            head='baz',
            repo='foo/bar',
            target='main',
            title='baz in main',
            token='GITHUB_TOKEN',
        )

        self.assertEqual(parsed_args, expected_args)

    def test_parse_args_fail(self):
        argv = ["pr", "foo/bar"]

        with self.assertRaises(SystemExit):
            parse_args(argv)
