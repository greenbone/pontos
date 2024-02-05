# SPDX-FileCopyrightText: 2019-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Script to update the year of last modification
in the license header of source code files.\n
Also it appends a header if it is missing in the file.
"""

import re
import sys
from argparse import Namespace
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Dict, List, Optional, Tuple, Union

from pontos.terminal import Terminal
from pontos.terminal.null import NullTerminal
from pontos.terminal.rich import RichTerminal

from ._parser import parse_args

SUPPORTED_FILE_TYPES = [
    ".bash",
    ".c",
    ".h",
    ".go",
    ".cmake",
    ".js",
    ".nasl",
    ".po",
    ".py",
    ".sh",
    ".txt",
    ".xml",
    ".xsl",
]
OLD_LINES = [
    "# \-\*\- coding: utf\-8 \-\*\-",
    "This program is free software: you can redistribute it and/or modify",
    "it under the terms of the GNU Affero General Public License as",
    "published by the Free Software Foundation, either version 3 of the",
    "License, or \(at your option\) any later version.",
    "This program is free software; you can redistribute it and/or",
    "modify it under the terms of the GNU General Public License",
    "version 2 as published by the Free Software Foundation.",
    "This program is free software: you can redistribute it and/or modify",
    "it under the terms of the GNU General Public License as published by",
    "the Free Software Foundation, either version 3 of the License, or",
    "\(at your option\) any later version.",
    "This program is distributed in the hope that it will be useful,",
    "but WITHOUT ANY WARRANTY; without even the implied warranty of",
    "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the",
    "GNU Affero General Public License for more details.",
    "GNU General Public License for more details.",
    "You should have received a copy of the GNU Affero General Public License",
    "You should have received a copy of the GNU General Public License",
    "along with this program.  If not, see <http://www.gnu.org/licenses/>.",
    "along with this program; if not, write to the Free Software",
    "Foundation, Inc\., 51 Franklin St, Fifth Floor, Boston, MA 02110\-1301 USA\.",  # noqa: E501
]
OLD_COMPANY = "Greenbone Networks GmbH"


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
    copyright_regex: re.Pattern,
) -> Tuple[bool, Union[Dict[str, Union[str, None]], None]]:
    """Match the line for the copyright_regex"""
    copyright_match = re.search(copyright_regex, line)
    if copyright_match:
        return (
            True,
            {
                "creation_year": copyright_match.group(2),
                "modification_year": copyright_match.group(3),
                "company": copyright_match.group(4),
            },
        )
    return False, None


def _add_header(
    suffix: str, license_id: str, company: str, year: str
) -> Union[str, None]:
    """Tries to add the header to the file.
    Requirements:
      - file type must be supported
      - license file must exist
    """
    if suffix in SUPPORTED_FILE_TYPES:
        root = Path(__file__).parent
        license_file = root / "templates" / license_id / f"template{suffix}"
        try:
            return (
                license_file.read_text(encoding="utf-8")
                .replace("<company>", company)
                .replace("<year>", year)
            )
        except FileNotFoundError as e:
            raise e
    else:
        raise ValueError


def _remove_outdated_lines(
    content: str, cleanup_regexes: List[re.Pattern]
) -> Optional[str]:
    """Remove lines that contain outdated copyright header ..."""
    changed = False
    splitted_lines = content.splitlines()
    i = 0
    for line in splitted_lines[:20]:
        if i > 3 and re.match(r"^(([#*]|//) ?$)", line):
            splitted_lines.pop(i)
            continue
        for regex in cleanup_regexes:
            if regex.match(line):
                changed = True
                splitted_lines.pop(i)
                i = i - 1
                break
        i = i + 1
    if changed:
        new_content = "\n".join(splitted_lines) + "\n"
        return new_content
    return None


def _update_file(
    file: Path,
    copyright_regex: re.Pattern,
    parsed_args: Namespace,
    term: Terminal,
    cleanup_regexes: Optional[List[re.Pattern]] = None,
) -> int:
    """Function to update the given file.
    Checks if header exists. If not it adds an
    header to that file, else it checks if year
    is up to date
    """

    if parsed_args.changed:
        try:
            parsed_args.year = _get_modified_year(file)
        except CalledProcessError:
            term.warning(
                f"{file}: Could not get date of last modification"
                f" using git, using {str(parsed_args.year)} instead."
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
                found, copyright_match = _find_copyright(
                    line=line, copyright_regex=copyright_regex
                )
                i = i - 1
            # header not found, add header
            if i == 0 and not found:
                try:
                    header = _add_header(
                        file.suffix,
                        parsed_args.license_id,
                        parsed_args.company,
                        parsed_args.year,
                    )
                    if header:
                        fp.seek(0)  # back to beginning of file
                        rest_of_file = fp.read()
                        fp.seek(0)
                        fp.write(header + "\n" + rest_of_file)
                        print(f"{file}: Added license header.")
                        return 0
                except ValueError:
                    print(
                        f"{file}: No license header for the"
                        f" format {file.suffix} found.",
                    )
                except FileNotFoundError:
                    print(
                        f"{file}: License file for {parsed_args.license_id} "
                        "is not existing."
                    )
                return 1
            # replace found header and write it to file
            if copyright_match and (
                not copyright_match["modification_year"]
                and copyright_match["creation_year"] < parsed_args.year
                or copyright_match["modification_year"]
                and copyright_match["modification_year"] < parsed_args.year
            ):
                copyright_term = (
                    f"SPDX-FileCopyrightText: "
                    f'{copyright_match["creation_year"]}'
                    f"-{parsed_args.year} {parsed_args.company}"
                )
                new_line = re.sub(copyright_regex, copyright_term, line)
                fp_write = fp.tell() - len(line)  # save position to insert
                rest_of_file = fp.read()
                fp.seek(fp_write)
                fp.write(new_line)
                fp.write(rest_of_file)
                # in some cases we replace "YYYY - YYYY" with "YYYY-YYYY"
                # resulting in 2 characters left at the end of the file
                # so we truncate the file, just in case!
                fp.truncate()
                print(
                    f"{file}: Changed License Header Copyright Year "
                    f'{copyright_match["modification_year"]} -> '
                    f"{parsed_args.year}"
                )

            else:
                print(f"{file}: License Header is ok.")
    except FileNotFoundError as e:
        print(f"{file}: File is not existing.")
        raise e
    except UnicodeDecodeError as e:
        print(f"{file}: Ignoring binary file.")
        raise e
    # old header existing - cleanup?
    if cleanup_regexes:
        old_content = file.read_text(encoding="utf-8")
        new_content = _remove_outdated_lines(
            content=old_content, cleanup_regexes=cleanup_regexes
        )
        if new_content:
            file.write_text(new_content, encoding="utf-8")
            print(f"{file}: Cleaned up!")
    return 0


def _get_exclude_list(
    exclude_file: Path, directories: List[Path]
) -> List[Path]:
    """Tries to get the list of excluded files / directories.
    If a file is given, it will be used. Otherwise it will be searched
    in the executed root path.
    The ignore file should only contain relative paths like *.py,
    not absolute as **/*.py
    """

    if exclude_file is None:
        exclude_file = Path(".pontos-header-ignore")
    try:
        exclude_lines = exclude_file.read_text(encoding="utf-8").split("\n")
    except FileNotFoundError:
        print("No exclude list file found.")
        return []

    expanded_globs = [
        directory.rglob(line.strip())
        for directory in directories
        for line in exclude_lines
        if line
    ]

    exclude_list = []
    for glob_paths in expanded_globs:
        for path in glob_paths:
            if path.is_dir():
                for efile in path.rglob("*"):
                    exclude_list.append(efile.absolute())
            else:
                exclude_list.append(path.absolute())

    return exclude_list


def _compile_outdated_regex() -> List[re.Pattern]:
    """prepare regex patterns to remove old copyright lines"""
    regexes: List[re.Pattern] = []
    for line in OLD_LINES:
        regexes.append(re.compile(rf"^(([#*]|//) ?)?{line}"))
    return regexes


def _compile_copyright_regex(company: Union[str, List[str]]) -> re.Pattern:
    """prepare the copyright regex"""
    c_str = r"(SPDX-FileCopyrightText:|[Cc]opyright)"
    d_str = r"(19[0-9]{2}|20[0-9]{2})"

    if isinstance(company, str):
        return re.compile(rf"{c_str}.*? {d_str}?-? ?{d_str}? ({company})")
    return re.compile(rf"{c_str}.*? {d_str}?-? ?{d_str}? ({'|'.join(company)})")


def main() -> None:
    parsed_args = parse_args()
    exclude_list = []

    if parsed_args.quiet:
        term: Union[NullTerminal, RichTerminal] = NullTerminal()
    else:
        term = RichTerminal()

    term.bold_info("pontos-update-header")

    if parsed_args.directories:
        if isinstance(parsed_args.directories, list):
            directories = [
                Path(directory) for directory in parsed_args.directories
            ]
        else:
            directories = [Path(parsed_args.directories)]
        # get file paths to exclude
        exclude_list = _get_exclude_list(parsed_args.exclude_file, directories)
        # get files to update
        files = [
            Path(file)
            for directory in directories
            for file in directory.rglob("*")
            if file.is_file()
        ]
    elif parsed_args.files:
        if isinstance(parsed_args.files, list):
            files = [Path(name) for name in parsed_args.files]
        else:
            files = [Path(parsed_args.files)]

    else:
        # should never happen
        term.error("Specify files to update!")
        sys.exit(1)

    copyright_regex: re.Pattern = _compile_copyright_regex(
        company=[parsed_args.company, OLD_COMPANY]
    )

    cleanup_regexes: Optional[List[re.Pattern]] = None
    if parsed_args.cleanup:
        cleanup_regexes = _compile_outdated_regex()

    for file in files:
        try:
            if file.absolute() in exclude_list:
                term.warning(f"{file}: Ignoring file from exclusion list.")
            else:
                _update_file(
                    file=file,
                    copyright_regex=copyright_regex,
                    parsed_args=parsed_args,
                    term=term,
                    cleanup_regexes=cleanup_regexes,
                )
        except (FileNotFoundError, UnicodeDecodeError, ValueError):
            continue


if __name__ == "__main__":
    main()
