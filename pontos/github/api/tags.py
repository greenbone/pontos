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

from datetime import datetime
from typing import Optional, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.tag import GitObjectType, Tag
from pontos.helper import enum_or_value


class GitHubAsyncRESTTags(GitHubAsyncREST):
    async def create(
        self,
        repo: str,
        tag: str,
        message: str,
        name: str,
        email: str,
        git_object: str,
        *,
        git_object_type: Optional[
            Union[GitObjectType, str]
        ] = GitObjectType.COMMIT,
        date: Optional[datetime] = None,
    ) -> Tag:
        """
        Create a new Git tag

        https://docs.github.com/en/rest/git/tags#create-a-tag-object

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The tag's name. This is typically a version (e.g., "v0.0.1").
            message: The tag message.
            name: The name of the author of the tag
            email: The email of the author of the tag
            git_object: The SHA of the git object this is tagging.
            git_object_type: The type of the object we're tagging. Normally this
                is a commit type but it can also be a tree or a blob.
            date: When this object was tagged.
        """
        data = {
            "tag": tag,
            "message": message,
            "object": git_object,
            "type": enum_or_value(git_object_type),
            "tagger": {
                "name": name,
                "email": email,
            },
        }

        if date:
            data["tagger"]["date"] = date.isoformat(timespec="seconds")

        api = f"/repos/{repo}/git/tags"
        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return Tag.from_dict(response.json())

    async def create_tag_reference(
        self,
        repo: str,
        tag: str,
        sha: str,
    ) -> None:
        """
        Create git tag reference (A real tag in git).

        https://docs.github.com/en/rest/git/refs#create-a-reference

        Args:
            repo: The name of the repository.
                The name is not case sensitive.
            tag: Github tag name.
            sha: The SHA1 value for this Github tag.
        """

        data = {
            "ref": f"refs/tags/{tag}",
            "sha": sha,
        }

        api = f"/repos/{repo}/git/refs"
        response = await self._client.post(api, data=data)
        response.raise_for_status()

    async def get(self, repo: str, tag_sha: str) -> Tag:
        """
        Get information about a git tag

        Args:
            repo: GitHub repository (owner/name) to use
            tag_sha: SHA of the git tag object
        """
        api = f"/repos/{repo}/git/tags/{tag_sha}"
        response = await self._client.get(api)
        response.raise_for_status()
        return Tag.from_dict(response.json())
