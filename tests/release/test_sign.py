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
from unittest.mock import MagicMock, patch

import requests

from pontos import changelog, release
from pontos.release.helper import version


class SignTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GITHUB_TOKEN"] = "foo"
        os.environ["GITHUB_USER"] = "bar"
        self.valid_gh_release_response = (
            '{"zipball_url": "zip", "tarball_url":'
            ' "tar", "upload_url":"upload"}'
        )

    @patch("pontos.release.sign.shell_cmd_runner")
    @patch("pontos.release.helper.Path", spec=Path)
    @patch("pontos.release.helper.requests", spec=requests)
    @patch("pontos.release.helper.version", spec=version)
    @patch("pontos.changelog", spec=changelog)
    def test_fail_sign_on_invalid_get_response(
        self,
        _changelog_mock,
        _version_mock,
        _requests_mock,
        _path_mock,
        _shell_mock,
    ):
        _version_mock.main.return_value = (True, "MyProject.conf")
        _changelog_mock.update.return_value = ("updated", "changelog")

        fake_get = MagicMock(spec=requests.Response).return_value
        fake_get.status_code = 404
        fake_get.text = self.valid_gh_release_response
        _requests_mock.get.return_value = fake_get

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
    @patch("pontos.release.helper.Path", spec=Path)
    @patch("pontos.release.helper.requests", spec=requests)
    @patch("pontos.release.helper.version", spec=version)
    @patch("pontos.changelog", spec=changelog)
    def test_fail_sign_on_upload_fail(
        self,
        _changelog_mock,
        _version_mock,
        _requests_mock,
        _path_mock,
        _shell_mock,
    ):
        _version_mock.main.return_value = (True, "MyProject.conf")
        _changelog_mock.update.return_value = ("updated", "changelog")

        fake_get = MagicMock(spec=requests.Response).return_value
        fake_get.status_code = 200
        fake_get.text = self.valid_gh_release_response
        fake_post = MagicMock(spec=requests.Response).return_value
        fake_post.status_code = 500
        fake_post.text = self.valid_gh_release_response
        _requests_mock.get.return_value = fake_get
        _requests_mock.post.return_value = fake_post

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
    @patch("pontos.release.helper.Path", spec=Path)
    @patch("pontos.release.helper.requests", spec=requests)
    @patch("pontos.release.sign.requests", spec=requests)
    #@patch("pontos.release.helper.version", spec=version)
    @patch("pontos.changelog", spec=changelog)
    def test_successfully_sign(
        self,
        _changelog_mock,
     #   _version_mock,
        _sign_requests_mock,
        _requests_mock,
        _path_mock,
        _shell_mock,
    ):
      #  _version_mock.main.return_value = (True, "MyProject.conf")
        _changelog_mock.update.return_value = ("updated", "changelog")

        fake_get = MagicMock(spec=requests.Response).return_value
        fake_get.status_code = 200
        fake_get.text = self.valid_gh_release_response
        fake_post = MagicMock(spec=requests.Response).return_value
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        _sign_requests_mock.get.return_value = fake_get
        _requests_mock.get.return_value = fake_get
        _requests_mock.post.return_value = fake_post

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
