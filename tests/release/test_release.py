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
from unittest.mock import MagicMock, call, patch

import httpx

from pontos import changelog, release
from pontos.git import Git
from pontos.release.helper import version
from pontos.testing import temp_git_repository


class ReleaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GITHUB_TOKEN"] = "foo"
        os.environ["GITHUB_USER"] = "bar"
        self.valid_gh_release_response = (
            '{"zipball_url": "zip", "tarball_url":'
            ' "tar", "upload_url":"upload"}'
        )

    @patch("pontos.release.release.Git", spec=Git)
    @patch("pontos.release.release.Path", spec=Path)
    @patch("pontos.github.api.api.httpx", spec=httpx)
    @patch("pontos.github.api.release.httpx", spec=httpx)
    @patch("pontos.release.helper.version", spec=version)
    @patch("pontos.release.release.changelog", spec=changelog)
    def test_release_successfully(
        self,
        changelog_mock,
        version_mock,
        requests_mock,
        requests2_mock,
        _path_mock,
        _git_mock,
    ):
        version_mock.main.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

        fake_post = MagicMock(spec=httpx.Response).return_value
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        requests_mock.post.return_value = fake_post
        requests2_mock.post.return_value = fake_post

        args = [
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

        with temp_git_repository(), redirect_stdout(StringIO()):
            released = release.main(
                leave=False,
                args=args,
            )
        self.assertTrue(released)

    @patch("pontos.release.release.Git", spec=Git)
    @patch("pontos.release.release.Path", spec=Path)
    @patch("pontos.github.api.api.httpx", spec=httpx)
    @patch("pontos.github.api.release.httpx", spec=httpx)
    @patch("pontos.release.helper.version", spec=version)
    @patch("pontos.release.release.changelog", spec=changelog)
    def test_release_conventional_commits_successfully(
        self,
        changelog_mock,
        version_mock,
        requests_mock,
        requests2_mock,
        _path_mock,
        _git_mock,
    ):
        version_mock.main.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

        fake_post = MagicMock(spec=httpx.Response).return_value
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        requests_mock.post.return_value = fake_post
        requests2_mock.post.return_value = fake_post

        args = [
            "release",
            "--project",
            "foo",
            "--git-signing-key",
            "123",
            "--release-version",
            "1.2.3",
            "-CC",
        ]

        with temp_git_repository(), redirect_stdout(StringIO()):
            released = release.main(
                leave=False,
                args=args,
            )

        version_mock.main.assert_called_with(
            leave=False, args=["--quiet", "update", "1.2.4", "--develop"]
        )
        self.assertTrue(released)

    @patch("pontos.release.release.Git", spec=Git)
    @patch("pontos.release.release.Path", spec=Path)
    @patch("pontos.github.api.api.httpx", spec=httpx)
    @patch("pontos.github.api.release.httpx", spec=httpx)
    @patch("pontos.release.helper.version", spec=version)
    @patch("pontos.release.release.changelog", spec=changelog)
    def test_not_release_successfully_when_github_create_release_fails(
        self,
        changelog_mock,
        version_mock,
        requests_mock,
        requests2_mock,
        _path_mock,
        _git_mock,
    ):

        version_mock.main.return_value = (True, "MyProject.conf")
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

        args = [
            "release",
            "--release-version",
            "0.0.1",
        ]

        with temp_git_repository(), redirect_stdout(StringIO()):
            git = Git()
            git.add_remote("origin", "https://foo.com/bar.git")

            released = release.main(
                leave=False,
                args=args,
            )
        self.assertFalse(released)

    @patch("pontos.release.release.Git", spec=Git)
    @patch("pontos.release.release.Path", spec=Path)
    @patch("pontos.github.api.api.httpx", spec=httpx)
    @patch("pontos.github.api.release.httpx", spec=httpx)
    @patch("pontos.release.helper.version", spec=version)
    @patch("pontos.release.release.changelog", spec=changelog)
    def test_release_to_specific_git_remote(
        self,
        changelog_mock,
        version_mock,
        requests_mock,
        requests2_mock,
        _path_mock,
        git_mock,
    ):
        version_mock.main.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

        fake_post = MagicMock(spec=httpx.Response).return_value
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        requests_mock.post.return_value = fake_post
        requests2_mock.post.return_value = fake_post

        args = [
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

        with temp_git_repository(), redirect_stdout(StringIO()):
            released = release.main(
                leave=False,
                args=args,
            )
        self.assertTrue(released)

        git_mock.return_value.push.assert_called_with(
            follow_tags=True, remote="upstream"
        )
        # git_mock.return_value.add.assert_called_with()
        git_mock.return_value.add.assert_has_calls(
            [
                call("MyProject.conf"),
                call("*__version__.py"),
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
