# SPDX-FileCopyrightText: 2021-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from pontos.changelog.conventional_commits import (
    ChangelogBuilder,
    ChangelogBuilderError,
    ConventionalCommits,
)
from pontos.testing import temp_directory


@dataclass
class StdOutput:
    stdout: bytes


class ChangelogBuilderTestCase(unittest.TestCase):
    maxDiff = None

    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_changelog_builder_with_config(self, git_mock: MagicMock):
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
            repository="foo/bar",
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
            repository="foo/bar",
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
            repository="foo/bar",
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
            repository="foo/bar",
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
            repository="foo/bar",
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
            repository="foo/bar",
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
        with (
            temp_directory() as temp_dir,
            self.assertRaisesRegex(
                ChangelogBuilderError,
                r"Changelog Config file '.*\.toml' does not exist\.",
            ),
        ):
            ChangelogBuilder(
                repository="foo/bar",
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
            "a1c5a0b Deps: Update foo from 1.2.3 to 3.2.1",
        ]

        changelog_builder = ChangelogBuilder(
            repository="foo/bar",
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

## Dependencies
* Update foo from 1.2.3 to 3.2.1 [a1c5a0b](https://github.com/foo/bar/commit/a1c5a0b)

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
            repository="foo/bar",
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
            repository="foo/bar",
            config=config_toml,
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


class ConventionalCommitsTestCase(unittest.TestCase):
    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    def test_get_commits(self, git_mock: MagicMock):
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

        conventional_commits = ConventionalCommits()
        commits = conventional_commits.get_commits(from_ref="0.0.1")

        self.assertEqual(len(commits), 4)  # four commit types
        self.assertEqual(len(commits["Added"]), 2)
        self.assertEqual(len(commits["Changed"]), 1)
        self.assertEqual(len(commits["Removed"]), 1)
        self.assertEqual(len(commits["Bug Fixes"]), 1)

        removed = commits["Removed"][0]
        self.assertEqual(removed.commit_id, "42a42a4")
        self.assertEqual(removed.message, "foo bar again")

        commit_id, message = removed
        self.assertEqual(commit_id, "42a42a4")
        self.assertEqual(message, "foo bar again")

    def test_default_config(self):
        conventional_commits = ConventionalCommits()

        categories = conventional_commits.commit_types()

        self.assertEqual(len(categories), 5)

        add = categories[0]
        self.assertEqual(add["message"], "^add")
        self.assertEqual(add["group"], "Added")

        remove = categories[1]
        self.assertEqual(remove["message"], "^remove")
        self.assertEqual(remove["group"], "Removed")

        change = categories[2]
        self.assertEqual(change["message"], "^change")
        self.assertEqual(change["group"], "Changed")

        fix = categories[3]
        self.assertEqual(fix["message"], "^fix")
        self.assertEqual(fix["group"], "Bug Fixes")

        deps = categories[4]
        self.assertEqual(deps["message"], "^deps")
        self.assertEqual(deps["group"], "Dependencies")
