# Copyright (C) 2020-2022 Greenbone Networks GmbH
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

# pylint: disable=no-name-in-module,no-member

import builtins
import sys
import unittest
from typing import Any, AsyncIterator, Awaitable, Iterable
from unittest import TestCase
from unittest.mock import MagicMock

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


if sys.version_info.minor > 7:
    from unittest import IsolatedAsyncioTestCase
    from unittest.mock import AsyncMock
else:

    @unittest.skip("Async Tests not available for Python 3.7")
    class IsolatedAsyncioTestCase(TestCase):
        pass

    class AsyncMock(MagicMock):
        # implement all necessary methods to keep Pylint happy

        def __init__(self, *args: Any, **kw: Any) -> None:
            super().__init__(*args, **kw)

            self.__aenter__ = self
            self.__aexit__ = self

        def assert_awaited(self):
            pass

        def assert_awaited_once(self):
            pass

        def assert_awaited_with(self, *args, **kwargs):
            pass

        def assert_awaited_once_with(self, *args, **kwargs):
            pass

        def assert_any_await(self, *args, **kwargs):
            pass

        def assert_has_awaits(self, calls, any_order=False):
            pass

        def assert_not_awaited(self):
            pass


class AsyncIteratorMock(AsyncIterator):
    def __init__(self, iterable: Iterable[Any]) -> None:
        self.iterator = iter(iterable)

    async def __anext__(self) -> Awaitable[Any]:
        try:
            return next(self.iterator)
        except StopIteration:
            raise StopAsyncIteration() from None


__all__ = ["IsolatedAsyncioTestCase", "AsyncMock"]
