# Copyright (C) 2023 Greenbone AG
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

from typing import Iterable, Tuple, Type

from ._cargo import CargoVersionCommand
from ._cmake import CMakeVersionCommand
from ._command import VersionCommand
from ._go import GoVersionCommand
from ._java import JavaVersionCommand
from ._javascript import JavaScriptVersionCommand
from ._python import PythonVersionCommand

__all__ = (
    "VersionCommand",
    "CMakeVersionCommand",
    "GoVersionCommand",
    "JavaScriptVersionCommand",
    "JavaVersionCommand",
    "PythonVersionCommand",
    "CargoVersionCommand",
    "get_commands",
)

__COMMANDS: Tuple[Type[VersionCommand]] = (  # type: ignore[assignment]
    CMakeVersionCommand,
    GoVersionCommand,
    JavaVersionCommand,
    JavaScriptVersionCommand,
    PythonVersionCommand,
    CargoVersionCommand,
)


def get_commands() -> Iterable[Type[VersionCommand]]:
    """
    Returns the available VersionCommands
    """
    return __COMMANDS
