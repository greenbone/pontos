# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Greenbone Networks GmbH
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
from argparse import Namespace
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock, call, patch

from pontos import changelog
from pontos.changelog.conventional_commits import parse_args


@dataclass
class StdOutput:
    stdout: bytes


class ConventionalCommitsTestCase(unittest.TestCase):
    @patch("pontos.changelog.conventional_commits.shell_cmd_runner")
    def test_changelog_builder(self, shell_mock):
        terminal = MagicMock()

        today = datetime.today().strftime("%Y-%m-%d")

        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"
        release_version = "0.0.2"
        output = f"v{release_version}.md"

        shell_mock.side_effect = [
            CompletedProcess(args=None, returncode=1, stdout="v0.0.1"),
            CompletedProcess(
                args=None,
                returncode=1,
                stdout=(
                    "1234567 Add: foo bar\n"
                    "8abcdef Add: bar baz\n"
                    "8abcd3f Add bar baz\n"
                    "8abcd3d Adding bar baz\n"
                    "1337abc Change: bar to baz\n"
                    "42a42a4 Remove: foo bar again\n"
                    "fedcba8 Test: bar baz testing\n"
                    "dead901 Refactor: bar baz ref\n"
                    "fedcba8 Fix: bar baz fixing\n"
                    "d0c4d0c Doc: bar baz documenting\n"
                ),
            ),
        ]

        cargs = Namespace(
            current_version="0.0.1",
            next_version=release_version,
            output=output,
            space="foo",
            project="bar",
            config=config_toml,
        )
        changelog_builder = changelog.ChangelogBuilder(
            terminal=terminal,
            args=cargs,
        )
        expected_output = f"""# Changelog

All notable changes to this project will be documented in this file.

## [0.0.2] - {today}

## Added
* foo bar [1234567](https://github.com/foo/bar/commit/1234567)
* bar baz [8abcdef](https://github.com/foo/bar/commit/8abcdef)

## Removed
* foo bar again [42a42a4](https://github.com/foo/bar/commit/42a42a4)

## Changed
* bar to baz [1337abc](https://github.com/foo/bar/commit/1337abc)

## Bug Fixes
* bar baz fixing [fedcba8](https://github.com/foo/bar/commit/fedcba8)

## Documentation
* bar baz documenting [d0c4d0c](https://github.com/foo/bar/commit/d0c4d0c)

## Refactor
* bar baz ref [dead901](https://github.com/foo/bar/commit/dead901)

## Testing
* bar baz testing [fedcba8](https://github.com/foo/bar/commit/fedcba8)

[0.0.2]: https://github.com/foo/bar/compare/0.0.1...0.0.2"""
        output_file = changelog_builder.create_changelog_file()
        self.assertEqual(
            output_file.read_text(encoding="utf-8"), expected_output
        )

        shell_mock.assert_has_calls(
            [
                call("git tag | sort -V | tail -1"),
                call('git log "v0.0.1..HEAD" --oneline'),
            ]
        )

        output_file.unlink()

    @patch("pontos.changelog.conventional_commits.shell_cmd_runner")
    def test_changelog_builder_no_commits(self, shell_mock):
        terminal = MagicMock()

        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"
        release_version = "0.0.2"
        output = f"v{release_version}.md"

        shell_mock.return_value = CompletedProcess(
            args=None, returncode=1, stdout="1234567 foo bar\n8abcdef bar baz\n"
        )

        cargs = Namespace(
            current_version="0.0.1",
            next_version=release_version,
            output=output,
            space="foo",
            project="bar",
            config=config_toml,
        )
        changelog_builder = changelog.ChangelogBuilder(
            terminal=terminal,
            args=cargs,
        )

        with self.assertRaises(SystemExit):
            output_file = changelog_builder.create_changelog_file()

            self.assertIsNone(output_file)
            shell_mock.assert_called_with(
                'git log "$(git describe --tags --abbrev=0)..HEAD" --oneline',
            )

    @patch("pontos.changelog.conventional_commits.shell_cmd_runner")
    def test_changelog_builder_no_tag(self, shell_mock):
        terminal = MagicMock()

        today = datetime.today().strftime("%Y-%m-%d")

        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"
        release_version = "0.0.2"
        output = f"v{release_version}.md"
        shell_mock.side_effect = [
            CompletedProcess(args=None, returncode=1, stdout=""),
            CompletedProcess(
                args=None,
                returncode=1,
                stdout=(
                    "1234567 Add: foo bar\n"
                    "8abcdef Add: bar baz\n"
                    "8abcd3f Add bar baz\n"
                    "8abcd3d Adding bar baz\n"
                    "1337abc Change: bar to baz\n"
                    "42a42a4 Remove: foo bar again\n"
                    "fedcba8 Test: bar baz testing\n"
                    "dead901 Refactor: bar baz ref\n"
                    "fedcba8 Fix: bar baz fixing\n"
                    "d0c4d0c Doc: bar baz documenting\n"
                ),
            ),
        ]

        cargs = Namespace(
            current_version="0.0.1",
            next_version=release_version,
            output=output,
            space="foo",
            project="bar",
            config=config_toml,
        )
        changelog_builder = changelog.ChangelogBuilder(
            terminal=terminal,
            args=cargs,
        )
        expected_output = f"""# Changelog

All notable changes to this project will be documented in this file.

## [0.0.2] - {today}

## Added
* foo bar [1234567](https://github.com/foo/bar/commit/1234567)
* bar baz [8abcdef](https://github.com/foo/bar/commit/8abcdef)

## Removed
* foo bar again [42a42a4](https://github.com/foo/bar/commit/42a42a4)

## Changed
* bar to baz [1337abc](https://github.com/foo/bar/commit/1337abc)

## Bug Fixes
* bar baz fixing [fedcba8](https://github.com/foo/bar/commit/fedcba8)

## Documentation
* bar baz documenting [d0c4d0c](https://github.com/foo/bar/commit/d0c4d0c)

## Refactor
* bar baz ref [dead901](https://github.com/foo/bar/commit/dead901)

## Testing
* bar baz testing [fedcba8](https://github.com/foo/bar/commit/fedcba8)

[0.0.2]: https://github.com/foo/bar/compare/0.0.1...0.0.2"""
        output_file = changelog_builder.create_changelog_file()
        self.assertEqual(
            output_file.read_text(encoding="utf-8"), expected_output
        )

        shell_mock.assert_has_calls(
            [
                call("git tag | sort -V | tail -1"),
                call("git log HEAD --oneline"),
            ]
        )

        output_file.unlink()

    @patch("pontos.changelog.conventional_commits.shell_cmd_runner")
    def test_changelog_builder_no_conventional_commits(self, shell_mock):
        terminal = MagicMock()

        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"
        release_version = "0.0.2"
        output = f"v{release_version}.md"
        shell_mock.return_value = CompletedProcess(
            args="foo", returncode=1, stdout=None
        )
        cargs = Namespace(
            current_version="0.0.1",
            next_version=release_version,
            output=output,
            space="foo",
            project="bar",
            config=config_toml,
        )
        changelog_builder = changelog.ChangelogBuilder(
            terminal=terminal,
            args=cargs,
        )

        with self.assertRaises(SystemExit):
            output_file = changelog_builder.create_changelog_file()

            self.assertIsNone(output_file)
            shell_mock.assert_called_with(
                'git log "$(git describe --tags --abbrev=0)..HEAD" --oneline',
            )

    def test_parse_args(self):
        parsed_args = parse_args(
            ["-q", "--log-file", "blah", "--project", "urghs"]
        )

        self.assertTrue(parsed_args.quiet)
        self.assertEqual(parsed_args.log_file, "blah")
        self.assertEqual(parsed_args.project, "urghs")
