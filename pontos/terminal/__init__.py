# Copyright (C) 2021-2022 Greenbone Networks GmbH
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

from pathlib import Path
from typing import Optional
from .terminal import Terminal

__term = None  # pylint: disable=invalid-name

__all__ = [
    'error',
    'fail',
    'info',
    'bold_info',
    'ok',
    'out',
    'warning',
]


def ok(message: str) -> None:
    __term.ok(message)


def fail(message: str) -> None:
    __term.fail(message)


def error(message: str) -> None:
    __term.error(message)


def warning(message: str) -> None:
    __term.warning(message)


def info(message: str) -> None:
    __term.info(message)


def bold_info(message: str) -> None:
    __term.bold_info(message)


def out(message: str):
    __term.print(message)


def overwrite(message: str, new_line: bool = False):
    __term.print_overwrite(message, new_line=new_line)


def _init_terminal(term: Terminal):
    __term = term


def terminal(
    term: Optional[Terminal] = None, verbose: int = 1, log_file: Path = None
) -> Terminal:
    """Init a Terminal that uses the verbosity given as in args

    Arguments:
        verbose         integer defining the verbosity (default: 1)
        log_file        path to a log_file, that will be used to log
                        output into
    """
    global __term  # pylint: disable=global-statement, invalid-name
    if not term:
        __term = Terminal(verbose=verbose, log_file=log_file)
    else:
        __term = term
    return __term


def _set_terminal(term: Terminal) -> Terminal:
    # remove later; left for backwards-compability
    return terminal(term)
