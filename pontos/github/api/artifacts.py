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
from typing import ContextManager, Iterable, Union

import httpx

from pontos.github.api.helper import JSON_OBJECT
from pontos.helper import DownloadProgressIterable, download


class GitHubRESTArtifactsMixin:
    def get_repository_artifacts(self, repo: str) -> Iterable[JSON_OBJECT]:
        """
        List all artifacts of a repository

        Args:
            repo: GitHub repository (owner/name) to use

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the artifacts in the repository as a dict
        """
        api = f"/repos/{repo}/actions/artifacts"
        return self._get_paged_items(api, "artifacts")

    def get_repository_artifact(self, repo: str, artifact: str) -> JSON_OBJECT:
        """
        Get a single artifact of a repository

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
        response: httpx.Response = self._request(api, request=httpx.get)
        response.raise_for_status()
        return response.json()

    def download_repository_artifact(
        self, repo: str, artifact: str, destination: Union[Path, str]
    ) -> ContextManager[DownloadProgressIterable]:
        """
        Download a repository artifact zip file

        Args:
            repo: GitHub repository (owner/name) to use
            artifact: ID of the artifact
            destination: A path where to store the downloaded file

        Raises:
            HTTPError if the request was invalid

        Example:
            .. code-block:: python

            api = GitHubRESTApi("...")

            print("Downloading", end="")

            with api.download_repository_artifact(
                "org/repo", "123", "/tmp/artifact.zip"
            ) as progress_iterator:
                for progress in progress_iterator:
                    print(".", end="")
        """
        api = f"{self.url}/repos/{repo}/actions/artifacts/{artifact}/zip"
        return download(api, destination, headers=self._request_headers())

    def get_workflow_run_artifacts(
        self, repo: str, run: str
    ) -> Iterable[JSON_OBJECT]:
        """
        List all artifacts for a workflow run

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
        return self._get_paged_items(api, "artifacts")

    def delete_repository_artifact(self, repo: str, artifact: str):
        """
        Delete an artifact of a repository

        Args:
            repo: GitHub repository (owner/name) to use
            artifact: ID of the artifact

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.
        """
        api = f"/repos/{repo}/actions/artifacts/{artifact}"
        response: httpx.Response = self._request(api, request=httpx.delete)
        response.raise_for_status()
