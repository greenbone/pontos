# Copyright (C) 2019-2022 Greenbone Networks GmbH
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

from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from shutil import get_terminal_size
from typing import Any, Callable, Generator, Optional

import colorful as cf  # type: ignore

from pontos.helper import DownloadProgressIterable

TERMINAL_SIZE_FALLBACK = (80, 24)  # use a small standard size as fallback


class Signs(Enum):
    FAIL = "\N{HEAVY MULTIPLICATION X}"
    ERROR = "\N{MULTIPLICATION SIGN}"
    WARNING = "\N{WARNING SIGN}"
    OK = "\N{CHECK MARK}"
    INFO = "\N{INFORMATION SOURCE}"
    NONE = " "

    def __str__(self):
        return f"{self.value}"


STATUS_LEN = 2


class Terminal(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._indent = 0

    @contextmanager
    def indent(self, indentation: int = 4) -> Generator[None, None, None]:
        """
        A context manager for indenting output using spaces

        Example:
            with terminal.indent():
                terminal.print("...")

        Args:
            indentation: Number of spaces to be used for indentation.
                         By default 4.
        """
        current_indent = self._indent
        self._add_indent(indentation)

        yield

        self._indent = current_indent

    def _add_indent(self, indentation: int = 4) -> None:
        self._indent += indentation

    @abstractmethod
    def out(self, *messages: Any, **kwargs: Any) -> None:
        """
        Print messages without formatting.

        Args:
            *messages: Arguments to print.
            **kwargs: Keyword arguments forwarded to the underlying
                     implementation.
        """

    @abstractmethod
    def print(self, *messages: Any, **kwargs: Any) -> None:
        """
        Print messages. Possibly formatting is applied.

        Args:
            *messages: Arguments to print.
            **kwargs: Keyword arguments forwarded to the underlying
                     implementation.
        """

    @abstractmethod
    def ok(self, *messages: Any, **kwargs: Any) -> None:
        """
        Print a success message. Possibly formatting is applied.

        Args:
            *messages: Arguments to print.
            **kwargs: Keyword arguments forwarded to the underlying
                     implementation.
        """

    @abstractmethod
    def fail(self, *messages: Any, **kwargs: Any) -> None:
        """
        Print a failure message. Possibly formatting is applied.

        Args:
            *messages: Arguments to print.
            **kwargs: Keyword arguments forwarded to the underlying
                     implementation.
        """

    @abstractmethod
    def error(self, *messages: Any, **kwargs: Any) -> None:
        """
        Print an error message. Possibly formatting is applied.

        Args:
            *messages: Arguments to print.
            **kwargs: Keyword arguments forwarded to the underlying
                     implementation.
        """

    @abstractmethod
    def warning(self, *messages: Any, **kwargs: Any) -> None:
        """
        Print a warning message. Possibly formatting is applied.

        Args:
            *messages: Arguments to print.
            **kwargs: Keyword arguments forwarded to the underlying
                     implementation.
        """

    @abstractmethod
    def info(self, *messages: Any, **kwargs: Any) -> None:
        """
        Print an info message. Possibly formatting is applied.

        Args:
            *messages: Arguments to print.
            **kwargs: Keyword arguments forwarded to the underlying
                     implementation.
        """

    @abstractmethod
    def bold_info(self, *messages: Any, **kwargs: Any) -> None:
        """
        Print an info message with bold text. Possibly formatting is applied.

        Args:
            *messages: Arguments to print.
            **kwargs: Keyword arguments forwarded to the underlying
                     implementation.
        """

    @abstractmethod
    def download_progress(self, progress: DownloadProgressIterable) -> None:
        """
        Display a download progress
        """


class ConsoleTerminal(Terminal):
    """
    A simple Terminal using colorful internally for highlighting
    """

    # Keep arguments for backwards compatibility but ignore them
    # pylint: disable=unused-argument
    def __init__(self, *, verbose: int = 1, log_file: Optional[Path] = None):
        super().__init__()

    @staticmethod
    def get_width() -> int:
        """
        Get the width of the terminal window
        """
        width, _ = get_terminal_size(TERMINAL_SIZE_FALLBACK)
        return width

    def _print_status(
        self,
        *messages: Any,
        status: Signs,
        color: Callable,
        style: Callable = cf.reset,
        new_line: bool = True,
        **kwargs: Any,
    ) -> None:
        width = self.get_width()
        offset = self._indent + STATUS_LEN
        usable_width = width - offset

        # deal with existing newlines, to avoid breaking the formatting
        # done by the terminal
        message = "".join(messages)
        processed_messages = message.split("\n")
        output = self._format_message(
            message=processed_messages[0],
            usable_width=usable_width,
            offset=offset,
            first=True,
        )
        if len(processed_messages) > 0:
            for msg in processed_messages[1:]:
                output += "\n"
                output += self._format_message(
                    message=msg,
                    usable_width=usable_width,
                    offset=offset,
                )
        if new_line:
            print(style(f"{color(status)} {output}"), **kwargs)
        else:
            kwargs.update({"end": "", "flush": True})
            print(style(f"{color(status)} {output}"), **kwargs)

    def _format_message(
        self,
        message: str,
        usable_width: int,
        offset: int,
        *,
        first: bool = False,
    ) -> str:
        formatted_message = ""
        if first:
            formatted_message += " " * self._indent
        else:
            formatted_message += " " * offset

        while usable_width < len(message):
            part = message[:usable_width]
            message = message[usable_width:]
            formatted_message += f"{part}"

            if len(message) > 0:
                formatted_message += f'\n{" " * offset}'

        formatted_message += f"{message}"

        return formatted_message

    def out(self, *messages: Any, **kwargs: Any) -> None:
        self.print(*messages, **kwargs)

    def print(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.NONE, "color": cf.white})
        self._print_status(*messages, **kwargs)

    def ok(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.OK, "color": cf.green})
        self._print_status(*messages, **kwargs)

    def fail(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.FAIL, "color": cf.red})
        self._print_status(*messages, **kwargs)

    def error(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.ERROR, "color": cf.red})
        self._print_status(*messages, **kwargs)

    def warning(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.WARNING, "color": cf.yellow})
        self._print_status(*messages, **kwargs)

    def info(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.INFO, "color": cf.cyan})
        self._print_status(*messages, **kwargs)

    def bold_info(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update(
            {"status": Signs.INFO, "color": cf.cyan, "style": cf.bold}
        )
        self._print_status(*messages, **kwargs)

    def download_progress(self, progress: DownloadProgressIterable) -> None:
        spinner = ["-", "\\", "|", "/"]
        if progress.length:
            for percent in progress:
                done = int(50 * percent) if percent else 0
                self.out(
                    f"\r[{'=' * done}{' ' * (50-done)}]", end="", flush=True
                )
        else:
            i = 0
            for _ in progress:
                i = i + 1
                if i == 4:
                    i = 0
                self.out(f"\r[{spinner[i]}]", end="", flush=True)

        self.out(f"\r[{Signs.OK}]{' ' * 50}", end="", flush=True)
