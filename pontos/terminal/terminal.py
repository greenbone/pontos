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
import re
from contextlib import contextmanager
from enum import Enum
from shutil import get_terminal_size
from typing import Callable, Generator

import colorful as cf

from .logfile import process_logger

TERMINAL_SIZE_FALLBACK = (80, 24)  # use a small standard size as fallback


class Signs(Enum):
    FAIL = '\N{HEAVY MULTIPLICATION X}'
    ERROR = '\N{MULTIPLICATION SIGN}'
    WARNING = '\N{WARNING SIGN}'
    OK = '\N{CHECK MARK}'
    INFO = '\N{INFORMATION SOURCE}'
    NONE = ' '

    def __str__(self):
        return f'{self.value}'


STATUS_LEN = 2


class Terminal:
    def __init__(self, **kwargs):
        print(kwargs)
        self._indent = 0
        self._log2file: bool = kwargs.get('log2file', False)
        self._log2term: bool = kwargs.get('log2term', True)

    @staticmethod
    def get_width() -> int:
        """
        Get the width of the terminal window
        """
        width, _ = get_terminal_size(TERMINAL_SIZE_FALLBACK)
        return width

    def _print_status(
        self,
        message: str,
        status: Signs,
        color: Callable,
        style: Callable,
        *,
        new_line: bool = True,
        overwrite: bool = False,
    ) -> None:
        width = self.get_width()
        offset = self._indent + STATUS_LEN
        usable_width = width - offset

        first_line = ''
        if overwrite:
            first_line = '\r'
        first_line += f'{color(status)} '
        first_line += ' ' * self._indent

        # remove existing newlines, to avoid breaking the formatting
        # done by the terminal
        messages = message.split("\n")
        output = self._format_message(
            message=messages[0],
            usable_width=usable_width,
            offset=offset,
            first=first_line,
        )
        if len(messages) > 0:
            for msg in messages[1:]:
                output += "\n"
                output += self._format_message(
                    message=msg,
                    usable_width=usable_width,
                    offset=offset,
                )

        self.print_logfile_message(output)
        self.print_message(output, style, new_line)

    def print_logfile_message(self, message: str) -> None:
        if self._log2file:
            process_logger.info(re.sub(r'\x1b\[[\d;]*[mGKHF]', '', message))

    def print_message(
        self, message: str, style: Callable, new_line: bool = True
    ) -> None:
        if self._log2term:
            if new_line:
                print(style(message))
            else:
                print(style(message), end='', flush=True)

    def _format_message(
        self, message: str, usable_width: int, offset: int, *, first: str = ""
    ) -> str:
        if first:
            formatted_message = f"{first}"
        else:
            formatted_message = " " * offset
        while usable_width < len(message):
            part = message[:usable_width]
            message = message[usable_width:]
            formatted_message += f'{part}'
            if len(message) > 0:
                formatted_message += f'\n{" " * offset}'
        formatted_message += f"{message}"
        return formatted_message

    @contextmanager
    def indent(self, indentation: int = 4) -> Generator:
        current_indent = self._indent
        self.add_indent(indentation)

        yield self

        self._indent = current_indent

    def add_indent(self, indentation: int = 4) -> None:
        self._indent += indentation

    def reset_indent(self) -> None:
        self._indent = 0

    def print(self, *messages: str, style: Callable = cf.reset) -> None:
        message = ''.join(messages)
        self._print_status(message, Signs.NONE, cf.white, style)

    def print_overwrite(
        self, *messages: str, style: Callable = cf.reset, new_line: bool = False
    ) -> None:
        message = ''.join(messages)
        self._print_status(
            message,
            Signs.NONE,
            cf.white,
            style,
            new_line=new_line,
            overwrite=True,
        )

    def ok(self, message: str, style: Callable = cf.reset) -> None:
        self._print_status(message, Signs.OK, cf.green, style)

    def fail(self, message: str, style: Callable = cf.reset) -> None:
        self._print_status(message, Signs.FAIL, cf.red, style)

    def error(self, message: str, style: Callable = cf.reset) -> None:
        self._print_status(message, Signs.ERROR, cf.red, style)

    def warning(self, message: str, style: Callable = cf.reset) -> None:
        self._print_status(message, Signs.WARNING, cf.yellow, style)

    def info(self, message: str, style: Callable = cf.reset) -> None:
        self._print_status(message, Signs.INFO, cf.cyan, style)

    def bold_info(self, message: str, style: Callable = cf.bold) -> None:
        self._print_status(message, Signs.INFO, cf.cyan, style)
