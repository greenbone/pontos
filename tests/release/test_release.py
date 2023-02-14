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
from unittest.mock import AsyncMock, MagicMock, call, patch

from httpx import HTTPStatusError, Request, Response

from pontos.release.main import parse_args
from pontos.release.release import ReleaseReturnValue, release
from pontos.terminal.terminal import Terminal
from pontos.testing import temp_git_repository
from pontos.version.go import GoVersionCommand
from pontos.version.version import VersionUpdate


def mock_terminal() -> MagicMock:
    return MagicMock(spec=Terminal)


class ReleaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GITHUB_TOKEN"] = "foo"
        os.environ["GITHUB_USER"] = "bar"

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._update_version", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    def test_release_successfully(
        self,
        create_release_mock: AsyncMock,
        update_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        update_version_mock.return_value = VersionUpdate(
            previous="0.0.1", new="0.0.2.dev1", changed_files=["MyProject.conf"]
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        git_mock.return_value.add.assert_has_calls(
            [call(Path("CHANGELOG.md")), call("MyProject.conf")]
        )
        git_mock.return_value.commit.assert_called_once_with(
            "Automatic adjustments after release\n\n* Update to version "
            "0.0.2.dev1\n* Add empty changelog after 0.0.1",
            verify=False,
            gpg_signing_key="123",
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:], ("0.0.1", "TOKEN")
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._update_version", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    def test_release_conventional_commits_successfully(
        self,
        create_release_mock: AsyncMock,
        update_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        update_version_mock.return_value = VersionUpdate(
            previous="0.0.1", new="0.0.2.dev1", changed_files=["MyProject.conf"]
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
                "-CC",
            ]
        )
        terminal = mock_terminal()

        with temp_git_repository():
            released = release(
                terminal=terminal,
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            "Automatic adjustments after release\n\n* Update to version "
            "0.0.2.dev1",
            verify=False,
            gpg_signing_key="123",
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:], ("0.0.1", "TOKEN")
        )
        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._update_version", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    def test_not_release_successfully_when_github_create_release_fails(
        self,
        create_release_mock: AsyncMock,
        update_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        update_version_mock.return_value = VersionUpdate(
            previous="0.0.1", new="0.0.2.dev1", changed_files=["MyProject.conf"]
        )
        create_release_mock.side_effect = HTTPStatusError(
            "Error during a request",
            request=MagicMock(spec=Request),
            response=MagicMock(spec=Response),
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_called_once_with(
            follow_tags=True, remote=None
        )
        git_mock.return_value.add.assert_not_called()
        git_mock.return_value.commit.assert_not_called()

        self.assertEqual(released, ReleaseReturnValue.CREATE_RELEASE_ERROR)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._update_version", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    def test_release_to_specific_git_remote(
        self,
        create_release_mock: AsyncMock,
        update_version_mock: MagicMock,
        git_mock,
    ):
        update_version_mock.return_value = VersionUpdate(
            previous="0.0.1", new="0.0.2.dev1", changed_files=["MyProject.conf"]
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
                "--git-remote-name",
                "upstream",
                "--git-signing-key",
                "1234",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_called_with(
            follow_tags=True, remote="upstream"
        )
        # git_mock.return_value.add.assert_called_with()
        git_mock.return_value.add.assert_has_calls(
            [
                call(Path("CHANGELOG.md")),
                call("MyProject.conf"),
            ]
        )
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1\n"
            "* Add empty changelog after 0.0.1",
            verify=False,
            gpg_signing_key="1234",
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:], ("0.0.1", "TOKEN")
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._update_version", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    def test_release_without_release_version(
        self,
        create_release_mock: AsyncMock,
        update_version_mock: MagicMock,
        git_mock,
    ):
        update_version_mock.return_value = VersionUpdate(
            previous="0.0.1", new="0.0.2", changed_files=["MyProject.conf"]
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "1234",
            ]
        )

        with temp_git_repository() as temp_dir:
            go_mod = temp_dir / GoVersionCommand.project_file_name
            go_mod.touch()
            version_file = temp_dir / GoVersionCommand.version_file_path
            version_file.write_text('var version = "0.0.1"', encoding="utf8")

            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

        git_mock.return_value.push.assert_called_with(
            follow_tags=True, remote=None
        )
        # git_mock.return_value.add.assert_called_with()
        git_mock.return_value.add.assert_has_calls(
            [
                call(Path("CHANGELOG.md")),
                call("MyProject.conf"),
            ]
        )
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2\n"
            "* Add empty changelog after 0.0.1",
            verify=False,
            gpg_signing_key="1234",
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:], ("0.0.1", "TOKEN")
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)
