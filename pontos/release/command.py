# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from abc import ABC, abstractmethod
from typing import Any, SupportsInt

from pontos.terminal import Terminal


class Command(ABC):
    """Base class for release related command"""

    def __init__(self, *, terminal: Terminal, error_terminal: Terminal) -> None:
        self.terminal = terminal
        self.error_terminal = error_terminal

    def print_error(self, *messages: Any, **kwargs: Any) -> None:
        """Print an error to the error terminal"""
        self.error_terminal.error(*messages, **kwargs)

    def print_warning(self, *messages: Any, **kwargs: Any) -> None:
        """Print a warning to the error console"""
        self.error_terminal.warning(*messages, **kwargs)

    @abstractmethod
    def run(self, **kwargs: Any) -> SupportsInt:
        """Run the command"""


class AsyncCommand(Command):
    """Base class for release related commands using asyncio"""

    def run(self, **kwargs: Any) -> SupportsInt:
        """
        Run the command using asyncio

        MUST NOT be called when an asyncio event loop is already running.
        """
        return asyncio.run(self.async_run(**kwargs))

    @abstractmethod
    async def async_run(self, **kwargs: Any) -> SupportsInt:
        """
        Run the async command

        Gets called via run. Alternatively use similar code as the example.

        Example:
            .. code-block:: python

                import asyncio

                async def main():
                    cmd = MyAsyncCommand()
                    task = asyncio.create_task(cmd.async_run(arg1, arg2))
                    ...
                    await task


                asyncio.run(main())
        """
