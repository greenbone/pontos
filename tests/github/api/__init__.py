# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from unittest.mock import MagicMock

import httpx

from pontos.github.api.client import GitHubAsyncREST, GitHubAsyncRESTClient
from tests import AsyncMock, IsolatedAsyncioTestCase


def create_response(*args, **kwargs) -> MagicMock:
    return MagicMock(spec=httpx.Response, *args, **kwargs)


class GitHubAsyncRESTTestCase(IsolatedAsyncioTestCase):
    api_cls = GitHubAsyncREST

    def setUp(self) -> None:
        self.client = AsyncMock(spec=GitHubAsyncRESTClient)
        self.api = self.api_cls(self.client)
