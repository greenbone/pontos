# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
from types import TracebackType
from typing import (
    Any,
    Iterator,
    Optional,
    Type,
)

from httpx import Timeout

from pontos.errors import PontosError
from pontos.nvd.api import (
    DEFAULT_TIMEOUT_CONFIG,
    JSON,
    NVDApi,
    NVDResults,
    Params,
    convert_camel_case,
    format_date,
    now,
)
from pontos.nvd.models.cpe_match_string import CPEMatchString

__all__ = ("CPEMatchApi",)

DEFAULT_NIST_NVD_CPE_MATCH_URL = (
    "https://services.nvd.nist.gov/rest/json/cpematch/2.0"
)
MAX_CPE_MATCHES_PER_PAGE = 500


class CPEMatchApi(NVDApi):
    """
    API for querying the NIST NVD CPE match information.

    Should be used as an async context manager.

    Example:
        .. code-block:: python

            from pontos.nvd.cpe_match import CPEMatchApi

            async with CPEMatchApi() as api:
                cpe = await api.cpe_match_string(...)
    """

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        timeout: Optional[Timeout] = DEFAULT_TIMEOUT_CONFIG,
        rate_limit: bool = True,
    ) -> None:
        """
        Create a new instance of the CPE API.

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
            DEFAULT_NIST_NVD_CPE_MATCH_URL,
            token=token,
            timeout=timeout,
            rate_limit=rate_limit,
        )
        self._cpe_match_cache: dict[str, Any] = {}

    def cpe_matches(
        self,
        *,
        last_modified_start_date: Optional[datetime] = None,
        last_modified_end_date: Optional[datetime] = None,
        cve_id: Optional[str] = None,
        match_string_search: Optional[str] = None,
        request_results: Optional[int] = None,
        start_index: int = 0,
        results_per_page: Optional[int] = None,
    ) -> NVDResults[CPEMatchString]:
        """
        Get all CPE matches for the provided arguments

        https://nvd.nist.gov/developers/products#divCpeMatch

        Args:
            last_modified_start_date: Return all CPE matches last modified after this date.
            last_modified_end_date: Return all CPE matches last modified before this date.
            cve_id: Return all CPE matches for this Common Vulnerabilities and Exposures identifier.
            match_string_search: Return all CPE matches that conform to the given pattern
            request_results: Number of CPE matches to download. Set to None
                (default) to download all available matches.
            start_index: Index of the first CPE match to be returned. Useful
                only for paginated requests that should not start at the first
                page.
            results_per_page: Number of results in a single requests. Mostly
                useful for paginated requests.

        Returns:
            A NVDResponse for CPE matches

        Example:
            .. code-block:: python

                from pontos.nvd.cpe_match import CPEMatchApi

                async with CPEMatchApi() as api:
                    async for match_string in api.matches(cve_id='CVE-2024-1234'):
                        print(match_string)

                    json = api.matches(cve_id='CVE-2024-1234').json()

                    async for match_strings in api.matches(
                        cve_id='CVE-2024-1234',
                    ).chunks():
                        for match_string in match_strings:
                        print(match_string)
        """
        params: Params = {}

        if last_modified_start_date:
            params["lastModStartDate"] = format_date(last_modified_start_date)
            if not last_modified_end_date:
                params["lastModEndDate"] = format_date(now())
        if last_modified_end_date:
            params["lastModEndDate"] = format_date(last_modified_end_date)

        if cve_id:
            params["cveId"] = cve_id
        if match_string_search:
            params["matchStringSearch"] = match_string_search

        results_per_page = min(
            results_per_page or MAX_CPE_MATCHES_PER_PAGE,
            request_results or MAX_CPE_MATCHES_PER_PAGE,
        )
        if start_index is None:
            start_index = 0

        return NVDResults(
            self,
            params,
            self._result_iterator,
            request_results=request_results,
            results_per_page=results_per_page,
            start_index=start_index,
        )

    def _result_iterator(self, data: JSON) -> Iterator[CPEMatchString]:
        """
        Creates an iterator of all the CPEMatchStrings in given API response JSON

        Args:
            data: The JSON response data to get the match strings from

        Returns:
            An iterator over the CPEMatchStrings
        """
        results: list[dict[str, Any]] = data.get("match_strings", [])  # type: ignore
        return (
            CPEMatchString.from_dict_with_cache(
                result["match_string"], self._cpe_match_cache
            )
            for result in results
        )

    async def cpe_match(self, match_criteria_id: str) -> CPEMatchString:
        """
        Returns a single CPE match for the given match criteria id.

        Args:
            match_criteria_id: Match criteria identifier

        Returns:
            A CPE match for the given identifier

        Raises:
            PontosError: If match criteria ID is empty or if no match with the given ID is
                found.

        Example:
            .. code-block:: python

                from pontos.nvd.cpe_match import CVEApi

                async with CVEApi() as api:
                    match = await api.cpe_match("36FBCF0F-8CEE-474C-8A04-5075AF53FAF4")
                    print(match)
        """
        if not match_criteria_id:
            raise PontosError("Missing Match Criteria ID.")

        response = await self._get(
            params={"matchCriteriaId": str(match_criteria_id)}
        )
        response.raise_for_status()
        data = response.json(object_hook=convert_camel_case)
        match_strings = data["match_strings"]
        if not match_strings:
            raise PontosError(
                f"No match with Match Criteria ID '{match_criteria_id}' found."
            )

        match_string = match_strings[0]
        return CPEMatchString.from_dict_with_cache(
            match_string["match_string"], self._cpe_match_cache
        )

    async def __aenter__(self) -> "CPEMatchApi":
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
