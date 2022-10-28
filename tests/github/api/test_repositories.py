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

from unittest.mock import MagicMock

import httpx

from pontos.github.api.repositories import (
    GitHubAsyncRESTRepositories,
    GitIgnoreTemplate,
    LicenseType,
    MergeCommitMessage,
    MergeCommitTitle,
    SquashMergeCommitMessage,
    SquashMergeCommitTitle,
)
from tests.github.api import GitHubAsyncRESTTestCase, create_response


class GitHubAsyncRESTRepositoriesTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTRepositories

    async def test_get(self):
        response = create_response()
        self.client.get.return_value = response

        await self.api.get("foo/bar")

        self.client.get.assert_awaited_once_with("/repos/foo/bar")

    async def test_get_failure(self):
        response = create_response()
        self.client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.get("foo/bar")

        self.client.get.assert_awaited_once_with("/repos/foo/bar")

    async def test_delete(self):
        response = create_response()
        self.client.delete.return_value = response

        await self.api.delete("foo/bar")

        self.client.delete.assert_awaited_once_with("/repos/foo/bar")

    async def test_delete_failure(self):
        response = create_response()
        self.client.delete.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.delete("foo/bar")

        self.client.delete.assert_awaited_once_with("/repos/foo/bar")

    async def test_create_with_defaults(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.create("foo", "bar")

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/repos",
            data={
                "name": "bar",
                "private": False,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True,
                "is_template": False,
                "has_downloads": True,
                "auto_init": False,
                "allow_squash_merge": True,
                "allow_merge_commit": True,
                "allow_rebase_merge": True,
                "allow_auto_merge": False,
                "delete_branch_on_merge": False,
            },
        )

    async def test_create(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.create(
            "foo",
            "bar",
            private=True,
            has_issues=False,
            has_projects=False,
            has_wiki=False,
            is_template=True,
            team_id="123",
            has_downloads=False,
            auto_init=True,
            gitignore_template=GitIgnoreTemplate.PYTHON,
            license_template=LicenseType.MIT,
            allow_squash_merge=False,
            allow_merge_commit=False,
            allow_rebase_merge=False,
            allow_auto_merge=True,
            delete_branch_on_merge=True,
            squash_merge_commit_title=SquashMergeCommitTitle.COMMIT_OR_PR_TITLE,
            squash_merge_commit_message=SquashMergeCommitMessage.PR_BODY,
            merge_commit_title=MergeCommitTitle.MERGE_MESSAGE,
            merge_commit_message=MergeCommitMessage.PR_BODY,
        )

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/repos",
            data={
                "name": "bar",
                "private": True,
                "has_issues": False,
                "has_projects": False,
                "has_wiki": False,
                "is_template": True,
                "team_id": "123",
                "has_downloads": False,
                "auto_init": True,
                "license_template": "mit",
                "gitignore_template": "Python",
                "allow_squash_merge": False,
                "allow_merge_commit": False,
                "allow_rebase_merge": False,
                "allow_auto_merge": True,
                "delete_branch_on_merge": True,
                "squash_merge_commit_title": "COMMIT_OR_PR_TITLE",
                "squash_merge_commit_message": "PR_BODY",
                "merge_commit_title": "MERGE_MESSAGE",
                "merge_commit_message": "PR_BODY",
            },
        )

    async def test_archive(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.archive("foo/bar")

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar", data={"archived": True}
        )

    async def test_archive_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.archive("foo/bar")

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar", data={"archived": True}
        )

    async def test_update(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.update(
            "foo/bar",
            name="baz",
            description="A new Baz",
            homepage="http://baz.com",
            private=True,
            has_issues=False,
            has_projects=False,
            has_wiki=False,
            is_template=True,
            allow_squash_merge=False,
            allow_merge_commit=False,
            allow_rebase_merge=False,
            allow_auto_merge=True,
            allow_update_branch=True,
            delete_branch_on_merge=True,
            squash_merge_commit_title=SquashMergeCommitTitle.PR_TITLE,
            squash_merge_commit_message=SquashMergeCommitMessage.PR_BODY,
            merge_commit_title=MergeCommitTitle.PR_TITLE,
            merge_commit_message=MergeCommitMessage.PR_BODY,
            allow_forking=True,
            web_commit_signoff_required=True,
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar",
            data={
                "name": "baz",
                "description": "A new Baz",
                "homepage": "http://baz.com",
                "private": True,
                "has_issues": False,
                "has_projects": False,
                "has_wiki": False,
                "is_template": True,
                "allow_squash_merge": False,
                "allow_merge_commit": False,
                "allow_rebase_merge": False,
                "allow_auto_merge": True,
                "allow_update_branch": True,
                "delete_branch_on_merge": True,
                "squash_merge_commit_title": "PR_TITLE",
                "squash_merge_commit_message": "PR_BODY",
                "merge_commit_title": "PR_TITLE",
                "merge_commit_message": "PR_BODY",
                "allow_forking": True,
                "web_commit_signoff_required": True,
            },
        )

    async def test_update_with_defaults(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.update("foo/bar")

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar",
            data={
                "private": False,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True,
                "is_template": False,
                "allow_squash_merge": True,
                "allow_merge_commit": True,
                "allow_rebase_merge": True,
                "allow_auto_merge": False,
                "allow_update_branch": False,
                "delete_branch_on_merge": False,
                "allow_forking": False,
                "web_commit_signoff_required": False,
            },
        )

    async def test_update_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.update("foo/bar")

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar",
            data={
                "private": False,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True,
                "is_template": False,
                "allow_squash_merge": True,
                "allow_merge_commit": True,
                "allow_rebase_merge": True,
                "allow_auto_merge": False,
                "allow_update_branch": False,
                "delete_branch_on_merge": False,
                "allow_forking": False,
                "web_commit_signoff_required": False,
            },
        )
