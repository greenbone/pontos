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

from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import (
    Callable,
    ContextManager,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)

import httpx

from pontos.helper import DownloadProgressIterable, download

DEFAULT_GITHUB_API_URL = "https://api.github.com"


class FileStatus(Enum):
    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"
    RENAMED = "renamed"


def _get_next_url(response) -> Optional[str]:
    if response and response.links:
        try:
            return response.links["next"]["url"]
        except KeyError:
            pass

    return None


JSON = Dict[str, Union[str, bool, int]]


class GitHubRESTApi:
    def __init__(
        self,
        token: Optional[str] = None,
        url: Optional[str] = DEFAULT_GITHUB_API_URL,
    ) -> None:
        self.token = token
        self.url = url

    def _request_headers(
        self, *, content_type: Optional[str] = None
    ) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        if content_type:
            headers["Content-Type"] = content_type

        return headers

    def _request_internal(
        self,
        url: str,
        *,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, str]] = None,
        content: Optional[bytes] = None,
        request: Optional[Callable] = None,
        content_type: Optional[str] = None,
    ) -> httpx.Response:
        request = request or httpx.get
        headers = self._request_headers(content_type=content_type)
        kwargs = {}
        if data is not None:
            kwargs["json"] = data
        if content is not None:
            kwargs["content"] = content
        return request(
            url,
            headers=headers,
            params=params,
            follow_redirects=True,
            **kwargs,
        )

    def _request(
        self,
        api: str,
        *,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, str]] = None,
        request: Optional[Callable] = None,
    ) -> httpx.Response:
        return self._request_internal(
            f"{self.url}{api}", params=params, data=data, request=request
        )

    def _request_all(
        self,
        api: str,
        *,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, str]] = None,
        request: Optional[Callable] = None,
    ) -> Iterator[JSON]:
        response = self._request(api, params=params, data=data, request=request)

        yield from response.json()

        next_url = _get_next_url(response)

        while next_url:
            response = self._request_internal(
                next_url, params=params, data=data, request=request
            )

            yield from response.json()

            next_url = _get_next_url(response)

        return data

    def branch_exists(self, repo: str, branch: str) -> bool:
        """
        Check if a single branch in a repository exists

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Branch name to check
        """
        api = f"/repos/{repo}/branches/{branch}"
        response = self._request(api)
        return response.is_success

    def pull_request_exists(self, repo: str, pull_request: int) -> bool:
        """
        Check if a single branch in a repository exists

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number to check
        """
        api = f"/repos/{repo}/pulls/{pull_request}"
        response = self._request(api)
        return response.is_success

    def pull_request_commits(
        self, repo: str, pull_request: int
    ) -> Iterable[JSON]:
        """
        Get all commit information of a pull request

        Hint: At maximum GitHub allows to receive 250 commits of a pull request.

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
        return list(self._request_all(api, params=params))

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
            base_branch: Branch as target for the pull request
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
            "body": body.replace("\\n", "\n"),
        }
        response = self._request(api, data=data, request=httpx.post)
        response.raise_for_status()

    def update_pull_request(
        self,
        repo: str,
        pull_request: int,
        *,
        base_branch: Optional[str] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
    ):
        """
        Update a Pull Request on GitHub

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number
            base_branch: Branch as target for the pull request. Leave empty for
                keeping the current one.
            title: Title for the pull request. Leave empty for keeping the
                current one.
            body: Description for the pull request. Can be formatted in
                Markdown. Leave empty for keeping the current one.
        """
        api = f"/repos/{repo}/pulls/{pull_request}"

        data = {}
        if base_branch:
            data["base"] = base_branch
        if title:
            data["title"] = title
        if body:
            data["body"] = body.replace("\\n", "\n")

        response = self._request(api, data=data, request=httpx.post)
        response.raise_for_status()

    def add_pull_request_comment(
        self, repo: str, pull_request: int, comment: str
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
        response = self._request(api, data=data, request=httpx.post)
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
        response = self._request(api, request=httpx.delete)
        response.raise_for_status()

    def create_release(
        self,
        repo: str,
        tag: str,
        *,
        body: Optional[str] = None,
        name: Optional[str] = None,
        target_commitish: Optional[str] = None,
        draft: Optional[bool] = False,
        prerelease: Optional[bool] = False,
    ):
        """
        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release
            body: Content of the changelog for the release
            name: name of the release, e.g. 'pontos 1.0.0'
            target_commitish: Only needed when tag is not there yet
            draft: If the release is a draft. False by default.
            prerelease: If the release is a pre release. False by default.
        """
        data = {
            "tag_name": tag,
            "draft": draft,
            "prerelease": prerelease,
        }
        if name is not None:
            data["name"] = name
        if body is not None:
            data["body"] = body
        if target_commitish is not None:
            data["target_commitish"] = target_commitish

        api = f"/repos/{repo}/releases"
        response = self._request(api, data=data, request=httpx.post)
        response.raise_for_status()

    def release_exists(self, repo: str, tag: str) -> bool:
        """
        Check wether a GitHub release exists by tag

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release

        Returns:
            True if the release exists
        """
        api = f"/repos/{repo}/releases/tags/{tag}"
        response = self._request(api)
        return response.is_success

    def release(self, repo: str, tag: str) -> JSON:
        """
        Get data of a GitHub release by tag

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release

        Raises:
            HTTPError if the request was invalid
        """
        api = f"/repos/{repo}/releases/tags/{tag}"
        response = self._request(api)
        response.raise_for_status()
        return response.json()

    def download_release_tarball(
        self, repo: str, tag: str, destination: Path
    ) -> ContextManager[DownloadProgressIterable]:
        """
        Download a release tarball (tar.gz) file

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release
            destination: A path where to store the downloaded file

        Raises:
            HTTPError if the request was invalid
        """
        api = f"https://github.com/{repo}/archive/refs/tags/{tag}.tar.gz"
        return download(api, destination)

    def download_release_zip(
        self, repo: str, tag: str, destination: Path
    ) -> ContextManager[DownloadProgressIterable]:
        """
        Download a release zip file

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release
            destination: A path where to store the downloaded file

        Raises:
            HTTPError if the request was invalid
        """
        api = f"https://github.com/{repo}/archive/refs/tags/{tag}.zip"
        return download(api, destination)

    def download_release_assets(
        self,
        repo: str,
        tag: str,
    ) -> Iterator[DownloadProgressIterable]:
        """
        Download release assets

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release

        Raises:
            HTTPError if the request was invalid
        """
        release_json = self.release(repo, tag)
        assets_url = release_json.get("assets_url")
        if not assets_url:
            return

        response = self._request_internal(assets_url)
        response.raise_for_status()
        assets_json = response.json()
        for asset_json in assets_json:
            asset_url: str = asset_json.get("browser_download_url", "")
            name: str = asset_json.get("name", "")
            if name.endswith(".zip") or name.endswith(".tar.gz"):
                with download(
                    asset_url,
                    Path(name),
                ) as progress:
                    yield progress

    def upload_release_assets(
        self,
        repo: str,
        tag: str,
        files: Iterable[Union[Path, Tuple[Path, str]]],
    ) -> Iterator[Path]:
        # pylint: disable=line-too-long
        """
        Upload release assets one after another

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release
            files: An iterable of file paths or an iterable of tuples
                containing a file path and content types to upload as an asset

        Returns:
            yields each file after its upload is finished

        Raises:
            HTTPError if an upload request was invalid

        Examples:
            >>> files = (Path("foo.txt"), Path("bar.txt"),)
            >>> for uploaded_file in git.upload_release_assets("foo/bar", "1.2.3", files):
            >>>    print(f"Uploaded: {uploaded_file}")

            >>> files = [(Path("foo.txt"), "text/ascii"), (Path("bar.pdf"), "application/pdf")]
            >>> for uploaded_file in git.upload_release_assets("foo/bar", "1.2.3", files):
            >>>    print(f"Uploaded: {uploaded_file}")
        """
        github_json = self.release(repo, tag)
        asset_url = github_json["upload_url"].replace("{?name,label}", "")

        for file_path in files:
            if isinstance(file_path, Tuple):
                file_path, content_type = file_path
            else:
                content_type = "application/octet-stream"

            to_upload = file_path.read_bytes()

            response = self._request_internal(
                asset_url,
                params={"name": file_path.name},
                content=to_upload,
                content_type=content_type,
                request=httpx.post,
            )
            response.raise_for_status()
            yield file_path

    def pull_request_files(
        self, repo: str, pull_request: int, status_list: Iterable[FileStatus]
    ) -> Dict[FileStatus, Iterable[Path]]:
        """
        Get all modified files of a pull request

        Hint: At maximum GitHub allows to receive 3000 files of a commit.

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number
            status_list: Iterable of status change types that should be included

        Returns:
            Information about the commits in the pull request as a dict
        """
        # per default github only shows 35 files per page and at max it is only
        # possible to receive 100
        params = {"per_page": "100"}
        api = f"/repos/{repo}/pulls/{pull_request}/files"
        data = self._request_all(api, params=params)
        file_dict = defaultdict(list)
        for f in data:
            try:
                status = FileStatus(f["status"])
            except ValueError:
                # unknown status
                continue

            if status in status_list:
                file_dict[status].append(Path(f["filename"]))

        return file_dict

    def get_labels(
        self,
        repo: str,
        issue: int,
    ) -> List[str]:
        """
        Get all labels that are set in the issue/pr

        Args:
            repo:   GitHub repository (owner/name) to use
            issue:  Issue/Pull request number

        Returns:
            List of existing labels
        """
        api = f"/repos/{repo}/issues/{issue}/labels"
        response = self._request(api, request=httpx.get)
        return [f["name"] for f in response.json()]

    def set_labels(self, repo: str, issue: int, labels: List[str]):
        """
        Set labels in the issue/pr. Existing labels will be overwritten

        Args:
            repo:   GitHub repository (owner/name) to use
            issue:  Issue/Pull request number
            labels: List of labels, that should be set.
                    Existing labels will be overwritten
        """
        api = f"/repos/{repo}/issues/{issue}/labels"
        data = {"labels": labels}
        response = self._request(api, data=data, request=httpx.post)
        response.raise_for_status()

    def _get_paged_items(self, api: str, key: str) -> Iterable[JSON]:
        """
        Internal method to get the paged items information from different REST
        URLs.
        """
        page = 1
        per_page = 100
        params = {"per_page": per_page, "page": page}

        response = self._request(api, request=httpx.get, params=params)
        response.raise_for_status()

        json = response.json()
        total = json.get("total_count", 0)
        items = json[key]
        downloaded = len(items)

        while total - downloaded > 0:
            page += 1
            params = {"per_page": per_page, "page": page}

            response = self._request(api, request=httpx.get, params=params)
            response.raise_for_status()

            json = response.json()
            items.extend(json[key])
            downloaded = len(items)

        return items

    def get_repository_artifacts(self, repo: str) -> Iterable[JSON]:
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

    def get_repository_artifact(
        self, repo: str, artifact: str
    ) -> Iterable[JSON]:
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
        response = self._request(api, request=httpx.get)
        response.raise_for_status()
        return response.json()

    def download_repository_artifact(
        self, repo: str, artifact: str, destination: Union[Path, str]
    ) -> ContextManager[DownloadProgressIterable]:
        """
        Download a repository artifact zip file

        Args:
            repo: GitHub repository (owner/name) to use
            destination: A path where to store the downloaded file

        Raises:
            HTTPError if the request was invalid

        Example:
            .. code-block:: python

            api = GitHubRESTApi("...")

            print("Downloading", end="")

            with api.download_repository_artifact(
                "org/repo", "artifact.zip"
            ) as progress_iterator:
                for progress in progress_iterator:
                    print(".", end="")
        """
        api = f"{self.url}/repos/{repo}/actions/artifacts/{artifact}/zip"
        return download(api, destination, headers=self._request_headers())

    def get_workflow_artifacts(
        self, repo: str, workflow: str
    ) -> Iterable[JSON]:
        """
        List all artifacts for a workflow run

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: The unique identifier of the workflow run

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the artifacts in the workflow as a dict
        """
        api = f"/repos/{repo}/actions/runs/{workflow}/artifacts"
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
        response = self._request(api, request=httpx.delete)
        response.raise_for_status()

    def get_workflows(self, repo: str) -> Iterable[JSON]:
        """
        List all workflows of a repository

        Args:
            repo: GitHub repository (owner/name) to use

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflows as an iterable of dicts
        """
        api = f"/repos/{repo}/actions/workflows"
        return self._get_paged_items(api, "workflows")

    def get_workflow(self, repo: str, workflow: str) -> JSON:
        """
        Get the information for the given workflow

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: ID of the workflow or workflow file name. For example
                `main.yml`.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflows as a dict
        """
        api = f"/repos/{repo}/actions/workflows/{workflow}"
        response = self._request(api, request=httpx.get)
        response.raise_for_status()
        return response.json()

    def create_workflow_dispatch(
        self,
        repo: str,
        workflow: str,
        *,
        ref: str,
        inputs: Dict[str, str] = None,
    ):
        """
        Create a workflow dispatch event to manually trigger a GitHub Actions
        workflow run.

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: ID of the workflow or workflow file name. For example
                `main.yml`.
            ref: The git reference for the workflow. The reference can be a
                branch or tag name.
            inputs: Input keys and values configured in the workflow file. Any
                default properties configured in the workflow file will be used
                when inputs are omitted.
        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Example:
            .. code-block:: python

            api = GitHubRESTApi("...")
            api.create_workflow_dispatch("foo/bar", "ci.yml", ref="main")
        """
        api = f"/repos/{repo}/actions/workflows/{workflow}/dispatches"
        data = {"ref": ref}

        if inputs:
            data["inputs"] = inputs

        response = self._request(api, data=data, request=httpx.post)
        response.raise_for_status()

    def get_workflow_runs(
        self, repo: str, workflow: Optional[str] = None
    ) -> Iterable[JSON]:
        """
        List all workflow runs of a repository or of a specific workflow.

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: ID of the workflow or workflow file name. For example
                `main.yml`.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflow runs as an iterable of dicts
        """

        api = (
            f"/repos/{repo}/actions/workflows/{workflow}/runs"
            if workflow
            else f"/repos/{repo}/actions/runs"
        )

        return self._get_paged_items(api, "workflow_runs")

    def get_workflow_run(self, repo: str, run: str) -> JSON:
        """
        Get information about a single workflow run

        Args:
            repo: GitHub repository (owner/name) to use

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflow runs as a dict
        """
        api = f"/repos/{repo}/actions/runs/{run}"
        response = self._request(api, request=httpx.get)
        response.raise_for_status()
        return response.json()
