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
in the license header of source code files.
"""

import sys
import os
import argparse
import re

from typing import Dict, Tuple, Union
from datetime import datetime
from glob import glob
from pathlib import Path
from subprocess import SubprocessError, check_output

SUPPORTED_FILE_TYPES = ['.bash', '.c', '.cmake', '.js', '.nasl', '.po', '.py', '.sh', '.txt', '.xml']
SUPPORTED_LICENCES = ['AGPL-3.0-or-later', 'GPL-2.0-only', 'GPL-2.0-or-later', 'GPL-3.0-or-later']

def _get_modified_year(f: Path) -> str:
    return check_output(
        f"cd {f.parents[0]} && git log -1 "
        f"--format='%ad' --date='format:%Y' {f.name}",
        shell=True,
        universal_newlines=True,
    ).rstrip()

def _find_copyright(
    line: str,
    regex: re.Pattern,
) -> Tuple[bool, Union[Dict[str, Union[str, None]], None]]:
    copyright_match = re.search(regex, line)
    if copyright_match:
        return (
            True,
            {
                'creation_year': copyright_match.group(1),
                'modification_year': copyright_match.group(2),
                'company': copyright_match.group(3),
            },
        )
    return False, None

def _add_header(suffix: str, licence: str, company: str) -> Union[str, None]:
    header = None
    if suffix in SUPPORTED_FILE_TYPES:
        root = Path(__file__).parent
        licence_file = root / 'templates' / licence / f'template{suffix}'
        try:
            header = licence_file.read_text().replace('Company', company)
        except IOError:
            print(f"Licence file {licence_file} is not existing.")
    return header

def _update_year(
    file: Path,
    new_modified_year: str,
    licence: str,
    company: str
) -> None:
    # copyright year(s) regex
    regex = re.compile(
        "[Cc]opyright.*?(19[0-9]{2}|20[0-9]{2}) "
        "?-? ?(19[0-9]{2}|20[0-9]{2})? (.reenbone*)"
    )

    with open(file, "r+") as fp:
        try:
            found = False
            i = 10 # assume that copyright is in the first 10 lines
            while not found and i > 0:
                line = fp.readline()
                if line == '':
                    i = 0
                    continue
                found, copyright_match = _find_copyright(line=line, regex=regex)
                i = i - 1
            if i == 0 and not found:
                header = _add_header(file.suffix, licence, company)
                if header:
                    fp.seek(0) # back to beginning of file
                    rest_of_file = fp.read()
                    fp.seek(0)
                    print(header)
                    fp.write(header)
                    fp.write(rest_of_file)
                    print(f"{file}: Added licence header to ")
                else:
                    print(f"{file}: No licence header found in")
                return
            # replace header and write it to file
            if (
                not copyright_match['modification_year']
                and copyright_match['creation_year'] < new_modified_year
                or copyright_match['modification_year'] 
                and copyright_match['modification_year'] < new_modified_year
            ):
                copyright_term = (
                    f'Copyright (C) {copyright_match["creation_year"]}'
                    f'-{new_modified_year} {copyright_match["company"]}'
                )
                new_line = re.sub(regex, copyright_term, line)
                fp_write = fp.tell() - len(line) # save position to insert
                rest_of_file = fp.read()
                fp.seek(fp_write)
                fp.write(new_line)
                fp.write(rest_of_file)
                print(
                    f'{file}: Changed Licence Header Copyright Year '
                    f'{copyright_match["modification_year"]} -> {new_modified_year}'
                )
            else:
                print(f'{file}: Licence Header is ok.')
        except IOError:
            print(f'{file}: Unable to read')
        except UnicodeDecodeError:
            print(f'{file}: Ignoring binary file.')


def main():
    parser = argparse.ArgumentParser(
        description="Update copyright in source file headers.",
        prog="pontos-copyright",
    )

    parser.add_argument(
        "-c",
        "--changed",
        action="store_true",
        help="Only update actually changed files.",
    )

    parser.add_argument(
        "-l",
        "--licence",
        choices=SUPPORTED_LICENCES,
        default='GPL-3.0-or-later',
        help="Add header f files",
    )

    parser.add_argument(
        "--company",
        default='Greenbone Networks GmbH',
        help=(
            "If a header will be added to file, \n"
            "it will be licenced by company."
        ),
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--files", nargs="+", help="Files to update.")
    group.add_argument(
        "-d",
        "--directory",
        help="Directory to find files to update recursively.",
    )
    args = parser.parse_args()

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

    this_year = str(datetime.now().year)

    for file in files:
        if args.changed:
            try:
                mod_year = _get_modified_year(file)
                _update_year(
                    file=file,
                    new_modified_year=mod_year,
                    licence=args.licence,
                    company=args.company
                )
                continue
            except SubprocessError:
                print(
                    f"{file}: Could not get date of last modification"
                    f" using git, using {str(this_year)} instead."
                )
        _update_year(
            file=file,
            new_modified_year=this_year,
            licence=args.licence,
            company=args.company,
        )

if __name__ == "__main__":
    main()
