# SPDX-FileCopyrightText: 2021-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import os
from contextlib import contextmanager
from io import TextIOWrapper
from pathlib import Path
from typing import Generator, Optional

from pontos.typing import SupportsStr

from .errors import GitHubActionsError


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
    @contextmanager
    def group(cls, title: str):
        """
        ContextManager to display a foldable group

        .. code-block:: python

            from pontos.github.actions import Console

            console = Console()
            with console.group("my-group"):
                console.log("some message)

        Args:
            title: Title of the group
        """
        cls.start_group(title)
        yield
        cls.end_group()

    @staticmethod
    def start_group(title: str):
        """
        Start a new foldable group

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
        """  # noqa: E501
        print(f"::debug::{message}")


class ActionOutput:
    """
    A GitHub Action output
    """

    def __init__(self, file: TextIOWrapper) -> None:
        self._file = file

    def write(self, name: str, value: SupportsStr):
        """
        Set action output

        An action output can be consumed by another job

        Args:
            name: Name of the output variable
            value: Value of the output variable
        """
        self._file.write(f"{name}={value}\n")


class ActionIO:
    """
    Class with static methods for handling GitHub Action IO
    """

    @staticmethod
    def has_output() -> bool:
        """
        Check if GITHUB_OUTPUT is set
        """
        return "GITHUB_OUTPUT" in os.environ

    @staticmethod
    @contextmanager
    def out() -> Generator[ActionOutput, None, None]:
        """
        Create an action output to write several output values

        An action output can be consumed by another job

        Example:
            .. code-block:: python

                from pontos.github.actions import ActionIO

                with ActionIO.out() as out:
                    out.write("foo", "bar")
                    out.write("lorem", "ipsum")
        """
        output_filename = os.environ.get("GITHUB_OUTPUT")
        if not output_filename:
            raise GitHubActionsError(
                "GITHUB_OUTPUT environment variable not set. Can't write "
                "action output."
            )

        with Path(output_filename).open("a", encoding="utf8") as f:
            yield ActionOutput(f)

    @staticmethod
    def output(name: str, value: SupportsStr):
        """
        Set action output

        An action output can be consumed by another job

        Example:
            .. code-block:: python

                from pontos.github.actions import ActionIO

                ActionIO.output("foo", "bar")

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
    def input(name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get the value of an action input

        Example:
            .. code-block:: python

                from pontos.github.actions import ActionIO

                value = ActionIO.input("foo", "bar")

        Args:
            name: Name of the input variable
            default: Use as default if the is no value for the variable
        """
        return os.environ.get(
            f"INPUT_{name.replace(' ', '_').upper()}", default
        )
