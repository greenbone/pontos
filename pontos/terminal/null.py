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
