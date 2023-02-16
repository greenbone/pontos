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

from typing import AsyncContextManager, AsyncIterator, Optional, Union

from pontos.github.api.client import GitHubAsyncREST, Params
from pontos.github.models.artifact import Artifact
from pontos.helper import AsyncDownloadProgressIterable, download_async


class GitHubAsyncRESTArtifacts(GitHubAsyncREST):
    def _get_paged_artifacts(
        self, api, *, params: Optional[Params] = None
    ) -> AsyncIterator[Artifact]:
        return self._get_paged_items(api, "artifacts", Artifact, params=params)

    def get_all(self, repo: str) -> AsyncIterator[Artifact]:
        """
        List all artifacts of a repository

        https://docs.github.com/en/rest/actions/artifacts#list-artifacts-for-a-repository

        Args:
            repo: GitHub repository (owner/name) to use

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the artifacts in the repository as a dict
        """
        api = f"/repos/{repo}/actions/artifacts"
        return self._get_paged_artifacts(api)

    async def get(self, repo: str, artifact: Union[str, int]) -> Artifact:
        """
        Get a single artifact of a repository

        https://docs.github.com/en/rest/actions/artifacts#get-an-artifact

        Args:
            repo: GitHub repository (owner/name) to use
            artifact: ID of the artifact

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the artifact as a dict
        """
        api = f"/repos/{repo}/actions/artifacts/{artifact}"
        response = await self._client.get(api)
        response.raise_for_status()
        return Artifact.from_dict(response.json())

    def get_workflow_run_artifacts(
        self, repo: str, run: Union[str, int]
    ) -> AsyncIterator[Artifact]:
        """
        List all artifacts for a workflow run

        https://docs.github.com/en/rest/actions/artifacts#list-workflow-run-artifacts

        Args:
            repo: GitHub repository (owner/name) to use
            run: The unique identifier of the workflow run

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the artifacts in the workflow as a dict
        """
        api = f"/repos/{repo}/actions/runs/{run}/artifacts"
        return self._get_paged_artifacts(api)

    async def delete(self, repo: str, artifact: Union[str, int]):
        """
        Delete an artifact of a repository

        https://docs.github.com/en/rest/actions/artifacts#delete-an-artifact

        Args:
            repo: GitHub repository (owner/name) to use
            artifact: ID of the artifact

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.
        """
        api = f"/repos/{repo}/actions/artifacts/{artifact}"
        response = await self._client.delete(api)
        response.raise_for_status()

    def download(
        self, repo: str, artifact: Union[str, int]
    ) -> AsyncContextManager[AsyncDownloadProgressIterable[bytes]]:
        """
        Download a repository artifact zip file

        https://docs.github.com/en/rest/actions/artifacts#download-an-artifact

        Args:
            repo: GitHub repository (owner/name) to use
            artifact: ID of the artifact

        Raises:
            HTTPStatusError if the request was invalid

        Example:
            .. code-block:: python

            api = GitHubAsyncRESTApi("...")

            print("Downloading", end="")

            with Path("foo.baz").open("wb") as f:
                async with api.download("org/repo", "123") as download:
                    async for content, progress in download:
                        f.write(content)
                        print(".", end="")
        """
        api = f"/repos/{repo}/actions/artifacts/{artifact}/zip"
        return download_async(self._client.stream(api))
