# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=no-name-in-module,no-member,unnecessary-dunder-call

import builtins
import sys
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from pontos.testing import AsyncIteratorMock

if sys.version_info.minor < 10:
    # aiter and anext have been added in Python 3.10
    def aiter(obj):  # pylint: disable=redefined-builtin
        return obj.__aiter__()

    def anext(obj):  # pylint: disable=redefined-builtin
        return obj.__anext__()

else:

    def aiter(obj):  # pylint: disable=redefined-builtin
        return builtins.aiter(obj)

    def anext(obj):  # pylint: disable=redefined-builtin
        return builtins.anext(obj)


__all__ = (
    "IsolatedAsyncioTestCase",
    "AsyncMock",
    "AsyncIteratorMock",
    "aiter",
    "anext",
)
