# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import httpx

DEFAULT_GITHUB_API_URL = "https://api.github.com"
DEFAULT_TIMEOUT = 180.0  # three minutes
DEFAULT_TIMEOUT_CONFIG = httpx.Timeout(DEFAULT_TIMEOUT)  # three minutes
JSON_OBJECT = dict[str, str | bool | int]
JSON = list[JSON_OBJECT] | JSON_OBJECT


def _get_next_url(response: httpx.Response) -> str | None:
    if response and response.links:
        try:
            return response.links["next"]["url"]
        except KeyError:
            pass

    return None
