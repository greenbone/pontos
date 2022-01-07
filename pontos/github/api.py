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

from typing import Callable, Dict, Optional

import requests

DEFAULT_GITHUB_API_URL = "https://api.github.com"


class GitHubRESTApi:
    def __init__(
        self, token: str, url: Optional[str] = DEFAULT_GITHUB_API_URL
    ) -> None:
        self.token = token
        self.url = url

    def request(
        self,
        api: str,
        *,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, str]] = None,
        request: Optional[Callable] = None,
    ) -> requests.Response:
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        request = request or requests.get
        return request(
            f"{self.url}{api}", headers=headers, params=params, json=data
        )

    def branch_exists(self, repo: str, branch: str) -> bool:
        """
        Check if a single branch in a repository exists

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Branch name to check
        """
        api = f"/repos/{repo}/branches/{branch}"
        response = self.request(api)
        return response.ok

    def pull_request_commits(
        self, repo: str, pull_request: str
    ) -> Dict[str, str]:
        """
        Get all commit information of a pull request

        Hint: At maximum GitHub allows to receive 100 commits. If a pull request
        contains more then 100 commits only the first 100 are returned.

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number

        Returns:
            Information about the commits in the pull request as a dict
        """
        # per default github only shows 35 commits and at max it is only
        # possible to receive 100
        params = {"per_page": "100"}
        api = f"/repos/{repo}/pulls/{pull_request}/commits"
        response = self.request(api, params=params)
        return response.json()

    def create_pull_request(
        self,
        repo: str,
        *,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str,
    ):
        """
        Create a new Pull Request on GitHub

        Args:
            repo: GitHub repository (owner/name) to use
            head_branch: Branch to create a pull request from
            base_branch: Branch as as target for the pull
            title: Title for the pull request
            body: Description for the pull request. Can be formatted in Markdown

        Raises:
            HTTPError if the request was invalid
        """
        api = f"/repos/{repo}/pulls"
        data = {
            "head": head_branch,
            "base": base_branch,
            "title": title,
            "body": body,
        }
        response = self.request(api, data=data, request=requests.post)
        response.raise_for_status()

    def add_pull_request_comment(
        self, repo: str, pull_request: str, comment: str
    ):
        """
        Add a comment to a pull request on GitHub

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number where to add a comment
            comment: The actual comment message. Can be formatted in Markdown.

        Raises:
            HTTPError if the request was invalid
        """
        api = f"/repos/{repo}/issues/{pull_request}/comments"
        data = {"body": comment}
        response = self.request(api, data=data, request=requests.post)
        response.raise_for_status()

    def delete_branch(self, repo: str, branch: str):
        """
        Delete a branch on GitHub

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Branch to be deleted

        Raises:
            HTTPError if the request was invalid
        """
        api = f"/repos/{repo}/git/refs/{branch}"
        response = self.request(api, request=requests.delete)
        response.raise_for_status()
