# Copyright (C) 2022 Greenbone Networks GmbH
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
from pathlib import Path
from unittest.mock import MagicMock, patch

from pontos.github.api import GitHubRESTApi
from tests.github.api import default_request

here = Path(__file__).parent


class GitHubContentTestCase(unittest.TestCase):
    @patch("pontos.github.api.api.httpx.get")
    def test_path_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.ok = True
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.path_exits(repo="foo/bar", path="baz", branch="main")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/contents/baz",
            params={
                "ref": "main",
            },
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
        self.assertTrue(exists)

    @patch("pontos.github.api.api.httpx.get")
    def test_path_not_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.is_success = False
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.path_exits(repo="foo/bar", path="baz", branch="main")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/contents/baz",
            params={
                "ref": "main",
            },
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
        self.assertFalse(exists)
