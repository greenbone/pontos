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


from typing import Optional

import httpx

from pontos.github.api.client import GitHubAsyncREST


class GitHubAsyncRESTContent(GitHubAsyncREST):
    async def path_exists(
        self, repo: str, path: str, *, branch: Optional[str] = None
    ) -> bool:
        """
        Check if a path (file or directory) exists in a branch of a repository

        Args:
            repo: GitHub repository (owner/name) to use
            path: to the file/directory in question
            branch: Branch to check, defaults to default branch (:

        Returns:
            True if existing, False else
        """
        api = f"/repos/{repo}/contents/{path}"
        params = {}
        if branch:
            params["ref"] = branch

        response = await self._client.get(api, params=params)
        return response.is_success


class GitHubRESTContentMixin:
    def path_exists(
        self, repo: str, path: str, *, branch: Optional[str] = None
    ) -> bool:
        """
        Check if a path (file or directory) exists in a branch of a repository

        Args:
            repo: GitHub repository (owner/name) to use
            path: to the file/directory in question
            branch: Branch to check, defaults to default branch (:

        Returns:
            True if existing, False else
        """
        api = f"/repos/{repo}/contents/{path}"
        params = {}
        if branch:
            params["ref"] = branch
        response: httpx.Response = self._request(api, params=params)
        return response.is_success
