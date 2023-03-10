# Copyright (C) 2020-2022 Greenbone AG
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

import unittest
from unittest.mock import patch

from pontos.git.git import Git
from pontos.version.helper import get_last_release_version
from pontos.version.version import Version


class GetLastReleaseVersionTestCase(unittest.TestCase):
    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_version(self, _git_interface_mock):
        git_interface = _git_interface_mock.return_value
        git_interface.list_tags.return_value = ["1", "2", "3.55"]
        self.assertEqual(get_last_release_version(), Version("3.55"))

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_no_release_version(self, _git_interface_mock):
        git_interface = _git_interface_mock.return_value
        git_interface.list_tags.return_value = []
        self.assertIsNone(get_last_release_version())

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_version_with_git_prefix(
        self, _git_interface_mock
    ):
        git_interface = _git_interface_mock.return_value
        git_interface.list_tags.return_value = ["v1", "v2", "v3.55"]
        self.assertEqual(get_last_release_version("v"), Version("3.55"))

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_version_ignore_pre_releases(
        self, _git_interface_mock
    ):
        git_interface = _git_interface_mock.return_value
        git_interface.list_tags.return_value = [
            "1",
            "2",
            "3.55a1",
            "3.56.dev1",
            "4.0.0rc1",
            "4.0.1b1",
        ]
        self.assertEqual(
            get_last_release_version(ignore_pre_releases=True), Version("2")
        )

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_version_no_non_pre_release(
        self, _git_interface_mock
    ):
        git_interface = _git_interface_mock.return_value
        git_interface.list_tags.return_value = [
            "3.55a1",
            "3.56.dev1",
            "4.0.0rc1",
            "4.0.1b1",
        ]
        self.assertIsNone(get_last_release_version(ignore_pre_releases=True))
