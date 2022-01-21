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

from argparse import Namespace
from pathlib import Path
import unittest
from dataclasses import dataclass
from datetime import datetime

from pontos.terminal import _set_terminal
from pontos.terminal.terminal import Terminal

from pontos import changelog


@dataclass
class StdOutput:
    stdout: bytes


class ConventionalCommitsTestCase(unittest.TestCase):
    def test_changelog_builder(self):

        _set_terminal(Terminal())

        today = datetime.today().strftime('%Y-%m-%d')

        own_path = Path(__file__).absolute().parent
        print(own_path)
        config_toml = own_path / 'changelog.toml'
        release_version = '0.0.2'
        output = f'v{release_version}.md'
        git_log = (
            '1234567 Add: foo bar\n'
            '8abcdef Add: bar baz\n'
            '8abcd3f Add bar baz\n'
            '8abcd3d Adding bar baz\n'
            '1337abc Change: bar to baz\n'
            '42a42a4 Remove: foo bar again\n'
            'fedcba8 Test: bar baz testing\n'
            'dead901 Refactor: bar baz ref\n'
            'fedcba8 Fix: bar baz fixing\n'
            'd0c4d0c Doc: bar baz documenting\n'
        )
        called = []

        def runner(cmd):
            called.append(cmd)
            return StdOutput(git_log)

        cargs = Namespace(
            current_version='0.0.1',
            next_version=release_version,
            output=output,
            space='foo',
            project='bar',
            config=config_toml,
        )
        changelog_builder = changelog.ChangelogBuilder(
            shell_cmd_runner=runner,
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
        print(output_file.read_text(encoding='utf-8'))
        self.assertEqual(
            output_file.read_text(encoding='utf-8'), expected_output
        )

        self.assertIn(
            'git log "$(git describe --tags --abbrev=0)..HEAD" --oneline',
            called,
        )

        output_file.unlink()

    def test_changelog_builder_no_commits(self):

        _set_terminal(Terminal())

        own_path = Path(__file__).absolute().parent
        print(own_path)
        config_toml = own_path / 'changelog.toml'
        release_version = '0.0.2'
        output = f'v{release_version}.md'
        git_log = '1234567 foo bar\n8abcdef bar baz\n'
        called = []

        def runner(cmd):
            called.append(cmd)
            return StdOutput(git_log)

        cargs = Namespace(
            current_version='0.0.1',
            next_version=release_version,
            output=output,
            space='foo',
            project='bar',
            config=config_toml,
        )
        changelog_builder = changelog.ChangelogBuilder(
            shell_cmd_runner=runner,
            args=cargs,
        )

        with self.assertRaises(SystemExit):
            output_file = changelog_builder.create_changelog_file()

            self.assertIsNone(output_file)
            self.assertIn(
                'git log "$(git describe --tags --abbrev=0)..HEAD" --oneline',
                called,
            )

    def test_changelog_builder_no_conventional_commits(self):

        _set_terminal(Terminal())

        own_path = Path(__file__).absolute().parent
        config_toml = own_path / 'changelog.toml'
        release_version = '0.0.2'
        output = f'v{release_version}.md'
        git_log = None
        called = []

        def runner(cmd):
            called.append(cmd)
            return StdOutput(git_log)

        cargs = Namespace(
            current_version='0.0.1',
            next_version=release_version,
            output=output,
            space='foo',
            project='bar',
            config=config_toml,
        )
        changelog_builder = changelog.ChangelogBuilder(
            shell_cmd_runner=runner,
            args=cargs,
        )

        with self.assertRaises(SystemExit):
            output_file = changelog_builder.create_changelog_file()

            self.assertIsNone(output_file)
            self.assertIn(
                'git log "$(git describe --tags --abbrev=0)..HEAD" --oneline',
                called,
            )
