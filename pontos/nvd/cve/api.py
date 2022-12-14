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
from pontos.nvd.models.cve import CVE
from pontos.nvd.models.cvss_v2 import Severity as CVSSv2Severity
from pontos.nvd.models.cvss_v3 import Severity as CVSSv3Severity

__all__ = ("CVEApi",)

DEFAULT_NIST_NVD_CVES_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class CVEApi(NVDApi):
    """
    API for querying the NIST NVD CVE information.

    Should be used as an async context manager.

    Example:
        .. code-block:: python

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
        Create a new instance of the CVE API.

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
            DEFAULT_NIST_NVD_CVES_URL,
            token=token,
            timeout=timeout,
            rate_limit=rate_limit,
        )

    async def cves(
        self,
        *,
        last_modified_start_date: Optional[datetime] = None,
        last_modified_end_date: Optional[datetime] = None,
        published_start_date: Optional[datetime] = None,
        published_end_date: Optional[datetime] = None,
        cpe_name: Optional[str] = None,
        is_vulnerable: Optional[bool] = None,
        cvss_v2_vector: Optional[str] = None,
        cvss_v2_severity: Optional[CVSSv2Severity] = None,
        cvss_v3_vector: Optional[str] = None,
        cvss_v3_severity: Optional[CVSSv3Severity] = None,
        keywords: Optional[Union[List[str], str]] = None,
        cwe_id: Optional[str] = None,
        source_identifier: Optional[str] = None,
        virtual_match_string: Optional[str] = None,
        has_cert_alerts: Optional[bool] = None,
        has_cert_notes: Optional[bool] = None,
        has_kev: Optional[bool] = None,
        has_oval: Optional[bool] = None,
    ) -> AsyncIterator[CVE]:
        """
        Get all CVEs for the provided arguments

        https://nvd.nist.gov/developers/vulnerabilities#divGetCves

        Args:
            last_modified_start_date: Return all CVEs modified after this date.
            last_modified_end_date: Return all CVEs modified before this date.
                If last_modified_start_date is set but no
                last_modified_end_date is passed it is set to now.
            published_start_date: Return all CVEs that were added to the NVD
                (i.e., published) after this date.
            published_end_date: Return all CVEs that were added to the NVD
                (i.e., published) before this date. If published_start_date is
                set but no published_end_date is passed it is set to now.
            cpe_name: Return all CVEs associated with a specific CPE. The exact
                value provided with cpe_name is compared against the CPE Match
                Criteria within a CVE applicability statement. If the value of
                cpe_name is considered to match, the CVE is included in the
                results.
            is_vulnerable: Return only CVEs that match cpe_name that are
                vulnerable. Requires cpe_name to be set.
            cvss_v2_vector: Return all CVEs matching this CVSSv2 vector
            cvss_v2_severity: Return all CVEs matching the CVSSv2 severity
            cvss_v3_vector: Return all CVEs matching this CVSSv3 vector
            cvss_v3_severity: Return all CVEs matching the CVSSv3 severity
            keywords: Returns only the CVEs where a word or phrase is found in
                the current description.
            cwe_id: Returns only the CVEs that include a weakness identified by
                Common Weakness Enumeration using the provided cwe_id.
            source_identifier: Returns CVEs where the exact value of
                source_identifier appears as a data source in the CVE record.
                For example: cve@mitre.org
            virtual_match_string: Filters CVEs more broadly than cpe_name. The
                exact value of virtual_match_string is compared against the CPE
                Match Criteria present on CVE applicability statements. If
                cpe_name and virtual_match_string are provided only cpe_name is
                considered.
            has_cert_alerts: Returns the CVEs that contain a Technical Alert
                from US-CERT.
            has_cert_notes: Returns the CVEs that contain a Vulnerability Note
                from CERT/CC.
            has_kev: Returns the CVE that appear in CISA's Known Exploited
                Vulnerabilities (KEV) Catalog.
            has_oval: Returns the CVEs that contain information from MITRE's
                Open Vulnerability and Assessment Language (OVAL) before this
                transitioned to the Center for Internet Security (CIS).

        Example:
            .. code-block:: python

            async with CVEApi() as api:
                async for cve in api.cves(keywords=["Mac OS X", "kernel"]):
                    print(cve.id)
        """
        total_results = None

        params = {}
        if last_modified_start_date:
            params["lastModStartDate"] = format_date(last_modified_start_date)
            if not last_modified_end_date:
                params["lastModEndDate"] = format_date(now())
        if last_modified_end_date:
            params["lastModEndDate"] = format_date(last_modified_end_date)

        if published_start_date:
            params["pubStartDate"] = format_date(published_start_date)
            if not published_end_date:
                params["pubEndDate"] = format_date(now())
        if published_end_date:
            params["pubEndDate"] = format_date(published_end_date)

        if cpe_name:
            params["cpeName"] = cpe_name
            if is_vulnerable:
                params["isVulnerable"] = ""

        if cvss_v2_vector:
            params["cvssV2Metrics"] = cvss_v2_vector
        if cvss_v3_vector:
            params["cvssV3Metrics"] = cvss_v3_vector
        if cvss_v2_severity:
            params["cvssV2Severity"] = cvss_v2_severity.value
        if cvss_v3_severity:
            params["cvssV3Severity"] = cvss_v3_severity.value

        if keywords:
            if isinstance(keywords, str):
                keywords = [keywords]

            params["keywordSearch"] = " ".join(keywords)
            if any((" " in keyword for keyword in keywords)):
                params["keywordExactMatch"] = ""

        if cwe_id:
            params["cweId"] = cwe_id

        if source_identifier:
            params["sourceIdentifier"] = source_identifier

        if not cpe_name and virtual_match_string:
            params["virtualMatchString"] = virtual_match_string

        if has_cert_alerts:
            params["hasCertAlerts"] = ""
        if has_cert_notes:
            params["hasCertNotes"] = ""
        if has_kev:
            params["hasKev"] = ""
        if has_oval:
            params["hasOval"] = ""

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
            vulnerabilities = data.get("vulnerabilities", [])

            for vulnerability in vulnerabilities:
                yield CVE.from_dict(vulnerability["cve"])

            start_index += results_per_page

    async def cve(self, cve_id: str) -> CVE:
        """
        Returns a single CVE matching the CVE ID. Vulnerabilities not yet
        published in the NVD are not available.

        Args:
            cve_id: Common Vulnerabilities and Exposures identifier

        Example:
            .. code-block:: python

            async with CVEApi() as api:
                cve = await api.cve("CVE-2022-45536"):
                    print(cve)
        """
        if not cve_id:
            raise PontosError("Missing CVE ID.")

        response = await self._get(params={"cveId": cve_id})
        response.raise_for_status()
        data = response.json(object_hook=convert_camel_case)
        vulnerabilities = data["vulnerabilities"]
        if not vulnerabilities:
            raise PontosError(f"No CVE with CVE ID '{cve_id}' found.")

        vulnerability = vulnerabilities[0]
        return CVE.from_dict(vulnerability["cve"])
