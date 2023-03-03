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
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from pontos.changelog.conventional_commits import (
    ChangelogBuilder,
    ChangelogBuilderError,
)
from pontos.testing import temp_directory


@dataclass
class StdOutput:
    stdout: bytes


class ChangelogBuilderTestCase(unittest.TestCase):
    maxDiff = None

    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_changelog_builder(self, git_mock: MagicMock):
        today = datetime.today().strftime("%Y-%m-%d")

        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"

        git_mock.return_value.list_tags.return_value = ["v0.0.1"]
        git_mock.return_value.log.return_value = [
            "1234567 Add: foo bar",
            "8abcdef Add: bar baz",
            "8abcd3f Add bar baz",
            "8abcd3d Adding bar baz",
            "1337abc Change: bar to baz",
            "42a42a4 Remove: foo bar again",
            "fedcba8 Test: bar baz testing",
            "dead901 Refactor: bar baz ref",
            "fedcba8 Fix: bar baz fixing",
            "d0c4d0c Doc: bar baz documenting",
        ]

        expected_output = f"""## [0.0.2] - {today}

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

[0.0.2]: https://github.com/foo/bar/compare/v0.0.1...v0.0.2"""

        changelog_builder = ChangelogBuilder(
            space="foo",
            project="bar",
            config=config_toml,
        )
        changelog = changelog_builder.create_changelog(
            last_version="0.0.1", next_version="0.0.2"
        )

        self.assertEqual(changelog, expected_output)

        git_mock.return_value.log.assert_called_once_with(
            "v0.0.1..HEAD", oneline=True
        )

    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_changelog_builder_no_commits(self, git_mock: MagicMock):
        today = datetime.today().strftime("%Y-%m-%d")

        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"
        expected_output = f"""## [0.0.2] - {today}

[0.0.2]: https://github.com/foo/bar/compare/v0.0.1...v0.0.2"""

        git_mock.return_value.log.return_value = []

        changelog_builder = ChangelogBuilder(
            space="foo",
            project="bar",
            config=config_toml,
        )
        changelog = changelog_builder.create_changelog(
            last_version="0.0.1", next_version="0.0.2"
        )

        self.assertEqual(changelog, expected_output)

        git_mock.return_value.log.assert_called_once_with(
            "v0.0.1..HEAD", oneline=True
        )

    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_changelog_builder_no_last_version(self, git_mock: MagicMock):
        today = datetime.today().strftime("%Y-%m-%d")

        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"

        git_mock.return_value.log.return_value = [
            "1234567 Add: foo bar",
            "8abcdef Add: bar baz",
            "8abcd3f Add bar baz",
            "8abcd3d Adding bar baz",
            "1337abc Change: bar to baz",
            "42a42a4 Remove: foo bar again",
            "fedcba8 Test: bar baz testing",
            "dead901 Refactor: bar baz ref",
            "fedcba8 Fix: bar baz fixing",
            "d0c4d0c Doc: bar baz documenting",
        ]
        git_mock.return_value.rev_list.return_value = ["123"]

        expected_output = f"""## [0.0.2] - {today}

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

[0.0.2]: https://github.com/foo/bar/compare/123...v0.0.2"""

        changelog_builder = ChangelogBuilder(
            project="bar",
            space="foo",
            config=config_toml,
        )
        changelog = changelog_builder.create_changelog(next_version="0.0.2")

        self.assertEqual(changelog, expected_output)

        git_mock.return_value.log.assert_called_once_with(oneline=True)

    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_changelog_builder_no_next_version(self, git_mock: MagicMock):
        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"

        git_mock.return_value.log.return_value = [
            "1234567 Add: foo bar",
            "8abcdef Add: bar baz",
            "8abcd3f Add bar baz",
            "8abcd3d Adding bar baz",
            "1337abc Change: bar to baz",
            "42a42a4 Remove: foo bar again",
            "fedcba8 Test: bar baz testing",
            "dead901 Refactor: bar baz ref",
            "fedcba8 Fix: bar baz fixing",
            "d0c4d0c Doc: bar baz documenting",
        ]
        git_mock.return_value.rev_list.return_value = ["123"]

        expected_output = """## [Unreleased]

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

[Unreleased]: https://github.com/foo/bar/compare/v0.0.1...HEAD"""

        changelog_builder = ChangelogBuilder(
            project="bar",
            space="foo",
            config=config_toml,
        )
        changelog = changelog_builder.create_changelog(last_version="0.0.1")

        self.assertEqual(changelog, expected_output)

        git_mock.return_value.log.assert_called_once_with(
            "v0.0.1..HEAD", oneline=True
        )

    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_changelog_builder_no_next_and_last_version(
        self, git_mock: MagicMock
    ):
        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"

        git_mock.return_value.log.return_value = [
            "1234567 Add: foo bar",
            "8abcdef Add: bar baz",
            "8abcd3f Add bar baz",
            "8abcd3d Adding bar baz",
            "1337abc Change: bar to baz",
            "42a42a4 Remove: foo bar again",
            "fedcba8 Test: bar baz testing",
            "dead901 Refactor: bar baz ref",
            "fedcba8 Fix: bar baz fixing",
            "d0c4d0c Doc: bar baz documenting",
        ]
        git_mock.return_value.rev_list.return_value = ["123"]

        expected_output = """## [Unreleased]

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

[Unreleased]: https://github.com/foo/bar/compare/123...HEAD"""

        changelog_builder = ChangelogBuilder(
            project="bar",
            space="foo",
            config=config_toml,
        )
        changelog = changelog_builder.create_changelog()

        self.assertEqual(changelog, expected_output)

        git_mock.return_value.log.assert_called_once_with(oneline=True)

    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_changelog_builder_no_conventional_commits(
        self, git_mock: MagicMock
    ):
        today = datetime.today().strftime("%Y-%m-%d")

        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"
        expected_output = f"""## [0.0.2] - {today}

[0.0.2]: https://github.com/foo/bar/compare/v0.0.1...v0.0.2"""

        git_mock.return_value.list_tags.return_value = ["v0.0.1"]
        git_mock.return_value.log.return_value = [
            "1234567 foo bar",
            "8abcdef bar baz",
        ]
        changelog_builder = ChangelogBuilder(
            space="foo",
            project="bar",
            config=config_toml,
        )
        changelog = changelog_builder.create_changelog(
            last_version="0.0.1", next_version="0.0.2"
        )

        self.assertEqual(changelog, expected_output)

        git_mock.return_value.log.assert_called_once_with(
            "v0.0.1..HEAD", oneline=True
        )

    def test_changelog_builder_config_file_not_exists(self):
        with temp_directory() as temp_dir, self.assertRaisesRegex(
            ChangelogBuilderError,
            r"Changelog Config file '.*\.toml' does not exist\.",
        ):
            ChangelogBuilder(
                space="foo",
                project="bar",
                config=temp_dir / "changelog.toml",
            )

    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_changelog_builder_with_default_changelog_config(
        self, git_mock: MagicMock
    ):
        today = datetime.today().strftime("%Y-%m-%d")

        git_mock.return_value.log.return_value = [
            "1234567 Add: foo bar",
            "8abcdef Add: bar baz",
            "8abcd3f Add bar baz",
            "8abcd3d Adding bar baz",
            "1337abc Change: bar to baz",
            "42a42a4 Remove: foo bar again",
            "fedcba8 Test: bar baz testing",
            "dead901 Refactor: bar baz ref",
            "fedcba8 Fix: bar baz fixing",
            "d0c4d0c Doc: bar baz documenting",
        ]

        changelog_builder = ChangelogBuilder(
            space="foo",
            project="bar",
        )
        expected_output = f"""## [0.0.2] - {today}

## Added
* foo bar [1234567](https://github.com/foo/bar/commit/1234567)
* bar baz [8abcdef](https://github.com/foo/bar/commit/8abcdef)

## Removed
* foo bar again [42a42a4](https://github.com/foo/bar/commit/42a42a4)

## Changed
* bar to baz [1337abc](https://github.com/foo/bar/commit/1337abc)

## Bug Fixes
* bar baz fixing [fedcba8](https://github.com/foo/bar/commit/fedcba8)

[0.0.2]: https://github.com/foo/bar/compare/v0.0.1...v0.0.2"""

        changelog = changelog_builder.create_changelog(
            last_version="0.0.1", next_version="0.0.2"
        )
        self.assertEqual(changelog, expected_output)

        git_mock.return_value.log.assert_called_once_with(
            "v0.0.1..HEAD", oneline=True
        )

    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_changelog_builder_with_empty_git_tag_prefix(
        self, git_mock: MagicMock
    ):
        today = datetime.today().strftime("%Y-%m-%d")

        git_mock.return_value.log.return_value = [
            "1234567 Add: foo bar",
            "8abcdef Add: bar baz",
            "8abcd3f Add bar baz",
            "8abcd3d Adding bar baz",
            "1337abc Change: bar to baz",
            "42a42a4 Remove: foo bar again",
            "fedcba8 Test: bar baz testing",
            "dead901 Refactor: bar baz ref",
            "fedcba8 Fix: bar baz fixing",
            "d0c4d0c Doc: bar baz documenting",
        ]

        changelog_builder = ChangelogBuilder(
            space="foo",
            project="bar",
            git_tag_prefix="",
        )
        expected_output = f"""## [0.0.2] - {today}

## Added
* foo bar [1234567](https://github.com/foo/bar/commit/1234567)
* bar baz [8abcdef](https://github.com/foo/bar/commit/8abcdef)

## Removed
* foo bar again [42a42a4](https://github.com/foo/bar/commit/42a42a4)

## Changed
* bar to baz [1337abc](https://github.com/foo/bar/commit/1337abc)

## Bug Fixes
* bar baz fixing [fedcba8](https://github.com/foo/bar/commit/fedcba8)

[0.0.2]: https://github.com/foo/bar/compare/0.0.1...0.0.2"""

        changelog = changelog_builder.create_changelog(
            last_version="0.0.1", next_version="0.0.2"
        )
        self.assertEqual(changelog, expected_output)

        git_mock.return_value.log.assert_called_once_with(
            "0.0.1..HEAD", oneline=True
        )

    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_write_changelog_to_file(self, git_mock: MagicMock):
        today = datetime.today().strftime("%Y-%m-%d")

        own_path = Path(__file__).absolute().parent
        config_toml = own_path / "changelog.toml"

        git_mock.return_value.list_tags.return_value = ["v0.0.1"]
        git_mock.return_value.log.return_value = [
            "1234567 Add: foo bar",
            "8abcdef Add: bar baz",
            "8abcd3f Add bar baz",
            "8abcd3d Adding bar baz",
            "1337abc Change: bar to baz",
            "42a42a4 Remove: foo bar again",
            "fedcba8 Test: bar baz testing",
            "dead901 Refactor: bar baz ref",
            "fedcba8 Fix: bar baz fixing",
            "d0c4d0c Doc: bar baz documenting",
        ]

        expected_output = f"""## [0.0.2] - {today}

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

[0.0.2]: https://github.com/foo/bar/compare/v0.0.1...v0.0.2"""

        changelog_builder = ChangelogBuilder(
            space="foo", project="bar", config=config_toml
        )

        with temp_directory() as temp_dir:
            changelog_file = temp_dir / "changelog.md"
            changelog_builder.create_changelog_file(
                changelog_file, last_version="0.0.1", next_version="0.0.2"
            )
            changelog = changelog_file.read_text(encoding="utf8")

        self.assertEqual(changelog, expected_output)

        git_mock.return_value.log.assert_called_once_with(
            "v0.0.1..HEAD", oneline=True
        )
