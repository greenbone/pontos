# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later


from argparse import ArgumentParser, FileType, Namespace
from datetime import datetime
from typing import Optional, Sequence

import shtab

SUPPORTED_LICENSES = [
    "AGPL-3.0-or-later",
    "GPL-2.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0-or-later",
]


def parse_args(args: Optional[Sequence[str]] = None) -> Namespace:
    """Parsing the args"""

    parser = ArgumentParser(
        description="Update copyright in source file headers.",
    )
    shtab.add_argument_to(parser)

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Don't print messages to the terminal",
    )

    parser.add_argument(
        "--log-file",
        dest="log_file",
        type=str,
        help="Activate logging using the given file path",
    ).complete = shtab.FILE  # type: ignore[attr-defined]

    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        "-c",
        "--changed",
        action="store_true",
        default=False,
        help=(
            "Update modified year using git log modified year. "
            "This will not changed all files to current year!"
        ),
    )
    date_group.add_argument(
        "-y",
        "--year",
        default=str(datetime.now().year),
        help=(
            "If year is set, modified year will be "
            "set to the specified year."
        ),
    )

    parser.add_argument(
        "-l",
        "--license",
        dest="license_id",
        choices=SUPPORTED_LICENSES,
        default="GPL-3.0-or-later",
        help=("Use the passed license type"),
    )

    parser.add_argument(
        "--company",
        default="Greenbone AG",
        help=(
            "If a header will be added to file, "
            "it will be licensed by company."
        ),
    )

    files_group = parser.add_mutually_exclusive_group(required=True)
    files_group.add_argument(
        "-f", "--files", nargs="+", help="Files to update."
    ).complete = shtab.FILE  # type: ignore[attr-defined]
    files_group.add_argument(
        "-d",
        "--directories",
        nargs="+",
        help="Directories to find files to update recursively.",
    ).complete = shtab.DIRECTORY  # type: ignore[attr-defined]

    parser.add_argument(
        "--exclude-file",
        help=(
            "File containing glob patterns for files to "
            "ignore when finding files to update in a directory. "
            "Will look for '.pontos-header-ignore' in the directory "
            "if none is given. "
            "The ignore file should only contain relative paths like *.py,"
            "not absolute as **/*.py"
        ),
        type=FileType("r"),
    ).complete = shtab.FILE  # type: ignore[attr-defined]

    parser.add_argument(
        "--cleanup",
        action="store_true",
        default=False,
        help="Do a cleanup: Remove lines from outdated header format",
    )

    return parser.parse_args(args)
