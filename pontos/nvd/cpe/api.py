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
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from httpx import Timeout

from pontos.errors import PontosError
from pontos.nvd.api import (
    DEFAULT_TIMEOUT_CONFIG,
    NVDApi,
    convert_camel_case,
    format_date,
    now,
)
from pontos.nvd.models.cpe import CPE

DEFAULT_NIST_NVD_CPES_URL = "https://services.nvd.nist.gov/rest/json/cpes/2.0"


class CPEApi(NVDApi):
    """
    API for querying the NIST NVD CPE information.

    Should be used as an async context manager.

    Example:
        .. code-block:: python

        async with CPEApi() as api:
            cpe = await api.cpe("")
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

    async def cpe(self, cpe_name_id: str) -> CPE:
        """
        Returns a single CPE matching the CPE ID.

        Args:
            cpe_name_id: Returns a specific CPE record identified by a Universal
                Unique Identifier (UUID).

        Example:
            .. code-block:: python

            async with CPEApi() as api:
                cpe = await api.cpe("87316812-5F2C-4286-94FE-CC98B9EAEF53"):
                    print(cpe)
        """
        if not cpe_name_id:
            raise PontosError("Missing CPE Name ID.")

        response = await self._get(params={"cpeNameId": cpe_name_id})
        response.raise_for_status()
        data = response.json(object_hook=convert_camel_case)
        products = data["products"]
        if not products:
            raise PontosError(f"No CPE with CPE Name ID '{cpe_name_id}' found.")

        product = products[0]
        return CPE.from_dict(product["cpe"])

    async def cpes(
        self,
        *,
        last_modified_start_date: Optional[datetime] = None,
        last_modified_end_date: Optional[datetime] = None,
        cpe_match_string: Optional[str] = None,
        keywords: Optional[Union[List[str], str]] = None,
        match_criteria_id: Optional[str] = None,
    ) -> AsyncIterator[CPE]:
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

        Example:
            .. code-block:: python

            async with CPEApi() as api:
                async for cpe in api.cpes(keywords=["Mac OS X"]):
                    print(cpe.cpe_name, cpe.cpe_name_id)
        """
        total_results = None

        params = {}
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

        start_index = 0
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

            results_per_page: int = data["results_per_page"]
            total_results: int = data["total_results"]
            products = data.get("products", [])

            for product in products:
                yield CPE.from_dict(product["cpe"])

            start_index += results_per_page
