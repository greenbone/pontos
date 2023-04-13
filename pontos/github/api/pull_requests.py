# Copyright (C) 2022 Greenbone AG
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

from collections import defaultdict
from pathlib import Path
from typing import AsyncIterator, Dict, Iterable, List, Optional, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.helper import JSON_OBJECT
from pontos.github.models.base import FileStatus
from pontos.github.models.pull_request import (
    Comment,
    PullRequest,
    PullRequestCommit,
)


class GitHubAsyncRESTPullRequests(GitHubAsyncREST):
    async def exists(self, repo: str, pull_request: Union[int, str]) -> bool:
        """
        Check if a single branch in a repository exists

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number to check

        Returns:
            True if the pull requests exists

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    exists = await api.pull_request.exists("foo/bar", 123)
        """
        api = f"/repos/{repo}/pulls/{pull_request}"
        response = await self._client.get(api)
        return response.is_success

    async def get(
        self, repo: str, pull_request: Union[int, str]
    ) -> PullRequest:
        """
        Get information about a pull request

        https://docs.github.com/en/rest/pulls/pulls#get-a-pull-request

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number

        Returns:
            Information about the pull request

        Raises:
            httpx.HTTPStatusError: If the request was invalid

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    pr = await api.pull_requests.get("foo/bar", 123)
                    print(pr)
        """
        api = f"/repos/{repo}/pulls/{pull_request}"
        response = await self._client.get(api)
        response.raise_for_status()
        return PullRequest.from_dict(response.json())

    async def commits(
        self, repo: str, pull_request: Union[int, str]
    ) -> AsyncIterator[PullRequestCommit]:
        """
        Get all commit information of a pull request

        https://docs.github.com/en/rest/pulls/pulls#list-commits-on-a-pull-request

        Hint: At maximum GitHub allows to receive 250 commits of a pull request.

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number

        Returns:
            An async iterator yielding pull request commits

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for commit in api.pull_requests.commits(
                        "foo/bar", 123
                    ):
                        print(commit)
        """
        # per default github only shows 35 commits and at max it is only
        # possible to receive 100
        params = {"per_page": "100"}
        api = f"/repos/{repo}/pulls/{pull_request}/commits"

        async for response in self._client.get_all(api, params=params):
            for commit in response.json():
                yield PullRequestCommit.from_dict(commit)

    async def create(
        self,
        repo: str,
        *,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str,
    ) -> PullRequest:
        """
        Create a new Pull Request on GitHub

        https://docs.github.com/en/rest/pulls/pulls#create-a-pull-request

        Args:
            repo: GitHub repository (owner/name) to use
            head_branch: Branch to create a pull request from
            base_branch: Branch as target for the pull request
            title: Title for the pull request
            body: Description for the pull request. Can be formatted in Markdown

        Raises:
            httpx.HTTPStatusError if the request was invalid

        Returns:
            A new pull request

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    pr = await api.pull_requests.create(
                        "foo/bar",
                        head_branch="a-new-feature",
                        base_branch="main",
                        title="A new Feature is ready",
                        body="Created a new feature",
                    )
        """
        api = f"/repos/{repo}/pulls"
        data: JSON_OBJECT = {
            "head": head_branch,
            "base": base_branch,
            "title": title,
            "body": body.replace("\\n", "\n"),
        }
        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return PullRequest.from_dict(response.json())

    async def update(
        self,
        repo: str,
        pull_request: Union[int, str],
        *,
        base_branch: Optional[str] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
    ) -> PullRequest:
        """
        Update a Pull Request on GitHub

        https://docs.github.com/en/rest/pulls/pulls#update-a-pull-request

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number
            base_branch: Branch as target for the pull request. Leave empty for
                keeping the current one.
            title: Title for the pull request. Leave empty for keeping the
                current one.
            body: Description for the pull request. Can be formatted in
                Markdown. Leave empty for keeping the current one.
        Raises:
            httpx.HTTPStatusError if the request was invalid

        Returns:
            Updated pull request

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    pr = await api.pull_requests.update(
                        "foo/bar",
                        123,
                        title="Another new Feature",
                    )
        """
        api = f"/repos/{repo}/pulls/{pull_request}"

        data: JSON_OBJECT = {}
        if base_branch:
            data["base"] = base_branch
        if title:
            data["title"] = title
        if body:
            data["body"] = body.replace("\\n", "\n")

        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return PullRequest.from_dict(response.json())

    async def add_comment(
        self, repo: str, pull_request: Union[int, str], comment: str
    ) -> Comment:
        """
        Add a comment to a pull request on GitHub

        https://docs.github.com/en/rest/issues/comments#create-an-issue-comment

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number where to add a comment
            comment: The actual comment message. Can be formatted in Markdown.

        Raises:
            httpx.HTTPStatusError if the request was invalid

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    await api.pull_requests.add_comment(
                        "foo/bar",
                        123,
                        "A new comment for the pull request",
                    )
        """
        api = f"/repos/{repo}/issues/{pull_request}/comments"
        data: JSON_OBJECT = {"body": comment}
        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return Comment.from_dict(response.json())

    async def update_comment(
        self, repo: str, comment_id: Union[str, int], comment: str
    ) -> Comment:
        """
        Update a comment to a pull request on GitHub

        https://docs.github.com/en/rest/issues/comments#update-an-issue-comment

        Args:
            repo: GitHub repository (owner/name) to use
            comment_id: The unique identifier of the comment
            comment: The actual comment message. Can be formatted in Markdown.

        Raises:
            httpx.HTTPStatusError if the request was invalid

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    await api.pull_requests.update_comment(
                        "foo/bar",
                        123,
                        "A new comment for the pull request",
                    )
        """
        api = f"/repos/{repo}/issues/comments/{comment_id}"
        data: JSON_OBJECT = {"body": comment}
        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return Comment.from_dict(response.json())

    async def comments(
        self, repo: str, pull_request: Union[int, str]
    ) -> AsyncIterator[Comment]:
        """
        Get all comments of a pull request on GitHub

        https://docs.github.com/en/rest/issues/comments#list-issue-comments

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number where to add a comment

        Raises:
            httpx.HTTPStatusError if the request was invalid

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for comment in api.pull_requests.comments(
                        "foo/bar",
                        123,
                    ):
                        print(comment)
        """
        params = {"per_page": "100"}
        api = f"/repos/{repo}/issues/{pull_request}/comments"

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for comment in response.json():
                yield Comment.from_dict(comment)

    async def files(
        self,
        repo: str,
        pull_request: Union[int, str],
        *,
        status_list: Optional[Iterable[FileStatus]] = None,
    ) -> Dict[FileStatus, Iterable[Path]]:
        """
        Get files of a pull request

        https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files

        Hint: At maximum GitHub allows to receive 3000 files of a commit.

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number
            status_list: Optional iterable of status change types that should be
                included in the response

        Returns:
            Information about the files in the pull request as a dict

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi
                from pontos.github.models import FileStatus

                async with GitHubAsyncRESTApi(token) as api:
                    status = await api.pull_requests.files("foo/bar", 123)
                    # list changed files
                    print(status[FileStatus.MODIFIED])
        """
        # per default github only shows 35 files per page and at max it is only
        # possible to receive 100
        params = {"per_page": "100"}
        api = f"/repos/{repo}/pulls/{pull_request}/files"
        file_dict: Dict[FileStatus, List[Path]] = defaultdict(list)

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for f in response.json():
                try:
                    status = FileStatus(f["status"])
                except ValueError:
                    # unknown status
                    continue

                if not status_list or status in status_list:
                    file_dict[status].append(Path(f["filename"]))

        return file_dict  # type: ignore
