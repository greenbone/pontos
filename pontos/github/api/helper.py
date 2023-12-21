# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import Dict, List, Optional, Union

import httpx

DEFAULT_GITHUB_API_URL = "https://api.github.com"
DEFAULT_TIMEOUT = 180.0  # three minutes
DEFAULT_TIMEOUT_CONFIG = httpx.Timeout(DEFAULT_TIMEOUT)  # three minutes
JSON_OBJECT = Dict[str, Union[str, bool, int]]  # pylint: disable=invalid-name
JSON = Union[List[JSON_OBJECT], JSON_OBJECT]  # pylint: disable=invalid-name


def _get_next_url(response: httpx.Response) -> Optional[str]:
    if response and response.links:
        try:
            return response.links["next"]["url"]
        except KeyError:
            pass

    return None
