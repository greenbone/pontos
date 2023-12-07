# Copyright (C) 2022 Greenbone AG
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
from typing import (
    Any,
    Iterator,
    List,
    Optional,
    Type,
    Union,
)
from uuid import UUID

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
from pontos.nvd.models.cpe import CPE

DEFAULT_NIST_NVD_CPES_URL = "https://services.nvd.nist.gov/rest/json/cpes/2.0"
MAX_CPES_PER_PAGE = 10000


def _result_iterator(data: JSON) -> Iterator[CPE]:
    results: list[dict[str, Any]] = data.get("products", [])  # type: ignore
    return (CPE.from_dict(result["cpe"]) for result in results)


class CPEApi(NVDApi):
    """
    API for querying the NIST NVD CPE information.

    Should be used as an async context manager.

    Example:
        .. code-block:: python

            from pontos.nvd.cpe import CPEApi

            async with CPEApi() as api:
                cpe = await api.cpe(...)
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
            DEFAULT_NIST_NVD_CPES_URL,
            token=token,
            timeout=timeout,
            rate_limit=rate_limit,
        )

    async def cpe(self, cpe_name_id: Union[str, UUID]) -> CPE:
        """
        Query for a CPE matching the CPE UUID.

        Args:
            cpe_name_id: Returns a specific CPE record identified by a Universal
                Unique Identifier (UUID).

        Example:
            .. code-block:: python

                from pontos.nvd.cpe import CPEApi

                async with CPEApi() as api:
                    cpe = await api.cpe("87316812-5F2C-4286-94FE-CC98B9EAEF53")
                    print(cpe)

        Returns:
            A single CPE matching the CPE UUID

        Raises:
            PontosError: If a CPE with the CPE UUID couldn't be found.
        """
        if not cpe_name_id:
            raise PontosError("Missing CPE Name ID.")

        response = await self._get(params={"cpeNameId": str(cpe_name_id)})
        response.raise_for_status()
        data = response.json(object_hook=convert_camel_case)
        products = data["products"]
        if not products:
            raise PontosError(f"No CPE with CPE Name ID '{cpe_name_id}' found.")

        product = products[0]
        return CPE.from_dict(product["cpe"])

    def cpes(
        self,
        *,
        last_modified_start_date: Optional[datetime] = None,
        last_modified_end_date: Optional[datetime] = None,
        cpe_match_string: Optional[str] = None,
        keywords: Optional[Union[List[str], str]] = None,
        match_criteria_id: Optional[str] = None,
        request_results: Optional[int] = None,
        start_index: int = 0,
        results_per_page: Optional[int] = None,
    ) -> NVDResults[CPE]:
        """
        Get all CPEs for the provided arguments

        https://nvd.nist.gov/developers/products

        Args:
            last_modified_start_date: Return all CPEs modified after this date.
            last_modified_end_date: Return all CPEs modified before this date.
                If last_modified_start_date is set but no
                last_modified_end_date is passed it is set to now.
            cpe_match_string: Returns all CPE names that exist in the Official
                CPE Dictionary.
            keywords: Returns only the CPEs where a word or phrase is found in
                the metadata title or reference links.
            match_criteria_id: Returns all CPE records associated with a match
                string identified by its UUID.
            request_results: Number of CPEs to download. Set to None (default)
                to download all available CPEs.
            start_index: Index of the first CPE to be returned. Useful only for
                paginated requests that should not start at the first page.
            results_per_page: Number of results in a single requests. Mostly
                useful for paginated requests.

        Returns:
            A NVDResponse for CPEs

        Examples:
            .. code-block:: python

                from pontos.nvd.cpe import CPEApi

                async with CPEApi() as api:
                    async for cpe in api.cpes(keywords=["Mac OS X"]):
                        print(cpe.cpe_name, cpe.cpe_name_id)

                    json = await api.cpes(request_results=10).json()

                    async for cpes in api.cpes(
                        cpe_match_string="cpe:2.3:o:microsoft:windows_7:-:*:*:*:*:*:*:*",
                    ).chunks():
                        for cpe in cpes:
                            print(cpe)
        """
        params: Params = {}
        if last_modified_start_date:
            params["lastModStartDate"] = format_date(last_modified_start_date)
            if not last_modified_end_date:
                params["lastModEndDate"] = format_date(now())
        if last_modified_end_date:
            params["lastModEndDate"] = format_date(last_modified_end_date)

        if cpe_match_string:
            params["cpeMatchString"] = cpe_match_string

        if keywords:
            if isinstance(keywords, str):
                keywords = [keywords]

            params["keywordSearch"] = " ".join(keywords)
            if any((" " in keyword for keyword in keywords)):
                params["keywordExactMatch"] = ""

        if match_criteria_id:
            params["matchCriteriaId"] = match_criteria_id

        results_per_page = min(
            results_per_page or MAX_CPES_PER_PAGE,
            request_results or MAX_CPES_PER_PAGE,
        )

        return NVDResults(
            self,
            params,
            _result_iterator,
            request_results=request_results,
            results_per_page=results_per_page,
            start_index=start_index,
        )

    async def __aenter__(self) -> "CPEApi":
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
