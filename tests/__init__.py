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
