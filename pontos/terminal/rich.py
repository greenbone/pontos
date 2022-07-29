# Copyright (C) 2022 Greenbone Networks GmbH
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

from typing import Any, Callable

from rich.console import Console, RenderableType
from rich.padding import Padding
from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskProgressColumn,
    TextColumn,
)

from pontos.helper import DownloadProgressIterable

from .terminal import Signs, Terminal


def red(text: str) -> str:
    return f"[red]{text}[/red]"


def yellow(text: str) -> str:
    return f"[yellow]{text}[/yellow]"


def cyan(text: str) -> str:
    return f"[cyan]{text}[/cyan]"


def green(text: str) -> str:
    return f"[green]{text}[/green]"


def white(text: str) -> str:
    return f"[white]{text}[/white]"


class PaddingColumn(ProgressColumn):
    def __init__(self, indent: int, table_column=None):
        self._padding = Padding.indent("", indent)
        super().__init__(table_column=table_column)

    def render(self, task: Task) -> RenderableType:
        return self._padding


class RichTerminal(Terminal):
    """
    A Terminal based on `rich`_

    .. _rich: https://github.com/Textualize/rich/
    """

    def __init__(self) -> None:
        super().__init__()
        self._console = Console()

    def _indent_message(self):
        return " " * self._indent

    def _print_status(
        self,
        *messages: Any,
        status: Signs,
        color: Callable,
        **kwargs: Any,
    ):
        self._console.print(
            self._indent_message(), color(status), *messages, **kwargs
        )

    def get_progress_default_columns(self):
        return (
            PaddingColumn(self._indent),
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        )

    def progress(self, **kwargs) -> Progress:
        kwargs["console"] = self._console
        return Progress(
            *self.get_progress_default_columns(),
            **kwargs,
        )

    def out(self, *messages: Any, **kwargs: Any) -> None:
        kwargs["highlight"] = False
        self._console.out(self._indent_message(), *messages, **kwargs)

    def print(self, *messages: Any, **kwargs: Any) -> None:
        self._console.print(self._indent_message(), *messages, **kwargs)

    def ok(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.OK, "color": green})
        self._print_status(*messages, **kwargs)

    def fail(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.FAIL, "color": red})
        self._print_status(*messages, **kwargs)

    def error(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.ERROR, "color": red})
        self._print_status(*messages, **kwargs)

    def warning(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.WARNING, "color": yellow})
        self._print_status(*messages, **kwargs)

    def info(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.INFO, "color": cyan})
        self._print_status(*messages, **kwargs)

    def bold_info(self, *messages: Any, **kwargs: Any) -> None:
        kwargs.update({"status": Signs.INFO, "color": cyan, "style": "bold"})
        self._print_status(*messages, **kwargs)

    def download_progress(self, progress: DownloadProgressIterable) -> None:
        with self.progress() as rich_progress:
            task_description = f"Downloading [blue]{progress.url}"
            if progress.length:
                task_id = rich_progress.add_task(
                    task_description, total=progress.length
                )
                for percent in progress:
                    rich_progress.advance(task_id, percent)
            else:
                task_id = rich_progress.add_task(task_description, total=None)
                for _ in progress:
                    rich_progress.advance(task_id)

            rich_progress.update(task_id, total=1, completed=1)
