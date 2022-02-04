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

from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List, Optional

import requests

DEFAULT_GITHUB_API_URL = "https://api.github.com"

DEFAULT_TIMEOUT = 1000
DEFAULT_CHUNK_SIZE = 4096


class FileStatus(Enum):
    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"
    RENAMED = "renamed"


class DownloadProgressIterable:
    def __init__(
        self, content_iterator: Iterator, destination: Path, length: int
    ):
        self._length = None if length is None else int(length)
        self._content_iterator = content_iterator
        self._destination = destination

    @property
    def length(self) -> Optional[int]:
        """
        Size in bytes of the to be downloaded file or None if the size is not
        available
        """
        return self._length

    @property
    def destination(self) -> Path:
        """
        Destination path of the to be downloaded file
        """
        return self._destination

    def _download(self) -> Iterator[Optional[float]]:
        dl = 0
        with self._destination.open("wb") as f:
            for content in self._content_iterator:
                dl += len(content)
                f.write(content)
                yield dl / self._length if self._length else None

    def __iter__(self) -> Iterator[Optional[float]]:
        return self._download()

    def run(self):
        """
        Just run the download without caring about the progress
        """
        try:
            it = iter(self)
            while True:
                next(it)
        except StopIteration:
            pass


def download(
    url: str,
    destination: Optional[Path] = None,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout: int = DEFAULT_TIMEOUT,
) -> DownloadProgressIterable:
    """Download file in url to filename

    Arguments:
        url: The url of the file we want to download
        destination: Path of the file to store the download in. If set it will
                     be derived from the passed URL.
        chunk_size: Download file in chunks of this size
        timeout: Connection timeout

    Raises:
        HTTPError if the request was invalid

    Returns:
        A DownloadProgressIterator that yields the progress of the download in
        percent for each downloaded chunk or None for each chunk if the progress
        is unknown.
    """
    destination = Path(url.split('/')[-1]) if not destination else destination

    response = requests.get(url, stream=True, timeout=timeout)
    response.raise_for_status()

    total_length = response.headers.get('content-length')

    return DownloadProgressIterable(
        response.iter_content(chunk_size=chunk_size),
        destination,
        total_length,
    )


class GitHubRESTApi:
    def __init__(
        self, token: str, url: Optional[str] = DEFAULT_GITHUB_API_URL
    ) -> None:
        self.token = token
        self.url = url

    def _request(
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
        response = self._request(api)
        return response.ok

    def pull_request_exists(self, repo: str, pull_request: int) -> bool:
        """
        Check if a single branch in a repository exists

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number to check
        """
        api = f"/repos/{repo}/pulls/{pull_request}"
        response = self._request(api)
        return response.ok

    def pull_request_commits(
        self, repo: str, pull_request: int
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
        response = self._request(api, params=params)
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
            base_branch: Branch as target for the pull
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
            "body": body.replace('\\n', '\n'),
        }
        response = self._request(api, data=data, request=requests.post)
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
        response = self._request(api, data=data, request=requests.post)
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
        response = self._request(api, request=requests.delete)
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
            'tag_name': tag,
            'target_commitish': target_commitish,
            'name': name,
            'body': body,
            'draft': draft,
            'prerelease': prerelease,
        }
        api = f"/repos/{repo}/releases"
        response = self._request(api, data=data, request=requests.post)
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
        return response.ok

    def release(self, repo: str, tag: str) -> Dict[str, str]:
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
    ) -> DownloadProgressIterable:
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
    ) -> DownloadProgressIterable:
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

    def pull_request_files(
        self, repo: str, pull_request: int, status_list: List[FileStatus]
    ) -> Dict[FileStatus, Iterable[Path]]:
        """
        Get all modified files of a pull request

        Hint: At maximum GitHub allows to receive 100 commits. If a pull request
        contains more then 100 commits only the first 100 are returned.

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number
            status_list: List of status change types that should be included

        Returns:
            Information about the commits in the pull request as a dict
        """
        # per default github only shows 35 commits and at max it is only
        # possible to receive 100
        # might add the page parameter, to get the files 101-202 and so on
        params = {"per_page": "100"}
        api = f"/repos/{repo}/pulls/{pull_request}/files"
        response = self._request(api, params=params)
        file_dict = {}
        for status in status_list:
            file_dict[status] = [
                Path(f['filename'])
                for f in response.json()
                if f['status'] == status.value
            ]

        return file_dict
