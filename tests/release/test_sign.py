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
from unittest.mock import MagicMock, patch

import httpx

from pontos import changelog, release
from pontos.release.helper import version


class SignTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GITHUB_TOKEN"] = "foo"
        self.valid_gh_release_response = (
            '{"zipball_url": "zip", "tarball_url":'
            ' "tar", "upload_url":"upload"}'
        )

    @patch("pontos.release.sign.shell_cmd_runner")
    @patch("pontos.release.helper.Path", spec=Path)
    @patch("pontos.github.api.api.httpx")
    @patch("pontos.release.helper.version", spec=version)
    @patch("pontos.changelog", spec=changelog)
    def test_fail_sign_on_invalid_get_response(
        self,
        changelog_mock,
        version_mock,
        requests_mock,
        _path_mock,
        _shell_mock,
    ):
        version_mock.main.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

        fake_get = MagicMock()
        fake_get.status_code = 404
        fake_get.text = self.valid_gh_release_response
        requests_mock.get.return_value = fake_get

        args = [
            "sign",
            "--project",
            "foo",
            "--release-version",
            "0.0.1",
        ]

        with redirect_stdout(StringIO()), self.assertRaises(httpx.HTTPError):
            release.main(
                leave=False,
                args=args,
            )

    @patch("pontos.release.sign.shell_cmd_runner")
    @patch("pontos.release.sign.Path", spec=Path)
    @patch("pontos.helper.Path", spec=Path)
    @patch("pontos.github.api.api.httpx")
    @patch("pontos.github.api.release.httpx")
    @patch("pontos.helper.httpx.stream")
    @patch("pontos.release.helper.version", spec=version)
    @patch("pontos.changelog", spec=changelog)
    def test_fail_sign_on_upload_fail(
        self,
        changelog_mock,
        version_mock,
        stream_mock,
        request_mock,
        request2_mock,
        _path_mock,
        _path2_mock,
        _shell_mock,
    ):
        version_mock.main.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

        fake_get = MagicMock()
        fake_get.status_code = 200
        fake_get.text = self.valid_gh_release_response
        fake_post = MagicMock()
        fake_post.status_code = 500
        fake_post.is_success = False
        fake_post.text = self.valid_gh_release_response
        fake_post.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=fake_post
        )
        request_mock.get.return_value = fake_get
        request_mock.post.return_value = fake_post
        request2_mock.get.return_value = fake_get
        request2_mock.post.return_value = fake_post

        response = MagicMock()
        response.iter_bytes.side_effect = [
            [b"foo", b"bar", b"baz"],
            [b"lorem", b"ipsum"],
        ]
        response_stream = MagicMock()
        response_stream.__enter__.return_value = response
        stream_mock.return_value = response_stream

        args = [
            "sign",
            "--project",
            "foo",
            "--release-version",
            "0.0.1",
        ]
        with redirect_stdout(StringIO()):
            released = release.main(
                leave=False,
                args=args,
            )

        self.assertFalse(released)

    @patch("pontos.release.sign.shell_cmd_runner")
    @patch("pontos.release.sign.Path", spec=Path)
    @patch("pontos.helper.Path", spec=Path)
    @patch("pontos.github.api.api.httpx")
    @patch("pontos.github.api.release.httpx")
    @patch("pontos.helper.httpx.stream")
    @patch("pontos.release.helper.version", spec=version)
    @patch("pontos.changelog", spec=changelog)
    def test_successfully_sign(
        self,
        changelog_mock,
        version_mock,
        stream_mock,
        request_mock,
        request_mock2,
        _path_mock,
        _path2_mock,
        _shell_mock,
    ):
        version_mock.main.return_value = (True, "MyProject.conf")
        changelog_mock.update.return_value = ("updated", "changelog")

        fake_get = MagicMock()
        fake_get.status_code = 200
        fake_get.text = self.valid_gh_release_response
        fake_post = MagicMock()
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        request_mock.get.return_value = fake_get
        request_mock.post.return_value = fake_post
        request_mock2.get.return_value = fake_get
        request_mock2.post.return_value = fake_post

        response = MagicMock()
        response.iter_bytes.side_effect = [
            [b"foo", b"bar", b"baz"],
            [b"lorem", b"ipsum"],
        ]
        response_stream = MagicMock()
        response_stream.__enter__.return_value = response
        stream_mock.return_value = response_stream

        args = [
            "sign",
            "--project",
            "bar",
            "--release-version",
            "0.0.1",
        ]
        with redirect_stdout(StringIO()):
            released = release.main(
                leave=False,
                args=args,
            )
        self.assertTrue(released)
