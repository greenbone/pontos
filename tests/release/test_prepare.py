# -*- coding: utf-8 -*-
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
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock, call, patch

import requests

from pontos import changelog, release
from pontos.release.helper import version


class PrepareTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GITHUB_TOKEN"] = "foo"
        os.environ["GITHUB_USER"] = "bar"

    @patch("pontos.release.prepare.shell_cmd_runner")
    def test_prepare_successfully(self, _shell_mock):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, "MyProject.conf")
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ("updated", "changelog")
        args = [
            "prepare",
            "--release-version",
            "0.0.1",
        ]
        with redirect_stdout(StringIO()):
            released = release.main(
                _path=fake_path_class,
                _version=fake_version,
                _changelog=fake_changelog,
                leave=False,
                args=args,
            )
        self.assertTrue(released)

    @patch("pontos.release.prepare.shell_cmd_runner")
    def test_prepare_calendar_successfully(self, _shell_mock):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, "MyProject.conf")
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ("updated", "changelog")

        args = [
            "prepare",
            "--calendar",
        ]
        with redirect_stdout(StringIO()):
            released = release.main(
                _path=fake_path_class,
                _version=fake_version,
                _changelog=fake_changelog,
                leave=False,
                args=args,
            )
        self.assertTrue(released)

    @patch("pontos.release.prepare.shell_cmd_runner")
    def test_use_git_signing_key_on_prepare(self, shell_mock):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, "MyProject.conf")
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ("updated", "changelog")

        args = [
            "prepare",
            "--git-signing-key",
            "0815",
            "--release-version",
            "0.0.1",
        ]

        with redirect_stdout(StringIO()):
            released = release.main(
                _path=fake_path_class,
                _version=fake_version,
                _changelog=fake_changelog,
                leave=False,
                args=args,
            )

        self.assertTrue(released)
        shell_mock.assert_has_calls(
            [
                call(
                    "git commit -S0815 --no-verify -m "
                    "'Automatic release to 0.0.1'"
                ),
                call("git tag -u 0815 v0.0.1 -m 'Automatic release to 0.0.1'"),
            ]
        )

    @patch("pontos.release.prepare.shell_cmd_runner")
    def test_fail_if_tag_is_already_taken(self, shell_mock):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_changelog = MagicMock(spec=changelog)

        shell_mock.return_value = CompletedProcess(
            args="foo", returncode=1, stdout=b"v0.0.1"
        )

        args = [
            "prepare",
            "--release-version",
            "0.0.1",
            "--project",
            "bla",
            "--git-signing-key",
            "1337",
        ]

        with self.assertRaises(SystemExit), redirect_stdout(StringIO()):
            release.main(
                _path=fake_path_class,
                _version=fake_version,
                _changelog=fake_changelog,
                leave=False,
                args=args,
            )

            shell_mock.assert_called_with("git tag -l")
            shell_mock.assert_called_with("git tag v0.0.1 is already taken")

    @patch("pontos.release.prepare.shell_cmd_runner")
    def test_not_release_when_no_project_found(self, _shell_mock):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (False, "")
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ("updated", "changelog")

        args = [
            "prepare",
            "--release-version",
            "0.0.1",
        ]
        with redirect_stdout(StringIO()):
            released = release.main(
                _path=fake_path_class,
                _version=fake_version,
                _changelog=fake_changelog,
                leave=False,
                args=args,
            )
        self.assertFalse(released)

    @patch("pontos.release.prepare.shell_cmd_runner")
    def test_not_release_when_updating_version_fails(self, _shell_mock):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (False, "MyProject.conf")
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ("updated", "changelog")

        args = [
            "prepare",
            "--release-version",
            "0.0.1",
        ]
        with redirect_stdout(StringIO()):
            released = release.main(
                _path=fake_path_class,
                _requests=fake_requests,
                _version=fake_version,
                _changelog=fake_changelog,
                leave=False,
                args=args,
            )
        self.assertFalse(released)

    @patch("pontos.release.prepare.shell_cmd_runner")
    @patch("pontos.changelog.changelog")
    def test_prepare_coventional_commits(self, changelog_mock, _shell_mock):
        fake_requests = MagicMock(spec=requests)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, "MyProject.conf")

        own_path = Path(__file__).absolute().parent
        release_file = own_path.parent.parent / ".release.md"

        builder = changelog_mock.ChangelogBuilder.return_value
        builder.create_changelog_file.return_value = own_path / "v1.2.3.md"

        args = [
            "prepare",
            "--release-version",
            "1.2.3",
            "-CC",
        ]
        with redirect_stdout(StringIO()):
            released = release.main(
                _path=Path,
                _requests=fake_requests,
                _version=fake_version,
                _changelog=changelog_mock,
                leave=False,
                args=args,
            )
        self.assertTrue(released)

        expected_release_content = """## [21.8.1] - 2021-08-23

## Added

* Need for commits. [1234567](https://github.com/foo/bar/commit/1234567)

## Changed

* fooooo. [1234568](https://github.com/foo/bar/commit/1234568)

[21.8.1]: https://github.com/y0urself/test_workflows/compare/21.8.0...21.8.1"""

        self.assertEqual(
            release_file.read_text(encoding="utf-8"), expected_release_content
        )

        release_file.unlink()
