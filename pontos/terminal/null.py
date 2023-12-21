# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from contextlib import contextmanager
from typing import Any, Generator

from pontos.helper import DownloadProgressIterable

from .terminal import Terminal


class NullTerminal(Terminal):
    """A terminal implementation to keep the terminal quiet"""

    @contextmanager
    def indent(self, indentation: int = 4) -> Generator[None, None, None]:
        yield

    def out(self, *messages: Any, **kwargs: Any) -> None:
        pass

    def print(self, *messages: Any, **kwargs: Any) -> None:
        pass

    def ok(self, *messages: Any, **kwargs: Any) -> None:
        pass

    def fail(self, *messages: Any, **kwargs: Any) -> None:
        pass

    def error(self, *messages: Any, **kwargs: Any) -> None:
        pass

    def warning(self, *messages: Any, **kwargs: Any) -> None:
        pass

    def info(self, *messages: Any, **kwargs: Any) -> None:
        pass

    def bold_info(self, *messages: Any, **kwargs: Any) -> None:
        pass

    def download_progress(self, progress: DownloadProgressIterable) -> None:
        progress.run()
