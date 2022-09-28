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

# pylint: disable=too-many-lines

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pontos.github.api import GitHubRESTApi
from tests.github.api import default_request

here = Path(__file__).parent


class GitHubBranchTestCase(unittest.TestCase):
    @patch("pontos.github.api.api.httpx.get")
    def test_branch_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.ok = True
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.branch_exists("foo/bar", "main")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/branches/main",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
        self.assertTrue(exists)

    @patch("pontos.github.api.api.httpx.get")
    def test_branch_not_exists(self, requests_mock: MagicMock):
        response = MagicMock()
        response.is_success = False
        requests_mock.return_value = response

        api = GitHubRESTApi("12345")
        exists = api.branch_exists("foo/bar", "main")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/branches/main",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
        self.assertFalse(exists)

    @patch("pontos.github.api.api.httpx.delete")
    def test_delete_branch(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.delete_branch("foo/bar", "foo")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/git/refs/foo",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.get")
    def test_branch_protection_rules(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.branch_protection_rules(repo="foo/bar", branch="baz")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/branches/baz/protection",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
