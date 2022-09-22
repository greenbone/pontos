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
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Union

import httpx

DEFAULT_GITHUB_API_URL = "https://api.github.com"
DEFAULT_TIMEOUT_CONFIG = httpx.Timeout(180.0)  # three minutes


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


JSON_OBJECT = Dict[str, Union[str, bool, int]]  # pylint: disable=invalid-name
JSON = Union[List[JSON_OBJECT], JSON_OBJECT]


class GitHubREST:
    def __init__(
        self,
        token: Optional[str] = None,
        url: Optional[str] = DEFAULT_GITHUB_API_URL,
        *,
        timeout: httpx.Timeout = DEFAULT_TIMEOUT_CONFIG,
    ) -> None:
        self.token = token
        self.url = url
        self.timeout = timeout

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
            timeout=self.timeout,
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

    def _get_paged_items(
        self, api: str, key: str, *, params: Optional[JSON_OBJECT] = None
    ) -> Iterable[JSON_OBJECT]:
        """
        Internal method to get the paged items information from different REST
        URLs.
        """
        page = 1
        per_page = 100
        params = params or {}
        params.update({"per_page": per_page, "page": page})

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
