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

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from httpx import HTTPStatusError, Request, Response

from pontos.git.git import ConfigScope, Git
from pontos.release.main import parse_args
from pontos.release.release import ReleaseReturnValue, release
from pontos.terminal.terminal import Terminal
from pontos.testing import temp_git_repository
from pontos.version.errors import VersionError
from pontos.version.go import GoVersionCommand
from pontos.version.version import VersionCommand, VersionUpdate


def mock_terminal() -> MagicMock:
    return MagicMock(spec=Terminal)


@patch.dict("os.environ", {"GITHUB_TOKEN": "foo", "GITHUB_USER": "user"})
class ReleaseTestCase(unittest.TestCase):
    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_successfully(
        self,
        gather_project_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.return_value = VersionUpdate(
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

        version_command_mock.update_version.assert_called_once_with(
            "0.0.2.dev1", develop=True
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:], ("0.0.1", "foo")
        )

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            "Automatic adjustments after release\n\n* Update to version "
            "0.0.2.dev1",
            verify=False,
            gpg_signing_key="123",
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    def test_no_project_settings(self):
        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
                "--git-signing-key",
                "123",
            ]
        )
        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        self.assertEqual(
            released, ReleaseReturnValue.PROJECT_SETTINGS_NOT_FOUND
        )

    @patch("pontos.release.release.gather_project", autospec=True)
    def test_no_release_error(self, gather_project_mock: MagicMock):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.get_current_version.side_effect = VersionError(
            "An error"
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        self.assertEqual(released, ReleaseReturnValue.NO_RELEASE_VERSION)

    @patch("pontos.release.release.gather_project", autospec=True)
    def test_no_release(self, gather_project_mock: MagicMock):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.get_current_version.return_value = None

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        self.assertEqual(released, ReleaseReturnValue.NO_RELEASE_VERSION)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_github_create_release_failure(
        self,
        gather_project_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.return_value = VersionUpdate(
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
                "--next-version",
                "0.0.2.dev1",
                "--git-signing-key",
                "123",
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
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_update_version_error(
        self,
        gather_project_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.side_effect = VersionError(
            "An error"
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

        git_mock.return_value.push.assert_called_once_with(
            follow_tags=True, remote=None
        )
        version_command_mock.update_version.assert_called_once_with(
            "0.0.2.dev1", develop=True
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:], ("0.0.1", "foo")
        )

        git_mock.return_value.add.assert_not_called()
        git_mock.return_value.commit.assert_not_called()

        self.assertEqual(released, ReleaseReturnValue.UPDATE_VERSION_ERROR)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_to_specific_git_remote(
        self,
        gather_project_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.return_value = VersionUpdate(
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

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote="upstream"),
                call(follow_tags=True, remote="upstream"),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:], ("0.0.1", "foo")
        )

        git_mock.return_value.add.assert_called_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1",
            verify=False,
            gpg_signing_key="1234",
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    def test_release_without_arguments(
        self,
        create_release_mock: AsyncMock,
        git_mock,
    ):
        _, token, args = parse_args(
            [
                "release",
            ]
        )

        with temp_git_repository() as temp_dir:
            git = Git()
            git.config("user.signingkey", "1234", scope=ConfigScope.LOCAL)
            git.add_remote("origin", "http://foo/bar.git")

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
        git_mock.return_value.add.assert_called_with(
            GoVersionCommand.version_file_path
        )
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2",
            verify=False,
            gpg_signing_key="1234",
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:], ("0.0.1", "foo")
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)
