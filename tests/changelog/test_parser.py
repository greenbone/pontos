# Copyright (C) 2021-2023 Greenbone Networks GmbH
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
from pathlib import Path

from pontos.changelog.main import parse_args


class ParseArgsTestCase(unittest.TestCase):
    def test_parse_args(self):
        parsed_args = parse_args(
            [
                "-q",
                "--project",
                "urghs",
                "--space",
                "bla",
                "--config",
                "foo.toml",
                "--current-version",
                "1.2.3",
                "--next-version",
                "2.3.4",
                "--git-tag-prefix",
                "a",
                "--output",
                "changelog.md",
            ]
        )

        self.assertTrue(parsed_args.quiet)
        self.assertEqual(parsed_args.project, "urghs")
        self.assertEqual(parsed_args.space, "bla")
        self.assertEqual(parsed_args.config, Path("foo.toml"))
        self.assertEqual(parsed_args.current_version, "1.2.3")
        self.assertEqual(parsed_args.next_version, "2.3.4")
        self.assertEqual(parsed_args.git_tag_prefix, "a")
        self.assertEqual(parsed_args.output, Path("changelog.md"))
