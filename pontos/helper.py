# -*- coding: utf-8 -*-
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

import subprocess
from pathlib import Path
from typing import Iterable, Iterator, Optional


class DownloadProgressIterable:
    def __init__(
        self, content_iterator: Iterator, destination: Path, length: int
    ):
        self._length = None if length is None else int(length)
        self._content_iterator = content_iterator
        self._destination = destination

    @property
    def length(self) -> Optional[int]:
        """
        Size in bytes of the to be downloaded file or None if the size is not
        available
        """
        return self._length

    @property
    def destination(self) -> Path:
        """
        Destination path of the to be downloaded file
        """
        return self._destination

    def _download(self) -> Iterator[Optional[float]]:
        dl = 0
        with self._destination.open("wb") as f:
            for content in self._content_iterator:
                dl += len(content)
                f.write(content)
                yield dl / self._length if self._length else None

    def __iter__(self) -> Iterator[Optional[float]]:
        return self._download()

    def run(self):
        """
        Just run the download without caring about the progress
        """
        try:
            it = iter(self)
            while True:
                next(it)
        except StopIteration:
            pass


def shell_cmd_runner(args: Iterable[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        shell=True,
        check=True,
        errors="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
