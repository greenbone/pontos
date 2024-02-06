# Copyright (C) 2021-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
import unittest
from pathlib import Path

from pontos.changelog.main import parse_args
from pontos.version.schemes._pep440 import PEP440Version


class ParseArgsTestCase(unittest.TestCase):
    def test_parse_args(self):
        parsed_args = parse_args(
            [
                "-q",
                "--repository",
                "urghs/bla",
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
        self.assertEqual(parsed_args.repository, "urghs/bla")
        self.assertEqual(parsed_args.config, Path("foo.toml"))
        self.assertEqual(parsed_args.current_version, PEP440Version("1.2.3"))
        self.assertEqual(parsed_args.next_version, PEP440Version("2.3.4"))
        self.assertEqual(parsed_args.git_tag_prefix, "a")
        self.assertEqual(parsed_args.output, Path("changelog.md"))
