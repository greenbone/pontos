# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
import time
from abc import ABC
from datetime import datetime, timezone
from types import TracebackType
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generator,
    Generic,
    Iterator,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from httpx import URL, AsyncClient, Response, Timeout

from pontos.errors import PontosError
from pontos.helper import snake_case

SLEEP_TIMEOUT = 30.0  # in seconds
DEFAULT_TIMEOUT = 180.0  # three minutes
DEFAULT_TIMEOUT_CONFIG = Timeout(DEFAULT_TIMEOUT)  # three minutes

Headers = Dict[str, str]
Params = Dict[str, Union[str, int]]
JSON = dict[str, Union[int, str, dict[str, Any]]]

__all__ = (
    "convert_camel_case",
    "format_date",
    "now",
    "NVDApi",
    "NVDResults",
)


def now() -> datetime:
    """
    Return current datetime with UTC timezone applied
    """
    return datetime.now(tz=timezone.utc)


def format_date(date: datetime) -> str:
    """
    Format date matching to NVD api

    Args:
        date: Date to format

    Returns:
        Formatted date as string
    """
    return date.isoformat(timespec="seconds")


def convert_camel_case(dct: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert camel case keys into snake case keys

    Args:
        dct: dict to convert

    Returns:
        A dict with key names converted to snake case
    """
    converted = {}
    for key, value in dct.items():
        converted[snake_case(key)] = value
    return converted


class NoMoreResults(PontosError):
    """
    Raised if the NVD API has no more results to consume
    """


class InvalidState(PontosError):
    """
    Raised if the state of the NVD API is invalid
    """


T = TypeVar("T")

result_iterator_func = Callable[[JSON], Iterator[T]]


class NVDResults(Generic[T], AsyncIterable[T], Awaitable["NVDResults"]):
    """
    A generic object for accessing the results of a NVD API response

    It implements the pagination and will issue requests against the NVD API.
    """

    def __init__(
        self,
        api: "NVDApi",
        params: Params,
        result_func: result_iterator_func,
        *,
        request_results: Optional[int] = None,
        results_per_page: Optional[int] = None,
        start_index: int = 0,
    ) -> None:
        self._api = api
        self._params = params
        self._url: Optional[URL] = None

        self._data: Optional[JSON] = None
        self._it: Optional[Iterator[T]] = None
        self._total_results: Optional[int] = None
        self._downloaded_results: int = 0

        self._start_index = start_index
        self._request_results = request_results
        self._results_per_page = results_per_page

        self._current_index = start_index
        self._current_request_results = request_results
        self._current_results_per_page = results_per_page

        self._result_func = result_func

    async def chunks(self) -> AsyncIterator[Sequence[T]]:
        """
        Return the results in chunks

        The size of the chunks is defined by results_per_page.

        Examples:
            .. code-block:: python

                nvd_results: NVDResults = ...

                async for results in nvd_results.chunks():
                    for result in results:
                        print(result)
        """
        while True:
            try:
                if self._it:
                    yield list(self._it)
                await self._next_iterator()
            except NoMoreResults:
                return

    async def items(self) -> AsyncIterator[T]:
        """
        Return the results of the NVD API response

        Examples:
            .. code-block:: python

                nvd_results: NVDResults = ...

                async for result in nvd_results.items():
                    print(result)
        """
        while True:
            try:
                if self._it:
                    for result in self._it:
                        yield result
                await self._next_iterator()
            except NoMoreResults:
                return

    async def json(self) -> Optional[JSON]:
        """
        Return the result from the NVD API request as JSON

        Examples:
            .. code-block:: python

                nvd_results: NVDResults = ...
                while data := await nvd_results.json():
                    print(data)

        Returns:
            The response data as JSON or None if the response is exhausted.
        """
        try:
            if not self._data:
                await self._next_iterator()

            data = self._data
            self._data = None
            return data
        except NoMoreResults:
            return None

    def __len__(self) -> int:
        """
        Get the number of available result items for a NVD API request

        Examples:
            .. code-block:: python

                nvd_results: NVDResults = ...
                total_results = len(nvd_results) # None because it hasn't been awaited yet
                json = await nvd_results.json() # request the plain JSON data
                total_results = len(nvd_results) # contains the total number of results now

                nvd_results: NVDResults = ...
                total_results = len(nvd_results) # None because it hasn't been awaited yet
                async for result in nvd_results:
                    print(result)
                total_results = len(nvd_results) # contains the total number of results now

        Returns:
            The total number of available results if the NVDResults has been awaited
        """
        if self._total_results is None:
            raise InvalidState(
                f"{self.__class__.__name__} has not been awaited yet."
            )
        return self._total_results

    def __aiter__(self) -> AsyncIterator[T]:
        """
        Return the results of the NVD API response

        Same as the items() method. @see items()

        Examples:
            .. code-block:: python

                nvd_results: NVDResults = ...

                async for result in nvd_results:
                    print(result)
        """
        return self.items()

    def __await__(self) -> Generator[Any, None, "NVDResults"]:
        """
        Request the next results from the NVD API

        Examples:
            .. code-block:: python

                nvd_results: NVDResults = ...
                print(len(nvd_results)) # None, because no request has been send yet
                await nvd_results # creates a request to the NVD API
                print(len(nvd_results))

        Returns:
            The response data as JSON or None if the response is exhausted.
        """

        return self._next_iterator().__await__()

    async def _load_next_data(self) -> None:
        if (
            not self._current_request_results
            or self._downloaded_results < self._current_request_results
        ):
            params = self._params
            params["startIndex"] = self._current_index

            if self._current_results_per_page is not None:
                params["resultsPerPage"] = self._current_results_per_page

            response = await self._api._get(params=params)
            response.raise_for_status()

            self._url = response.url
            data: JSON = response.json(object_hook=convert_camel_case)

            self._data = data
            self._current_results_per_page = int(data["results_per_page"])  # type: ignore
            self._total_results = int(data["total_results"])  # type: ignore
            self._current_index += self._current_results_per_page
            self._downloaded_results += self._current_results_per_page

            if not self._current_request_results:
                self._current_request_results = self._total_results

            if (
                self._request_results
                and self._downloaded_results + self._current_results_per_page
                > self._request_results
            ):
                # avoid downloading more results then requested
                self._current_results_per_page = (
                    self._request_results - self._downloaded_results
                )

        else:
            raise NoMoreResults()

    async def _get_next_iterator(self) -> Iterator[T]:
        await self._load_next_data()
        return self._result_func(self._data)  # type: ignore

    async def _next_iterator(self) -> "NVDResults":
        self._it = await self._get_next_iterator()
        return self

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f'url="{self._url}" '
            f"total_results={self._total_results} "
            f"start_index={self._start_index} "
            f"current_index={self._current_index} "
            f"results_per_page={self._results_per_page}>"
        )


class NVDApi(ABC):
    """
    Abstract base class for querying the NIST NVD API.

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
            self._rate_limit: Optional[int] = 50 if token else 5
        else:
            self._rate_limit = None

        self._request_count = 0
        self._last_sleep = time.monotonic()

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
            time_since_last_sleep = time.monotonic() - self._last_sleep

            if time_since_last_sleep < SLEEP_TIMEOUT:
                time_to_sleep = SLEEP_TIMEOUT - time_since_last_sleep
                await asyncio.sleep(time_to_sleep)

            self._last_sleep = time.monotonic()
            self._request_count = 0

    async def _get(
        self,
        *,
        params: Optional[Params] = None,
    ) -> Response:
        """
        A request against the NIST NVD REST API.
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
        return await self._client.__aexit__(  # type: ignore
            exc_type, exc_value, traceback
        )
