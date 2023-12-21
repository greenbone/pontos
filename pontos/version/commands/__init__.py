# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

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
