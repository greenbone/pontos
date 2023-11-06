# Copyright (C) 2023 Greenbone AG
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
from types import TracebackType
from typing import Any, AsyncIterator, Dict, Iterable, Optional, Type, Union

from httpx import Timeout

from pontos.nvd.api import (
    DEFAULT_TIMEOUT_CONFIG,
    NVDApi,
    Params,
    convert_camel_case,
    format_date,
    now,
)
from pontos.nvd.models.cve_change import CVEChange, EventName

__all__ = ("CVEChangeHistoryApi",)

DEFAULT_NIST_NVD_CVE_HISTORY_URL = (
    "https://services.nvd.nist.gov/rest/json/cvehistory/2.0"
)


class CVEChangeHistoryApi(NVDApi):
    """
    API for querying the NIST NVD CVE Change History information.

    Should be used as an async context manager.

    Example:
        .. code-block:: python

            from pontos.nvd.cve import CVEApi

            async with CVEApi() as api:
                cve = await api.cve("CVE-2022-45536")
    """

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        timeout: Optional[Timeout] = DEFAULT_TIMEOUT_CONFIG,
        rate_limit: bool = True,
    ) -> None:
        """
        Create a new instance of the CVE Change History API.

        Args:
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
        super().__init__(
            DEFAULT_NIST_NVD_CVE_HISTORY_URL,
            token=token,
            timeout=timeout,
            rate_limit=rate_limit,
        )

    async def cve_changes(
        self,
        *,
        change_start_date: Optional[datetime] = None,
        change_end_date: Optional[datetime] = None,
        cve_id: Optional[str] = None,
        event_name: Optional[EventName] = None,
    ) -> AsyncIterator[CVEChange]:
        """
        Get all CVEs for the provided arguments

        https://nvd.nist.gov/developers/vulnerabilities#divGetCves

        Args:
            TODO: ...

        Returns:
            An async iterator to iterate over CVEChange model instances

        Example:
            .. code-block:: python

                from pontos.nvd.cve import CVEApi

                async with CVEApi() as api:
                    async for cve in api.cves(keywords=["Mac OS X", "kernel"]):
                        print(cve.id)
        """
        total_results: Optional[int] = None

        params: Params = {}
        if change_start_date:
            params["changeStartDate"] = format_date(change_start_date)
            if not change_end_date:
                params["changeEndDate"] = format_date(now())

        if change_end_date:
            params["changeEndDate"] = format_date(change_end_date)

        if cve_id:
            params["cveId"] = cve_id

        if event_name:
            params["eventName"] = event_name

        start_index: int = 0
        results_per_page = None

        while total_results is None or start_index < total_results:
            params["startIndex"] = start_index

            if results_per_page is not None:
                params["resultsPerPage"] = results_per_page

            response = await self._get(params=params)
            response.raise_for_status()

            data: Dict[str, Union[int, str, Dict[str, Any]]] = response.json(
                object_hook=convert_camel_case
            )

            total_results = data["total_results"]  # type: ignore
            results_per_page: int = data["results_per_page"]  # type: ignore
            cve_changes: Iterable = data.get("cve_changes", [])  # type: ignore

            for cve_change in cve_changes:
                yield CVEChange.from_dict(cve_change["change"])

            if results_per_page is not None:
                start_index += results_per_page

    async def __aenter__(self) -> "CVEChangeHistoryApi":
        await super().__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        return await super().__aexit__(  # type: ignore
            exc_type, exc_value, traceback
        )
