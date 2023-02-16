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

from pathlib import Path

from pontos.github.api.contents import GitHubAsyncRESTContent
from tests.github.api import GitHubAsyncRESTTestCase, create_response

here = Path(__file__).parent


class GitHubAsyncRESTContentTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTContent

    async def test_path_exists(self):
        response = create_response(is_success=True)
        self.client.get.return_value = response

        self.assertTrue(await self.api.path_exists("foo/bar", "a/file.txt"))

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/contents/a/file.txt", params={}
        )

    async def test_path_exists_with_branch(self):
        response = create_response(is_success=True)
        self.client.get.return_value = response

        self.assertTrue(
            await self.api.path_exists("foo/bar", "a/file.txt", branch="baz")
        )

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/contents/a/file.txt", params={"ref": "baz"}
        )

    async def test_path_not_exists(self):
        response = create_response(is_success=False)
        self.client.get.return_value = response

        self.assertFalse(await self.api.path_exists("foo/bar", "a/file.txt"))

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/contents/a/file.txt", params={}
        )
