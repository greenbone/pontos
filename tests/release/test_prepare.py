# Copyright (C) 2020-2022 Greenbone Networks GmbH
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

# pylint: disable=line-too-long

import os
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from pontos.release.main import parse_args
from pontos.release.prepare import PrepareReturnValue, prepare
from pontos.terminal.terminal import Terminal
from pontos.testing import temp_git_repository
from pontos.version.errors import VersionError
from pontos.version.helper import calculate_calendar_version
from pontos.version.version import VersionUpdate


def mock_terminal() -> MagicMock:
    return MagicMock(spec=Terminal)


class PrepareTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GITHUB_TOKEN"] = "foo"
        os.environ["GITHUB_USER"] = "bar"

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.find_signing_key", autospec=True)
    @patch("pontos.release.prepare.update_changelog", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._update_version", autospec=True
    )
    @patch(
        "pontos.release.prepare.PrepareCommand._create_old_changelog",
        autospec=True,
    )
    def test_prepare_successfully(
        self,
        create_old_changelog_mock: MagicMock,
        update_version_mock: MagicMock,
        update_changelog_mock: MagicMock,
        find_signing_key_mock: MagicMock,
        git_mock: MagicMock,
    ):
        update_changelog_mock.return_value = ("updated", "changelog")
        update_version_mock.return_value = VersionUpdate(
            previous="0.0.0", new="0.0.1", changed_files=["MyProject.conf"]
        )
        create_old_changelog_mock.return_value = "A changelog text"
        find_signing_key_mock.return_value = "0815"

        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(released, PrepareReturnValue.SUCCESS)

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            "Automatic release to 0.0.1", verify=False, gpg_signing_key="0815"
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.1",
            message="Automatic release to 0.0.1",
            gpg_key_id="0815",
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.find_signing_key", autospec=True)
    @patch("pontos.release.prepare.get_current_version", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._update_version", autospec=True
    )
    @patch("pontos.release.prepare.update_changelog", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._create_old_changelog",
        autospec=True,
    )
    def test_prepare_calendar_successfully(
        self,
        create_old_changelog_mock: MagicMock,
        update_changelog_mock: MagicMock,
        update_version_mock: MagicMock,
        get_current_version_mock: MagicMock,
        find_signing_key_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = "21.6.0"
        get_current_version_mock.return_value = current_version
        calendar_version = calculate_calendar_version(current_version)
        update_version_mock.return_value = VersionUpdate(
            previous=current_version,
            new=calendar_version,
            changed_files=["MyProject.conf"],
        )
        update_changelog_mock.return_value = ("updated", "changelog")
        create_old_changelog_mock.return_value = "A changelog text"
        find_signing_key_mock.return_value = "0815"

        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--calendar",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(released, PrepareReturnValue.SUCCESS)

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            f"Automatic release to {calendar_version}",
            verify=False,
            gpg_signing_key="0815",
        )
        git_mock.return_value.tag.assert_called_once_with(
            f"v{calendar_version}",
            message=f"Automatic release to {calendar_version}",
            gpg_key_id="0815",
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._update_version", autospec=True
    )
    @patch("pontos.release.prepare.update_changelog", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._create_old_changelog",
        autospec=True,
    )
    def test_use_git_signing_key_on_prepare(
        self,
        create_old_changelog_mock: MagicMock,
        update_changelog_mock: MagicMock,
        update_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        update_version_mock.return_value = VersionUpdate(
            previous="0.0.0", new="0.0.1", changed_files=["MyProject.conf"]
        )
        update_changelog_mock.return_value = ("updated", "changelog")
        create_old_changelog_mock.return_value = "A changelog text"

        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--git-signing-key",
                "0815",
                "--release-version",
                "0.0.1",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )

        self.assertEqual(released, PrepareReturnValue.SUCCESS)

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="0815", message="Automatic release to 0.0.1"
        )
        git_mock.return_value.commit.assert_called_once_with(
            "Automatic release to 0.0.1", verify=False, gpg_signing_key="0815"
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    def test_fail_if_tag_is_already_taken(
        self,
        git_mock: MagicMock,
    ):
        git_mock.return_value.list_tags.return_value = ["v0.0.1"]

        _, _, args = parse_args(
            [
                "prepare",
                "--release-version",
                "0.0.1",
                "--project",
                "bla",
                "--git-signing-key",
                "1337",
            ]
        )

        with temp_git_repository():
            release = prepare(
                terminal=mock_terminal(),
                args=args,
            )

            self.assertEqual(release, PrepareReturnValue.ALREADY_TAKEN)

        git_mock.return_value.list_tags.assert_called_once()

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.update_changelog", autospec=True)
    def test_no_release_when_no_project_found(
        self,
        update_changelog_mock: MagicMock,
        _git_mock: MagicMock,
    ):
        update_changelog_mock.return_value = ("updated", "changelog")

        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(released, PrepareReturnValue.UPDATE_VERSION_ERROR)

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._update_version", autospec=True
    )
    def test_no_release_when_updating_version_fails(
        self,
        update_version_mock: MagicMock,
        _git_mock: MagicMock,
    ):
        update_version_mock.side_effect = VersionError(
            "Error updating the version"
        )

        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(released, PrepareReturnValue.UPDATE_VERSION_ERROR)

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._update_version", autospec=True
    )
    @patch("pontos.release.prepare.ChangelogBuilder", autospec=True)
    def test_prepare_conventional_commits(
        self,
        changelog_builder_mock: MagicMock,
        update_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        update_version_mock.return_value = VersionUpdate(
            previous="0.0.0", new="0.0.1", changed_files=["MyProject.conf"]
        )

        own_path = Path(__file__).absolute().parent
        with temp_git_repository() as temp_dir:
            release_file = temp_dir / ".release.md"
            changelog_file = own_path / "v1.2.3.md"
            builder = changelog_builder_mock.return_value
            builder.create_changelog_file.return_value = changelog_file

            _, _, args = parse_args(
                [
                    "prepare",
                    "--project",
                    "foo",
                    "--release-version",
                    "1.2.3",
                    "-CC",
                ]
            )
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )

            self.assertEqual(released, PrepareReturnValue.SUCCESS)

            git_mock.return_value.add.assert_has_calls(
                [call("MyProject.conf"), call(changelog_file)]
            )

            expected_release_content = """## [21.8.1] - 2021-08-23

## Added

* Need for commits. [1234567](https://github.com/foo/bar/commit/1234567)

## Changed

* fooooo. [1234568](https://github.com/foo/bar/commit/1234568)

[21.8.1]: https://github.com/y0urself/test_workflows/compare/21.8.0...21.8.1"""

            self.assertEqual(
                release_file.read_text(encoding="utf-8"),
                expected_release_content,
            )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._update_version", autospec=True
    )
    def test_prepare_with_changelog(
        self,
        update_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        update_version_mock.return_value = VersionUpdate(
            previous="0.0.0", new="1.2.3", changed_files=["MyProject.conf"]
        )
        content = """# Changelog

All notable changes to this project will be documented in this file.

## [unreleased]

## Added

* Need for commits. [1234567](https://github.com/foo/bar/commit/1234567)

## Changed

* fooooo. [1234568](https://github.com/foo/bar/commit/1234568)

[unreleased]: https://github.com/y0urself/test_workflows/compare/1.2.2...1.2.3"""

        with temp_git_repository() as temp_dir:
            release_file = temp_dir / ".release.md"
            changelog_file = temp_dir / "CHANGELOG.md"
            changelog_file.write_text(content, encoding="utf8")

            _, _, args = parse_args(
                [
                    "prepare",
                    "--project",
                    "foo",
                    "--release-version",
                    "1.2.3",
                    "--changelog",
                    str(changelog_file),
                ]
            )
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )

            self.assertEqual(released, PrepareReturnValue.SUCCESS)

            git_mock.return_value.add.assert_has_calls(
                [call("MyProject.conf"), call(changelog_file)]
            )

            expected_release_content = f"""## [1.2.3] - {date.today().isoformat()}

## Added

* Need for commits. [1234567](https://github.com/foo/bar/commit/1234567)

## Changed

* fooooo. [1234568](https://github.com/foo/bar/commit/1234568)

[1.2.3]: https://github.com/y0urself/test_workflows/compare/1.2.2...1.2.3
"""

            self.assertEqual(
                release_file.read_text(encoding="utf-8").strip(),
                expected_release_content.strip(),
            )
