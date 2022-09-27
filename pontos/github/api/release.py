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
from typing import ContextManager, Iterable, Iterator, Optional, Tuple, Union

import httpx

from pontos.github.api.helper import JSON_OBJECT
from pontos.helper import DownloadProgressIterable, download


class GitHubRESTReleaseMixin:
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
        response: httpx.Response = self._request(
            api, data=data, request=httpx.post
        )
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
        response: httpx.Response = self._request(api)
        return response.is_success

    def release(self, repo: str, tag: str) -> JSON_OBJECT:
        """
        Get data of a GitHub release by tag

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release

        Raises:
            HTTPError if the request was invalid
        """
        api = f"/repos/{repo}/releases/tags/{tag}"
        response: httpx.Response = self._request(api)
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

        response: httpx.Response = self._request_internal(assets_url)
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

            response: httpx.Response = self._request_internal(
                asset_url,
                params={"name": file_path.name},
                content=to_upload,
                content_type=content_type,
                request=httpx.post,
            )
            response.raise_for_status()
            yield file_path
