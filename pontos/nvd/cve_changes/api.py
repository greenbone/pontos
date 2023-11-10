# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, timedelta
from typing import AsyncIterator, Iterable, Optional, Union

from httpx import Timeout

from pontos.errors import PontosError
from pontos.nvd.api import (
    DEFAULT_TIMEOUT_CONFIG,
    JSON,
    NVDApi,
    Params,
    convert_camel_case,
    format_date,
    now,
)
from pontos.nvd.models.cve_change import CVEChange, EventName

__all__ = ("CVEChangesApi",)

DEFAULT_NIST_NVD_CVE_HISTORY_URL = (
    "https://services.nvd.nist.gov/rest/json/cvehistory/2.0"
)


class CVEChangesApi(NVDApi):
    """
    API for querying the NIST NVD CVE Change History information.

    Should be used as an async context manager.

    Example:
        .. code-block:: python

            from pontos.nvd.cve_changes import CVEChangesApi

            async with CVEChangesApi() as api:
                async for cve_change in api.changes(event_name=EventName.INITIAL_ANALYSIS):
                    print(cve_change)
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

    async def changes(
        self,
        *,
        change_start_date: Optional[datetime] = None,
        change_end_date: Optional[datetime] = None,
        cve_id: Optional[str] = None,
        event_name: Optional[Union[EventName, str]] = None,
    ) -> AsyncIterator[CVEChange]:
        """
        Get all CVEs for the provided arguments

        https://nvd.nist.gov/developers/vulnerabilities#divGetCves

        Args:
            change_start_date: Return all CVE changes after this date.
            change_end_date: Return all CVE changes before this date.
            cve_id: Return all CVE changes for this Common Vulnerabilities and Exposures identifier.
            event_name: Return all CVE changes with this event name.


        Returns:
            An async iterator to iterate over CVEChange model instances

        Example:
            .. code-block:: python

                from pontos.nvd.cve_changes import CVEChangesApi

                async with CVEChangesApi() as api:
                    async for cve_change in api.changes(event_name=EventName.INITIAL_ANALYSIS):
                        print(cve_change)
        """
        total_results: Optional[int] = None

        if change_start_date and not change_end_date:
            change_end_date = min(
                now(), change_start_date + timedelta(days=120)
            )
        elif change_end_date and not change_start_date:
            change_start_date = change_end_date - timedelta(days=120)

        params: Params = {}
        if change_start_date and change_end_date:
            if change_end_date - change_start_date > timedelta(days=120):
                raise PontosError(
                    "change_start_date and change_end_date must not be more than 120 days apart"
                )

            params["changeStartDate"] = format_date(change_start_date)
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

            data: JSON = response.json(object_hook=convert_camel_case)

            total_results = data["total_results"]  # type: ignore
            results_per_page: int = data["results_per_page"]  # type: ignore
            cve_changes: Iterable = data.get("cve_changes", [])  # type: ignore

            for cve_change in cve_changes:
                yield CVEChange.from_dict(cve_change["change"])

            start_index += results_per_page  # type: ignore

    async def __aenter__(self) -> "CVEChangesApi":
        await super().__aenter__()
        return self
