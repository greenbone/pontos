# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


from typing import Optional

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

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    exists = await api.contents.path_exists(
                        "foo/bar", "src/utils.py"
                    )
        """
        api = f"/repos/{repo}/contents/{path}"
        params = {}
        if branch:
            params["ref"] = branch

        response = await self._client.get(api, params=params)
        return response.is_success
