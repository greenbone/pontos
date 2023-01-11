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
# pylint: disable=C0413,W0108

import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pontos.release.helper import get_current_version
from pontos.release.main import parse_args
from pontos.release.prepare import PrepareReturnValue, prepare
from pontos.terminal.terminal import Terminal
from pontos.testing import temp_git_repository


def mock_terminal() -> MagicMock:
    return MagicMock(spec=Terminal)


class PrepareTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GITHUB_TOKEN"] = "foo"
        os.environ["GITHUB_USER"] = "bar"

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.Path", autospec=True)
    @patch("pontos.release.prepare.update_version", autospec=True)
    @patch("pontos.release.prepare.changelog", autospec=True)
    def test_prepare_successfully(
        self,
        changelog_mock,
        update_version_mock,
        _path_mock,
        _git_mock,
    ):
        changelog_mock.update.return_value = ("updated", "changelog")
        update_version_mock.return_value = (True, "MyProject.conf")

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

    @patch(
        "pontos.release.helper.get_current_version", spec=get_current_version
    )
    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.Path", autospec=True)
    @patch("pontos.release.prepare.update_version", autospec=True)
    @patch("pontos.release.prepare.changelog", autospec=True)
    def test_prepare_calendar_successfully(
        self,
        changelog_mock,
        update_version_mock,
        _path_mock,
        _git_mock,
        get_current_version_mock,
    ):
        get_current_version_mock.return_value = "21.6.0"
        update_version_mock.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")
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

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.Path", autospec=True)
    @patch("pontos.release.prepare.update_version", autospec=True)
    @patch("pontos.release.prepare.changelog", autospec=True)
    def test_use_git_signing_key_on_prepare(
        self,
        changelog_mock,
        update_version_mock,
        _path_mock,
        git_mock,
    ):
        update_version_mock.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

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

        git_mock.return_value.tag.assert_called_with(
            "v0.0.1", gpg_key_id="0815", message="Automatic release to 0.0.1"
        )
        git_mock.return_value.commit.assert_called_with(
            "Automatic release to 0.0.1", verify=False, gpg_signing_key="0815"
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.Path", autospec=True)
    @patch("pontos.release.prepare.update_version", autospec=True)
    @patch("pontos.release.prepare.changelog", autospec=True)
    def test_fail_if_tag_is_already_taken(
        self,
        _changelog_mock,
        update_version_mock,
        _path_mock,
        git_mock,
    ):
        git_mock.return_value.list_tags.return_value = ["v0.0.1"]

        update_version_mock.return_value = (True, "MyProject.conf")

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
    @patch("pontos.release.prepare.Path", autospec=True)
    @patch("pontos.release.prepare.update_version", autospec=True)
    @patch("pontos.release.prepare.changelog", autospec=True)
    def test_not_release_when_no_project_found(
        self,
        changelog_mock,
        update_version_mock,
        _path_mock,
        _git_mock,
    ):
        update_version_mock.return_value = (False, None)
        changelog_mock.update.return_value = ("updated", "changelog")

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
    @patch("pontos.release.prepare.Path", autospec=True)
    @patch("pontos.release.prepare.update_version", autospec=True)
    @patch("pontos.release.prepare.changelog", autospec=True)
    def test_not_release_when_updating_version_fails(
        self,
        changelog_mock,
        update_version_mock,
        _path_mock,
        _git_mock,
    ):
        update_version_mock.return_value = (False, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

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
    @patch("pontos.release.prepare.changelog", autospec=True)
    @patch("pontos.release.prepare.update_version", autospec=True)
    def test_prepare_conventional_commits(
        self,
        update_version_mock,
        changelog_mock,
        _git_mock,
    ):
        update_version_mock.return_value = (True, "MyProject.conf")

        own_path = Path(__file__).absolute().parent
        with temp_git_repository() as temp_dir:
            release_file = temp_dir / ".release.md"

            builder = changelog_mock.ChangelogBuilder.return_value
            builder.create_changelog_file.return_value = own_path / "v1.2.3.md"

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
