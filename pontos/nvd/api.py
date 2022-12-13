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
from abc import ABC
from datetime import datetime, timezone
from types import TracebackType
from typing import Any, Dict, Optional, Type

from httpx import AsyncClient, Response, Timeout

from pontos.helper import snake_case

SLEEP_TIMEOUT = 30.0  # in seconds
DEFAULT_TIMEOUT = 180.0  # three minutes
DEFAULT_TIMEOUT_CONFIG = Timeout(DEFAULT_TIMEOUT)  # three minutes

Headers = Dict[str, str]
Params = Dict[str, str]

__all__ = (
    "now",
    "format_date",
    "convert_camel_case",
    "NVDApi",
    "DEFAULT_TIMEOUT_CONFIG",
)


def now() -> datetime:
    """
    Return current datetime with UTC timezone applied
    """
    return datetime.now(tz=timezone.utc)


def format_date(date: datetime) -> str:
    return date.isoformat(timespec="seconds")


def convert_camel_case(dct: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert camel case keys into snake case keys
    """
    converted = {}
    for key, value in dct.items():
        converted[snake_case(key)] = value
    return converted


async def sleep() -> None:
    await asyncio.sleep(SLEEP_TIMEOUT)


class NVDApi(ABC):
    """
    Base class for querying the NIST NVD API.

    Should be used as an async context manager.

    """

    def __init__(
        self,
        url: str,
        *,
        token: Optional[str] = None,
        timeout: Optional[Timeout] = DEFAULT_TIMEOUT_CONFIG,
        rate_limit: bool = True,
    ) -> None:
        """
        Create a new instance of the CVE API.

        Args:
            url: The API URL to use.
            token: The API key to use. Using an API key allows to run more
                requests at the same time.
            timeout: Timeout settings for the HTTP requests
            rate_limit: Set to False to ignore rate limits. The public rate
                limit (without an API key) is 5 requests in a rolling 30 second
                window. The rate limit with an API key is 50 requests in a
                rolling 30 second window.
                See https://nvd.nist.gov/developers/start-here#divRateLimits
                Default: True.
        """
        self._url = url
        self._token = token
        self._client = AsyncClient(http2=True, timeout=timeout)

        if rate_limit:
            self._rate_limit = 50 if token else 5
        else:
            self._rate_limit = None

        self._request_count = 0

    def _request_headers(self) -> Headers:
        """
        Get the default request headers
        """
        headers = {}

        if self._token:
            headers["apiKey"] = self._token

        return headers

    async def _consider_rate_limit(self) -> None:
        """
        Apply rate limit if necessary
        """
        if not self._rate_limit:
            return

        self._request_count += 1
        if self._request_count > self._rate_limit:
            await sleep()
            self._request_count = 0

    async def _get(
        self,
        *,
        params: Optional[Params] = None,
    ) -> Response:
        """
        A request against the NIST NVD CVE REST API.
        """
        headers = self._request_headers()

        await self._consider_rate_limit()

        return await self._client.get(self._url, headers=headers, params=params)

    async def __aenter__(self) -> "NVDApi":
        # reset rate limit counter
        self._request_count = 0
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        return await self._client.__aexit__(exc_type, exc_value, traceback)
