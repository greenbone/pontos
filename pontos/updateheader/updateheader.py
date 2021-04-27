# Copyright (C) 2019-2021 Greenbone Networks GmbH
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

"""Script to update the year of last modification
in the license header of source code files.\n
Also it appends a header if it is missing in the file.
"""

import sys
import os
import re

from argparse import ArgumentParser, Namespace
from datetime import datetime
from glob import glob

from subprocess import CalledProcessError, run
from typing import Dict, Tuple, Union
from pathlib import Path

SUPPORTED_FILE_TYPES = [
    ".bash",
    ".c",
    ".h",
    ".cmake",
    ".js",
    ".nasl",
    ".po",
    ".py",
    ".sh",
    ".txt",
    ".xml",
]
SUPPORTED_LICENCES = [
    "AGPL-3.0-or-later",
    "GPL-2.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0-or-later",
]


def _get_modified_year(f: Path) -> str:
    """In case of the changed arg, update year to last modified year"""
    try:
        cmd = ["git", "log", "-1", "--format=%ad", "--date=format:%Y", str(f)]
        proc = run(
            cmd,
            text=True,
            capture_output=True,
            check=True,
            universal_newlines=True,
        )
        return proc.stdout.rstrip()
    except CalledProcessError as e:
        raise e


def _find_copyright(
    line: str,
    regex: re.Pattern,
) -> Tuple[bool, Union[Dict[str, Union[str, None]], None]]:
    """Match the line for the regex"""
    copyright_match = re.search(regex, line)
    if copyright_match:
        return (
            True,
            {
                "creation_year": copyright_match.group(1),
                "modification_year": copyright_match.group(2),
                "company": copyright_match.group(3),
            },
        )
    return False, None


def _add_header(suffix: str, licence: str, company: str) -> Union[str, None]:
    """Tries to add the header to the file.
    Requirements:
      - file type must be supported
      - licence file must exist
    """
    if suffix in SUPPORTED_FILE_TYPES:
        root = Path(__file__).parent
        licence_file = root / "templates" / licence / f"template{suffix}"
        try:
            return licence_file.read_text().replace("Company", company)
        except FileNotFoundError as e:
            raise e
    else:
        raise ValueError


def _update_file(
    file: Path,
    regex: re.Pattern,
    args: Namespace,
) -> None:
    """Function to update the given file.
    Checks if header exists. If not it adds an
    header to that file, else it checks if year
    is up to date
    """

    if args.changed:
        try:
            args.year = _get_modified_year(file)
        except CalledProcessError:
            print(
                f"{file}: Could not get date of last modification"
                f" using git, using {str(args.year)} instead."
            )

    try:
        with file.open("r+") as fp:
            found = False
            i = 10  # assume that copyright is in the first 10 lines
            while not found and i > 0:
                line = fp.readline()
                if line == "":
                    i = 0
                    continue
                found, copyright_match = _find_copyright(line=line, regex=regex)
                i = i - 1
            if i == 0 and not found:
                try:
                    header = _add_header(
                        file.suffix, args.licence, args.company
                    )
                    if header:
                        fp.seek(0)  # back to beginning of file
                        rest_of_file = fp.read()
                        fp.seek(0)
                        fp.write(header)
                        fp.write(rest_of_file)
                        print(f"{file}: Added licence header.")
                        return 0
                except ValueError:
                    print(
                        f"{file}: No licence header for the"
                        f" format {file.suffix} found.",
                    )
                except FileNotFoundError:
                    print(
                        f"{file}: Licence file for {args.licence} "
                        "is not existing."
                    )
                return 1
            # replace header and write it to file
            if (
                not copyright_match["modification_year"]
                and copyright_match["creation_year"] < args.year
                or copyright_match["modification_year"]
                and copyright_match["modification_year"] < args.year
            ):
                copyright_term = (
                    f'Copyright (C) {copyright_match["creation_year"]}'
                    f'-{args.year} {copyright_match["company"]}'
                )
                new_line = re.sub(regex, copyright_term, line)
                fp_write = fp.tell() - len(line)  # save position to insert
                rest_of_file = fp.read()
                fp.seek(fp_write)
                fp.write(new_line)
                fp.write(rest_of_file)
                print(
                    f"{file}: Changed Licence Header Copyright Year "
                    f'{copyright_match["modification_year"]} -> '
                    f"{args.year}"
                )

                return 0
            else:
                print(f"{file}: Licence Header is ok.")
                return 0
    except FileNotFoundError as e:
        print(f"{file}: File is not existing.")
        raise e
    except UnicodeDecodeError as e:
        print(f"{file}: Ignoring binary file.")
        raise e


def _parse_args(args=None):
    """Parsing the args"""

    parser = ArgumentParser(
        description="Update copyright in source file headers.",
        prog="pontos-copyright",
    )

    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        "-c",
        "--changed",
        action="store_true",
        default=False,
        help=(
            "Update modified year using git log modified year. \n"
            "This will probably not changed all files to current year!",
        ),
    )
    date_group.add_argument(
        "-y",
        "--year",
        default=str(datetime.now().year),
        help=(
            "If year is set, modified year will be \n"
            "set to the specified year."
        ),
    )

    parser.add_argument(
        "-l",
        "--licence",
        choices=SUPPORTED_LICENCES,
        default="GPL-3.0-or-later",
        help="Add header f files",
    )

    parser.add_argument(
        "--company",
        default="Greenbone Networks GmbH",
        help=(
            "If a header will be added to file, \n"
            "it will be licenced by company."
        ),
    )

    files_group = parser.add_mutually_exclusive_group(required=True)
    files_group.add_argument(
        "-f", "--files", nargs="+", help="Files to update."
    )
    files_group.add_argument(
        "-d",
        "--directory",
        help="Directory to find files to update recursively.",
    )
    return parser.parse_args(args)


def main() -> None:
    args = _parse_args()

    if args.directory:
        # get files to update
        files = [
            Path(file)
            for file in glob(args.directory + "/**/*", recursive=True)
            if os.path.isfile(file)
        ]
    elif args.files:
        files = [Path(name) for name in args.files]

    else:
        # should never happen
        print("Specify files to update!")
        sys.exit(1)

    regex = re.compile(
        "[Cc]opyright.*?(19[0-9]{2}|20[0-9]{2}) "
        f"?-? ?(19[0-9]{{2}}|20[0-9]{{2}})? ({args.company})"
    )

    for file in files:
        try:
            _update_file(file=file, regex=regex, args=args)
        except (FileNotFoundError, UnicodeDecodeError, ValueError):
            continue

    return 0


if __name__ == "__main__":
    main()
