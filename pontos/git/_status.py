# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from enum import Enum
from pathlib import Path
from typing import Iterator


class Status(Enum):
    """
    Status of a file in git
    """

    UNMODIFIED = " "
    MODIFIED = "M"
    ADDED = "A"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UPDATED = "U"
    UNTRACKED = "?"
    IGNORED = "!"


class StatusEntry:
    """
    Status of a file in the git index and working tree.

    Implements the :py:class:`os.PathLike` protocol.

    Attributes:
        index: Status in the index
        working_tree: Status in the working tree
        path: Path to the file
        old_path: Set for renamed files
    """

    def __init__(self, status_string: str) -> None:
        status = status_string[:2]
        filename = status_string[3:]

        # Status in the index
        self.index = Status(status[0])
        # Status in the working directory
        self.working_tree = Status(status[1])

        if self.index == Status.RENAMED:
            new_filename, old_filename = filename.split("\0")
            self.path = Path(new_filename)
            self.old_path = Path(old_filename)
        else:
            # path of the file in git
            self.path = Path(filename)

    def __str__(self) -> str:
        return f"{self.index.value}{self.working_tree.value} {self.path}"

    def __repr__(self) -> str:
        return f"<StatusEntry {str(self)}>"

    def __fspath__(self):
        return self.path.__fspath__()


def parse_git_status(output: str) -> Iterator[StatusEntry]:
    output = output.rstrip("\0")
    if not output:
        return

    output_list = output.split("\0")
    while output_list:
        line = output_list.pop(0)
        if line[0] == Status.RENAMED.value:
            yield StatusEntry(f"{line}\0{output_list.pop(0)}")
        else:
            yield StatusEntry(line)
