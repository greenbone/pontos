# SPDX-FileCopyrightText: 2022-2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
from typing import (
    Iterable,
    Iterator,
    Optional,
)

from httpx import Timeout

from pontos.nvd.api import (
    DEFAULT_TIMEOUT_CONFIG,
    JSON,
    NVDApi,
    NVDResults,
    Params,
    format_date,
    now,
)
from pontos.nvd.models.source import Source

__all__ = ("SourceApi",)

DEFAULT_NIST_NVD_SOURCE_URL = (
    "https://services.nvd.nist.gov/rest/json/source/2.0"
)
MAX_SOURCES_PER_PAGE = 1000


def _result_iterator(data: JSON) -> Iterator[Source]:
    sources: Iterable = data.get("sources", [])  # type: ignore
    return (Source.from_dict(source) for source in sources)


class SourceApi(NVDApi):
    """
    API for querying the NIST NVD source API.

    Should be used as an async context manager.

    Example:
        .. code-block:: python

            from pontos.nvd.source import SourceApi

            async with SourceApi() as api:
                async for source in api.sources():
                    print(source)
    """

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        timeout: Optional[Timeout] = DEFAULT_TIMEOUT_CONFIG,
        rate_limit: bool = True,
        request_attempts: int = 1,
    ) -> None:
        """
        Create a new instance of the source API.

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
            request_attempts: The number of attempts per HTTP request. Defaults to 1.
        """
        super().__init__(
            DEFAULT_NIST_NVD_SOURCE_URL,
            token=token,
            timeout=timeout,
            rate_limit=rate_limit,
            request_attempts=request_attempts,
        )

    def sources(
        self,
        *,
        last_modified_start_date: Optional[datetime] = None,
        last_modified_end_date: Optional[datetime] = None,
        source_identifier: Optional[str] = None,
        request_results: Optional[int] = None,
        start_index: int = 0,
        results_per_page: Optional[int] = None,
    ) -> NVDResults[Source]:
        """
        Get all sources for the provided arguments

        https://nvd.nist.gov/developers/data-sources#divGetSource

        Args:
            last_modified_start_date: Return all sources modified after this date.
            last_modified_end_date: Return all sources modified before this date.
                If last_modified_start_date is set but no
                last_modified_end_date is passed it is set to now.
            source_identifier: Return all source records where the source identifier matches.
            request_results: Number of sources to download. Set to None
                (default) to download all available CPEs.
            start_index: Index of the first source to be returned. Useful only for
                paginated requests that should not start at the first page.
            results_per_page: Number of results in a single requests. Mostly
                useful for paginated requests.

        Returns:
            A NVDResponse for sources

        Examples:
            .. code-block:: python

                from pontos.nvd.source import SourceApi

                async with SourceApi() as api:
                    async for source in api.sources(source_identifier="cve@mitre.org"):
                        print(source)
        """
        params: Params = {}
        if last_modified_start_date:
            params["lastModStartDate"] = format_date(last_modified_start_date)
            if not last_modified_end_date:
                params["lastModEndDate"] = format_date(now())
        if last_modified_end_date:
            params["lastModEndDate"] = format_date(last_modified_end_date)

        if source_identifier:
            params["sourceIdentifier"] = source_identifier

        results_per_page = min(
            results_per_page or MAX_SOURCES_PER_PAGE,
            request_results or MAX_SOURCES_PER_PAGE,
        )
        return NVDResults(
            self,
            params,
            _result_iterator,
            request_results=request_results,
            results_per_page=results_per_page,
            start_index=start_index,
        )

    async def __aenter__(self) -> "SourceApi":
        await super().__aenter__()
        return self
