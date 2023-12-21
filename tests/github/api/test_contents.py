# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

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
