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

import httpx

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.helper import JSON


class GitHubAsyncRESTBranches(GitHubAsyncREST):
    async def exists(self, repo: str, branch: str) -> bool:
        """
        Check if a single branch in a repository exists

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Branch name to check
        """
        api = f"/repos/{repo}/branches/{branch}"
        response = await self._client.get(api)
        return response.is_success

    async def delete(self, repo: str, branch: str):
        """
        Delete a branch on GitHub

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Branch to be deleted

        Raises:
            HTTPStatusError if the request was invalid
        """
        api = f"/repos/{repo}/git/refs/{branch}"
        response = await self._client.delete(api)
        response.raise_for_status()

    async def protection_rules(self, repo: str, branch: str) -> JSON:
        """
        Get branch protection rules for a specific repository
        branch

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Get protection rules for this branch

        Raises:
            HTTPStatusError if the request was invalid
        """
        api = f"/repos/{repo}/branches/{branch}/protection"
        response = await self._client.get(api)
        response.raise_for_status()
        return response.json()


class GitHubRESTBranchMixin:
    def branch_exists(self, repo: str, branch: str) -> bool:
        """
        Check if a single branch in a repository exists

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Branch name to check
        """
        api = f"/repos/{repo}/branches/{branch}"
        response: httpx.Response = self._request(api)
        return response.is_success

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
        response: httpx.Response = self._request(api, request=httpx.delete)
        response.raise_for_status()

    def branch_protection_rules(self, repo: str, branch: str):
        """
        Get branch protection rules for a specific repository
        branch

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Get protection rules for this branch

        Raises:
            HTTPError if the request was invalid
        """
        api = f"/repos/{repo}/branches/{branch}/protection"
        response: httpx.Response = self._request(api)
        return response.json()
