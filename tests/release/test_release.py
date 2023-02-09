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
from unittest.mock import MagicMock, call, patch

import httpx

from pontos.git import Git
from pontos.release.main import parse_args
from pontos.release.release import ReleaseReturnValue, release
from pontos.terminal.terminal import Terminal
from pontos.testing import temp_git_repository


def mock_terminal() -> MagicMock:
    return MagicMock(spec=Terminal)


class ReleaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GITHUB_TOKEN"] = "foo"
        os.environ["GITHUB_USER"] = "bar"
        self.valid_gh_release_response = (
            '{"zipball_url": "zip", "tarball_url":'
            ' "tar", "upload_url":"upload"}'
        )

    @patch("pontos.release.release.Git", autospec=True)
    @patch("pontos.release.release.Path", autospec=True)
    @patch("pontos.github.api.api.httpx", autospec=True)
    @patch("pontos.github.api.release.httpx", autospec=True)
    @patch("pontos.release.release.update_version", autospec=True)
    @patch("pontos.release.release.changelog", autospec=True)
    def test_release_successfully(
        self,
        changelog_mock,
        update_version_mock,
        requests_mock,
        requests2_mock,
        _path_mock,
        _git_mock,
    ):
        update_version_mock.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

        fake_post = MagicMock(spec=httpx.Response).return_value
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        requests_mock.post.return_value = fake_post
        requests2_mock.post.return_value = fake_post

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
                "0.0.2dev",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch("pontos.release.release.Path", autospec=True)
    @patch("pontos.github.api.api.httpx", autospec=True)
    @patch("pontos.github.api.release.httpx", autospec=True)
    @patch("pontos.release.release.update_version", autospec=True)
    @patch("pontos.release.release.changelog", autospec=True)
    def test_release_conventional_commits_successfully(
        self,
        changelog_mock,
        update_version_mock,
        requests_mock,
        requests2_mock,
        _path_mock,
        _git_mock,
    ):
        update_version_mock.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

        fake_post = MagicMock(spec=httpx.Response).return_value
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        requests_mock.post.return_value = fake_post
        requests2_mock.post.return_value = fake_post

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-version",
                "1.2.3",
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

        update_version_mock.assert_called_with(
            terminal,
            "1.2.4",
            develop=True,
        )
        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch("pontos.release.release.Path", autospec=True)
    @patch("pontos.github.api.api.httpx", autospec=True)
    @patch("pontos.github.api.release.httpx", autospec=True)
    @patch("pontos.release.release.update_version", autospec=True)
    @patch("pontos.release.release.changelog", autospec=True)
    def test_not_release_successfully_when_github_create_release_fails(
        self,
        changelog_mock,
        update_version_mock,
        requests_mock,
        requests2_mock,
        _path_mock,
        _git_mock,
    ):
        update_version_mock.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

        fake_post = MagicMock(spec=httpx.Response).return_value
        fake_post.status_code = 401
        fake_post.text = self.valid_gh_release_response
        fake_post.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Authorization required",
            response=fake_post,
            request=requests_mock.post,
        )
        requests_mock.post.return_value = fake_post
        requests2_mock.post.return_value = fake_post

        _, token, args = parse_args(
            [
                "release",
                "--release-version",
                "0.0.1",
            ]
        )

        with temp_git_repository():
            git = Git()
            git.add_remote("origin", "https://foo.com/bar.git")

            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )
        self.assertEqual(released, ReleaseReturnValue.CREATE_RELEASE_ERROR)

    @patch("pontos.release.release.Git", autospec=True)
    @patch("pontos.release.release.Path", autospec=True)
    @patch("pontos.github.api.api.httpx", autospec=True)
    @patch("pontos.github.api.release.httpx", autospec=True)
    @patch("pontos.release.release.update_version", autospec=True)
    @patch("pontos.release.release.changelog", autospec=True)
    def test_release_to_specific_git_remote(
        self,
        changelog_mock,
        update_version_mock,
        requests_mock,
        requests2_mock,
        _path_mock,
        git_mock,
    ):
        update_version_mock.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

        fake_post = MagicMock(spec=httpx.Response).return_value
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        requests_mock.post.return_value = fake_post
        requests2_mock.post.return_value = fake_post

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
        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

        git_mock.return_value.push.assert_called_with(
            follow_tags=True, remote="upstream"
        )
        # git_mock.return_value.add.assert_called_with()
        git_mock.return_value.add.assert_has_calls(
            [
                call("MyProject.conf"),
                call("*__version__.py"),
                call("version.go"),
                call("CHANGELOG.md"),
            ]
        )
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1\n"
            "* Add empty changelog after 0.0.1",
            verify=False,
            gpg_signing_key="1234",
        )
