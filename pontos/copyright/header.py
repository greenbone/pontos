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

from datetime import datetime
from glob import glob
from pathlib import Path
from subprocess import SubprocessError, check_output


def main():
    parser = argparse.ArgumentParser(
        description="Update copyright in source file headers",
        prog="pontos-copyright",
    )
    parser.add_argument(
        "-c",
        "--changed",
        action="store_true",
        help="Only update actually changed files",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--files", nargs="+", help="Files to update")
    group.add_argument(
        "-d", "--directory", help="Directory to find files to update"
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

    for file in files:
        year_creation, year_modification, new_year_modification = (
            None,
            None,
            None,
        )
        try:
            content = file.read_text()
        except Exception:  # pylint: disable=broad-except
            print(str(file) + ": Unable to read file")
            continue

        # get copyright year(s)
        regex = re.compile(
            "[Cc]opyright.*?(19[0-9]{2}|20[0-9]{2}) "
            "?-? ?(19[0-9]{2}|20[0-9]{2})? (.reenbone*)"
        )

        copyright_holder = ""

        try:
            match = re.search(regex, content[0:500])
            if match.group(1):
                year_creation = match.group(1)
            if match.group(2):
                year_modification = match.group(2)
            if match.group(3):
                copyright_holder = match.group(3)
        except Exception:  # pylint: disable=broad-except
            print(str(file) + ": No Copyright information found")
            continue

        if args.changed:
            try:
                new_year_modification = check_output(
                    "cd {} && git log -1 --format='%ad' "
                    "--date='format:%Y' {}".format(file.parents[0], file.name),
                    shell=True,
                    universal_newlines=True,
                ).rstrip()
            except SubprocessError:
                print(
                    "Could not get date of last modification using git for "
                    + str(file)
                )
                continue

            if not new_year_modification:
                continue

            # check if new_year_modification match year regex
            if re.match("19[0-9]{2}|20[0-9]{2}", new_year_modification) is None:
                continue
        else:
            new_year_modification = str(datetime.now().year)

        if (
            not year_modification
            and year_creation < new_year_modification
            or year_modification
            and year_modification < new_year_modification
        ):
            print(
                "{}: {} -> {}".format(
                    str(file), year_modification, new_year_modification
                )
            )
            copyright_line = "Copyright (C) {}-{} {}".format(
                year_creation, new_year_modification, copyright_holder
            )

            # replace header and write file
            content = re.sub(regex, copyright_line, content)
            file.write_text(content)
        else:
            print(str(file) + ": OK")


if __name__ == "__main__":
    main()
