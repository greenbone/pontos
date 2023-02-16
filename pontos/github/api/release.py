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

import asyncio
from pathlib import Path
from typing import (
    AsyncContextManager,
    AsyncIterator,
    Iterable,
    Optional,
    Tuple,
    Union,
)

import httpx

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.release import Release
from pontos.helper import AsyncDownloadProgressIterable, download_async, upload


class GitHubAsyncRESTReleases(GitHubAsyncREST):
    async def create(
        self,
        repo: str,
        tag: str,
        *,
        body: Optional[str] = None,
        name: Optional[str] = None,
        target_commitish: Optional[str] = None,
        draft: Optional[bool] = False,
        prerelease: Optional[bool] = False,
    ) -> Release:
        """
        Create a new GitHub release

        https://docs.github.com/en/rest/releases/releases#create-a-release

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release
            body: Content of the changelog for the release
            name: name of the release, e.g. 'pontos 1.0.0'
            target_commitish: Only needed when tag is not there yet
            draft: If the release is a draft. False by default.
            prerelease: If the release is a pre release. False by default.

        Raises:
            httpx.HTTPStatusError if the request was invalid
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
        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return Release.from_dict(response.json())

    async def exists(self, repo: str, tag: str) -> bool:
        """
        Check wether a GitHub release exists by tag

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release

        Returns:
            True if the release exists
        """
        api = f"/repos/{repo}/releases/tags/{tag}"
        response = await self._client.get(api)
        return response.is_success

    async def get(self, repo: str, tag: str) -> Release:
        """
        Get data of a GitHub release by tag

        https://docs.github.com/en/rest/releases/releases#get-a-release-by-tag-name

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release

        Raises:
            httpx.HTTPStatusError if the request was invalid
        """
        api = f"/repos/{repo}/releases/tags/{tag}"
        response = await self._client.get(api)
        response.raise_for_status()
        return Release.from_dict(response.json())

    def download_release_tarball(
        self, repo: str, tag: str
    ) -> AsyncContextManager[AsyncDownloadProgressIterable[bytes]]:
        """
        Download a release tarball (tar.gz) file

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release

        Raises:
            HTTPStatusError if the request was invalid

        Example:
            .. code-block:: python

            async with api.download_release_tarball(
                "foo/bar", "v1.0.0"
            ) as download:
                file_path = Path("a.file.tar.gz")
                with file_path.open("wb") as f:
                    async for content, progress in download:
                        f.write(content)
                        print(progress)
        """
        api = f"https://github.com/{repo}/archive/refs/tags/{tag}.tar.gz"
        return download_async(self._client.stream(api))

    def download_release_zip(
        self,
        repo: str,
        tag: str,
    ) -> AsyncContextManager[AsyncDownloadProgressIterable[bytes]]:
        """
        Download a release zip file

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release

        Raises:
            HTTPStatusError if the request was invalid

        Example:
            .. code-block:: python

            async with api.download_release_zip(
                "foo/bar", "v1.0.0"
            ) as download:
                file_path = Path("a.file.zip")
                with file_path.open("wb") as f:
                    async for content, progress in download:
                        f.write(content)
                        print(progress)
        """
        api = f"https://github.com/{repo}/archive/refs/tags/{tag}.zip"
        return download_async(self._client.stream(api))

    async def download_release_assets(
        self,
        repo: str,
        tag: str,
        *,
        match_pattern: Optional[str] = None,
    ) -> AsyncIterator[
        Tuple[str, AsyncContextManager[AsyncDownloadProgressIterable[bytes]]]
    ]:
        """
        Download release assets

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release
            match_pattern: Optional pattern which the name of the available
                artifact must match. For example "*.zip". Allows to download
                only specific artifacts.

        Raises:
            HTTPError if the request was invalid

        Example:
            .. code-block:: python

            async def download_asset(name: str, download_cm) -> Path:
                async with download_cm as iterator:
                    file_path = Path(name)
                    with file_path.open("wb") as f:
                        async for content, progress in iterator:
                            f.write(content)
                            print(name, progress)
                    return file_path


            tasks = []
            async for name, download_cm in api.download_release_assets(
                "foo/bar, "v1.2.3",
            ):
                tasks.append(asyncio.create_task(
                    download_asset(name, download_cm)
                )

            file_paths = await asyncio.gather(*tasks)

        """
        release = await self.get(repo, tag)
        assets_url = release.assets_url
        if not assets_url:
            raise RuntimeError("assets URL not found")

        response = await self._client.get(assets_url)
        response.raise_for_status()

        assets_json = response.json()
        for asset_json in assets_json:
            asset_url: str = asset_json.get("url", "")
            name: str = asset_json.get("name", "")

            if match_pattern and not Path(name).match(match_pattern):
                continue

            yield name, download_async(self._client.stream(asset_url))

    async def upload_release_assets(
        self,
        repo: str,
        tag: str,
        files: Iterable[Union[Path, Tuple[Path, str]]],
    ) -> AsyncIterator[Path]:
        """
        Upload release assets asynchronously

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The git tag for the release
            files: An iterable of file paths or an iterable of tuples
                containing a file path and content types to upload as an asset

        Returns:
            yields each file after its upload is finished

        Raises:
            HTTPError if an upload request was invalid

        Example:
            .. code-block:: python

            files = (Path("foo.txt"), Path("bar.txt"),)
            async for uploaded_file in api.upload_release_assets(
                "foo/bar", "1.2.3", files
            ):
                print(f"Uploaded: {uploaded_file}")

            files = [
                (Path("foo.txt"), "text/ascii"),
                (Path("bar.pdf"), "application/pdf"),
            ]
            async for uploaded_file in api.upload_release_assets(
                "foo/bar", "1.2.3", files
            ):
               print(f"Uploaded: {uploaded_file}")
        """
        release = await self.get(repo, tag)
        asset_url = release.upload_url.replace("{?name,label}", "")

        async def upload_file(
            file_path: Path, content_type: str
        ) -> Tuple[httpx.Response, Path]:
            response = await self._client.post(
                asset_url,
                params={"name": file_path.name},
                content_type=content_type,
                content_length=file_path.stat().st_size,
                content=upload(file_path),
            )
            return response, file_path

        tasks = []
        for file_path in files:
            if isinstance(file_path, Tuple):
                file_path, content_type = file_path
            else:
                content_type = "application/octet-stream"

            tasks.append(upload_file(file_path, content_type))

        for coroutine in asyncio.as_completed(tasks):
            response, file_path = await coroutine
            response.raise_for_status()
            yield file_path
