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

# pylint: disable=no-member

from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from pontos.github.api import FileStatus
from pontos.github.cmds import (
    create_pull_request,
    create_release,
    create_tag,
    file_status,
    labels,
    repos,
    update_pull_request,
)
from pontos.github.models.organization import RepositoryType
from pontos.testing import temp_file
from tests import AsyncIteratorMock, IsolatedAsyncioTestCase

here = Path(__file__).parent


class TestCmds(IsolatedAsyncioTestCase):
    @patch("pontos.github.api.api.GitHubAsyncRESTPullRequests", spec=True)
    async def test_file_status(self, api_mock):
        terminal = MagicMock()
        api_mock.return_value.exists.return_value = True
        api_mock.return_value.files.return_value = {
            FileStatus.ADDED: [Path("tests/github/foo/bar")],
            FileStatus.MODIFIED: [
                Path("tests/github/bar/baz"),
                Path("tests/github/baz/boo"),
            ],
        }

        with temp_file(name="some.file") as test_file, test_file.open(
            "w", encoding="utf8"
        ) as output:
            args = Namespace(
                repo="foo/bar",
                pull_request=8,
                output=output,
                status=[FileStatus.ADDED, FileStatus.MODIFIED],
                token="GITHUB_TOKEN",
            )

            await file_status(terminal, args)

            api_mock.return_value.exists.assert_awaited_once_with(
                repo="foo/bar", pull_request=8
            )
            api_mock.return_value.files.assert_awaited_once_with(
                repo="foo/bar",
                pull_request=8,
                status_list=[FileStatus.ADDED, FileStatus.MODIFIED],
            )

            output.flush()

            content = test_file.read_text(encoding="utf-8")
            self.assertEqual(
                content, f"{here}/foo/bar\n{here}/bar/baz\n{here}/baz/boo\n"
            )

    @patch("pontos.github.api.api.GitHubAsyncRESTReleases", spec=True)
    async def test_create_release_no_tag(self, api_mock):
        terminal = MagicMock()
        api_mock.return_value.exists.return_value = True

        args = Namespace(
            repo="foo/bar",
            tag="test_tag",
            name="test_release",
            body=None,
            target_commitish=None,
            draft=False,
            prerelease=False,
            token="GITHUB_TOKEN",
        )

        with self.assertRaises(SystemExit) as syse:
            await create_release(terminal, args)

        self.assertEqual(syse.exception.code, 1)

        api_mock.return_value.exists.assert_awaited_once_with(
            repo="foo/bar", tag="test_tag"
        )

    @patch("pontos.github.api.api.GitHubAsyncRESTReleases", spec=True)
    async def test_create_release(self, api_mock):
        terminal = MagicMock()
        api_mock.return_value.exists.return_value = False
        api_mock.return_value.create.return_value = True

        args = Namespace(
            repo="foo/bar",
            tag="test_tag",
            name="test_release",
            body=None,
            target_commitish=None,
            draft=False,
            prerelease=False,
            token="GITHUB_TOKEN",
        )

        await create_release(terminal, args)

        api_mock.return_value.exists.assert_awaited_once_with(
            repo="foo/bar", tag="test_tag"
        )
        api_mock.return_value.create.assert_awaited_once_with(
            repo="foo/bar",
            tag="test_tag",
            body=None,
            name="test_release",
            target_commitish=None,
            draft=False,
            prerelease=False,
        )

    @patch("pontos.github.api.api.GitHubAsyncRESTTags", spec=True)
    async def test_create_tag(self, api_mock):
        terminal = MagicMock()
        api_mock.return_value.create.return_value = MagicMock(sha="123")
        api_mock.return_value.create_tag_reference.return_value = True

        args = Namespace(
            repo="foo/bar",
            tag="test_tag",
            name="test_release",
            message="test msg",
            git_object="commit",
            git_object_type=None,
            email="test@test.test",
            date=None,
            token="GITHUB_TOKEN",
        )

        await create_tag(terminal, args)

        api_mock.return_value.create.assert_awaited_once_with(
            repo="foo/bar",
            tag="test_tag",
            message="test msg",
            git_object="commit",
            name="test_release",
            email="test@test.test",
            git_object_type=None,
            date=None,
        )
        api_mock.return_value.create_tag_reference.assert_awaited_once_with(
            repo="foo/bar", tag="test_tag", sha="123"
        )

    @patch("pontos.github.api.api.GitHubAsyncRESTBranches", spec=True)
    @patch("pontos.github.api.api.GitHubAsyncRESTPullRequests", spec=True)
    async def test_create_pull_request(
        self,
        pulls_api_mock,
        branches_api_mock,
    ):
        terminal = MagicMock()
        branches_api_mock.return_value.exists.return_value = [False, False]
        pulls_api_mock.return_value.create.return_value = True

        args = Namespace(
            repo="foo/bar",
            head="some-branch",
            target="main",
            title="foo",
            body="foo bar",
            token="GITHUB_TOKEN",
        )

        await create_pull_request(terminal, args)

        branches_api_mock.return_value.exists.assert_has_awaits(
            [
                call(repo="foo/bar", branch="some-branch"),
                call(repo="foo/bar", branch="main"),
            ]
        )

        pulls_api_mock.return_value.create.assert_awaited_once_with(
            repo="foo/bar",
            head_branch="some-branch",
            base_branch="main",
            title="foo",
            body="foo bar",
        )

    @patch("pontos.github.api.api.GitHubAsyncRESTBranches", spec=True)
    @patch("pontos.github.api.api.GitHubAsyncRESTPullRequests", spec=True)
    async def test_update_pull_request(
        self,
        pulls_api_mock,
        branches_api_mock,
    ):
        terminal = MagicMock()
        branches_api_mock.return_value.exists.return_value = True
        pulls_api_mock.return_value.create.return_value = True

        args = Namespace(
            repo="foo/bar",
            target="main",
            pull_request=9,
            title="foo",
            body="foo bar",
            token="GITHUB_TOKEN",
        )

        await update_pull_request(terminal, args)

        branches_api_mock.return_value.exists.assert_awaited_once_with(
            repo="foo/bar", branch="main"
        )

        pulls_api_mock.return_value.update.assert_awaited_once_with(
            repo="foo/bar",
            pull_request=9,
            base_branch="main",
            title="foo",
            body="foo bar",
        )

    @patch("pontos.github.api.api.GitHubAsyncRESTPullRequests", spec=True)
    @patch("pontos.github.api.api.GitHubAsyncRESTLabels", spec=True)
    async def test_labels(
        self,
        labels_api_mock,
        pulls_api_mock,
    ):
        terminal = MagicMock()
        pulls_api_mock.return_value.exists.return_value = True
        labels_api_mock.return_value.get_all.return_value = AsyncIteratorMock(
            ["foo", "bar"]
        )

        args = Namespace(
            repo="foo/bar",
            issue=9,
            labels=["baz"],
            token="GITHUB_TOKEN",
        )

        await labels(terminal, args)

        pulls_api_mock.return_value.exists.assert_awaited_once_with(
            repo="foo/bar", pull_request=9
        )

        labels_api_mock.return_value.get_all.assert_called_once_with(
            repo="foo/bar",
            issue=9,
        )

        labels_api_mock.return_value.set_all.assert_awaited_once_with(
            repo="foo/bar", issue=9, labels=["foo", "bar", "baz"]
        )

    @patch("pontos.github.api.api.GitHubAsyncRESTOrganizations", spec=True)
    async def test_repos(self, api_mock):
        terminal = MagicMock()
        api_mock.return_value.exists.return_value = True
        api_mock.return_value.get_repositories.return_value = AsyncIteratorMock(
            ["repo1", "repo2"]
        )

        args = Namespace(
            orga="foo",
            repo="bar",
            path=None,
            type=RepositoryType.PUBLIC,
            token="GITHUB_TOKEN",
        )

        await repos(terminal, args)

        api_mock.return_value.exists.assert_awaited_once_with("foo")
        api_mock.return_value.get_repositories.assert_called_once_with(
            organization="foo", repository_type=RepositoryType.PUBLIC
        )
