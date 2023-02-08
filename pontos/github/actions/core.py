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

import contextlib
import os
from pathlib import Path
from typing import Optional

from pontos.github.actions.errors import GitHubActionsError


def _to_options(
    name: Optional[str] = None,
    line: Optional[str] = None,
    end_line: Optional[str] = None,
    column: Optional[str] = None,
    end_column: Optional[str] = None,
    title: Optional[str] = None,
):
    options = []
    if name:
        options.append(f"file={name}")
    if line:
        options.append(f"line={line}")
    if end_line:
        options.append(f"endLine={end_line}")
    if column:
        options.append(f"col={column}")
    if end_column:
        options.append(f"endColumn={end_column}")
    if title:
        options.append(f"title={title}")
    return ",".join(options)


def _message(
    message_type: str,
    message: str,
    *,
    name: Optional[str] = None,
    line: Optional[str] = None,
    end_line: Optional[str] = None,
    column: Optional[str] = None,
    end_column: Optional[str] = None,
    title: Optional[str] = None,
):
    options = _to_options(name, line, end_line, column, end_column, title)
    print(f"::{message_type} {options}::{message}")


class Console:
    """
    Class for printing messages to the action console
    """

    @classmethod
    @contextlib.contextmanager
    def group(cls, title: str):
        """
        ContextManager to display a foldable group

        Args:
            title: Title of the group
        """
        cls.start_group(title)
        yield
        cls.end_group()

    @staticmethod
    def start_group(title: str):
        """
        Start a new folable group

        Args:
            title: Title of the group
        """
        print(f"::group::{title}")

    @staticmethod
    def end_group():
        """
        End the last group
        """
        print("::endgroup::")

    @staticmethod
    def warning(
        message: str,
        *,
        name: Optional[str] = None,
        line: Optional[str] = None,
        end_line: Optional[str] = None,
        column: Optional[str] = None,
        end_column: Optional[str] = None,
        title: Optional[str] = None,
    ):
        """
        Print a warning message

        This message will also be shown at the action summary
        """
        _message(
            "warning",
            message,
            name=name,
            line=line,
            end_line=end_line,
            column=column,
            end_column=end_column,
            title=title,
        )

    @staticmethod
    def error(
        message: str,
        *,
        name: Optional[str] = None,
        line: Optional[str] = None,
        end_line: Optional[str] = None,
        column: Optional[str] = None,
        end_column: Optional[str] = None,
        title: Optional[str] = None,
    ):
        """
        Print an error message

        This message will also be shown at the action summary
        """
        _message(
            "error",
            message,
            name=name,
            line=line,
            end_line=end_line,
            column=column,
            end_column=end_column,
            title=title,
        )

    @staticmethod
    def notice(
        message: str,
        *,
        name: Optional[str] = None,
        line: Optional[str] = None,
        end_line: Optional[str] = None,
        column: Optional[str] = None,
        end_column: Optional[str] = None,
        title: Optional[str] = None,
    ):
        """
        Print a warning message

        This message will also be shown at the action summary
        """
        _message(
            "notice",
            message,
            name=name,
            line=line,
            end_line=end_line,
            column=column,
            end_column=end_column,
            title=title,
        )

    @staticmethod
    def log(
        message: str,
    ):
        """
        Print a message to the console
        """
        print(message)

    @staticmethod
    def debug(message: str):
        # pylint: disable=line-too-long
        """
        Print a debug message to the console

        These messages are only shown if the secret ACTIONS_STEP_DEBUG is set to true.
        See https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/enabling-debug-logging#enabling-step-debug-logging
        """
        print(f"::debug::{message}")


class ActionIO:
    @staticmethod
    def output(name: str, value: str):
        """
        Set action output

        An action output can be consumed by another job

        Args:
            name: Name of the output variable
            value: Value of the output variable
        """
        output_filename = os.environ.get("GITHUB_OUTPUT")
        if not output_filename:
            raise GitHubActionsError(
                "GITHUB_OUTPUT environment variable not set. Can't write "
                "action output."
            )

        with Path(output_filename).open("a", encoding="utf8") as f:
            f.write(f"{name}={value}\n")

    @staticmethod
    def input(name: str, default: Optional[str] = None) -> str:
        """
        Get the value of an action input

        Args:
            name: Name of the input variable
            default: Use as default if the is no value for the variable
        """
        return os.environ.get(
            f"INPUT_{name.replace(' ', '_').upper()}", default  # type: ignore
        )
