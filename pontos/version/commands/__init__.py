# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import Iterable, Optional, Type

from pontos.enum import StrEnum

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
    "ProjectType",
    "get_commands",
)


class ProjectType(StrEnum):
    CMAKE = "cmake"
    CARGO = "cargo"
    GO = "go"
    JAVA = "java"
    NPM = "npm"
    PYPROJECT = "pyproject"


_COMMANDS: dict[ProjectType, Type[VersionCommand]] = {
    ProjectType.CMAKE: CMakeVersionCommand,
    ProjectType.CARGO: CargoVersionCommand,
    ProjectType.GO: GoVersionCommand,
    ProjectType.JAVA: JavaVersionCommand,
    ProjectType.NPM: JavaScriptVersionCommand,
    ProjectType.PYPROJECT: PythonVersionCommand,
}


def get_commands(
    names: Optional[Iterable[ProjectType]] = None,
) -> list[Type[VersionCommand]]:
    """
    Returns the available VersionCommands
    """
    if not names:
        return list(_COMMANDS.values())
    return [command for name, command in _COMMANDS.items() if name in names]
