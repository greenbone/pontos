# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import IO, Any, Callable, Iterable, Optional

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
    A Terminal based on `rich <https://github.com/Textualize/rich/>`_.
    """

    def __init__(
        self,
        file: Optional[IO[str]] = None,
    ) -> None:
        """
        Create a new RichTerminal

        Args:
            file: A file object where the output should write to.
                Default is stdout.
        """
        super().__init__()
        self._console = Console(file=file)

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

    def get_progress_default_columns(self) -> Iterable[ProgressColumn]:
        return (
            PaddingColumn(self._indent),
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        )

    def progress(
        self,
        *,
        columns: Optional[Iterable[ProgressColumn]] = None,
        additional_columns: Optional[Iterable[ProgressColumn]] = None,
        **kwargs,
    ) -> Progress:
        kwargs["console"] = self._console
        columns = columns or self.get_progress_default_columns()
        if additional_columns:
            columns = *columns, *additional_columns
        return Progress(
            *columns,
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
                    rich_progress.advance(task_id, percent)  # type: ignore[arg-type] # noqa: E501
            else:
                task_id = rich_progress.add_task(task_description, total=None)
                for _ in progress:
                    rich_progress.advance(task_id)

            rich_progress.update(task_id, total=1, completed=1)
