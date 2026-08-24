# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from collections.abc import Iterable

from pontos.enum import StrEnum

from ._cargo import CargoVersionCommand
from ._cmake import CMakeVersionCommand
from ._command import VersionCommand
from ._go import GoVersionCommand
from ._java import JavaVersionCommand
from ._javascript import JavaScriptVersionCommand
from ._poetry import PoetryVersionCommand
from ._python import PythonVersionCommand
from ._uv import UvVersionCommand

__all__ = (
    "CMakeVersionCommand",
    "CargoVersionCommand",
    "GoVersionCommand",
    "JavaScriptVersionCommand",
    "JavaVersionCommand",
    "PoetryVersionCommand",
    "ProjectType",
    "PythonVersionCommand",
    "UvVersionCommand",
    "VersionCommand",
    "get_commands",
)


class ProjectType(StrEnum):
    CMAKE = "cmake"
    CARGO = "cargo"
    GO = "go"
    JAVA = "java"
    NPM = "npm"
    PYPROJECT = "pyproject"
    POETRY = "poetry"
    UV = "uv"


_COMMANDS: dict[ProjectType, type[VersionCommand]] = {
    ProjectType.CMAKE: CMakeVersionCommand,
    ProjectType.CARGO: CargoVersionCommand,
    ProjectType.GO: GoVersionCommand,
    ProjectType.JAVA: JavaVersionCommand,
    ProjectType.NPM: JavaScriptVersionCommand,
    ProjectType.PYPROJECT: PoetryVersionCommand,  # legacy project type for poetry projects
    ProjectType.POETRY: PoetryVersionCommand,
    ProjectType.UV: UvVersionCommand,
}


def get_commands(
    names: Iterable[ProjectType] | None = None,
) -> list[type[VersionCommand]]:
    """
    Returns the available VersionCommands
    """
    if not names:
        return [
            command
            for name, command in _COMMANDS.items()
            # don't include poetry command twice
            if name != ProjectType.PYPROJECT
        ]
    return [command for name, command in _COMMANDS.items() if name in names]
