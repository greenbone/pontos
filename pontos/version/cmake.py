# Copyright (C) 2020-2022 Greenbone Networks GmbH
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


import re
from typing import Generator, Literal, Optional, Tuple, Union

from pontos.version.errors import VersionError

from .version import Version, VersionCommand, VersionUpdate, parse_version


class CMakeVersionCommand(VersionCommand):
    project_file_name = "CMakeLists.txt"

    def update_version(
        self, new_version: Version, *, force: bool = False
    ) -> VersionUpdate:
        content = self.project_file_path.read_text(encoding="utf-8")
        cmake_version_parser = CMakeVersionParser(content)
        previous_version = self.get_current_version()

        if not force and new_version == previous_version:
            return VersionUpdate(previous=previous_version, new=new_version)

        new_content = cmake_version_parser.update_version(new_version)
        self.project_file_path.write_text(new_content, encoding="utf-8")
        return VersionUpdate(
            previous=previous_version,
            new=new_version,
            changed_files=[self.project_file_path],
        )

    def get_current_version(self) -> Version:
        content = self.project_file_path.read_text(encoding="utf-8")
        return CMakeVersionParser(content).get_current_version()

    def verify_version(
        self, version: Union[Literal["current"], Version]
    ) -> None:
        current_version = self.get_current_version()
        if current_version != version:
            raise VersionError(
                f"Provided version {version} does not match the "
                f"current version {current_version}."
            )


class CMakeVersionParser:
    def __init__(self, cmake_content_lines: str):
        line_no, current_version, pd_line_no, pd = self._find_version_in_cmake(
            cmake_content_lines
        )
        self._cmake_content_lines = cmake_content_lines.split("\n")
        self._version_line_number = line_no
        self._current_version = current_version
        self._project_dev_version_line_number = pd_line_no
        self._project_dev_version = pd

    __cmake_scanner = re.Scanner(  # type: ignore
        [
            (r"#.*", lambda _, token: ("comment", token)),
            (r'"[^"]*"', lambda _, token: ("string", token)),
            (r'"[0-9]+"', lambda _, token: ("number", token)),
            (r"\(", lambda _, token: ("open_bracket", token)),
            (r"\)", lambda _, token: ("close_bracket", token)),
            (r'[^ \t\r\n()#"]+', lambda _, token: ("word", token)),
            (r"\n", lambda _, token: ("newline", token)),
            # to have spaces etc correctly
            (r"\s+", lambda _, token: ("special_printable", token)),
        ]
    )

    def get_current_version(self) -> Version:
        return (
            parse_version(f"{self._current_version}.dev1")
            if self.is_dev_version()
            else parse_version(self._current_version)
        )

    def update_version(self, new_version: Version) -> str:
        if new_version.is_devrelease:
            new_version = parse_version(
                f"{str(new_version.major)}."
                f"{str(new_version.minor)}."
                f"{str(new_version.micro)}"
            )
            develop = True
        else:
            develop = False

        to_update = self._cmake_content_lines[self._version_line_number]
        updated = to_update.replace(self._current_version, str(new_version))
        self._cmake_content_lines[self._version_line_number] = updated
        self._current_version = new_version
        if self._project_dev_version_line_number:
            self._cmake_content_lines[
                self._project_dev_version_line_number
            ] = self._cmake_content_lines[
                self._project_dev_version_line_number
            ].replace(
                str(int(not develop)), str(int(develop))
            )
            self._project_dev_version = str(int(develop))

        return "\n".join(self._cmake_content_lines)

    def _find_version_in_cmake(
        self, content: str
    ) -> Tuple[int, str, Optional[int], Optional[str]]:
        in_project = False
        in_version = False

        version_line_no: Optional[int] = None
        version: Optional[str] = None

        in_set = False
        in_project_dev_version = False

        project_dev_version_line_no: Optional[int] = None
        project_dev_version: Optional[str] = None

        for lineno, token_type, value in self._tokenize(content):
            if token_type == "word" and value == "project":
                in_project = True
            elif in_project and token_type == "word" and value == "VERSION":
                in_version = True
            elif in_version and (
                token_type == "word" or token_type == "string"
            ):
                version_line_no = lineno
                version = value
                in_project = False
                in_version = False
            elif token_type == "word" and value == "set":
                in_set = True
            elif in_set and token_type == "close_bracket":
                in_set = False
            elif (
                in_set
                and token_type == "word"
                and value == "PROJECT_DEV_VERSION"
            ):
                in_project_dev_version = True
            elif in_project_dev_version and (
                token_type == "word" or token_type == "number"
            ):
                project_dev_version_line_no = lineno
                project_dev_version = value
                in_project_dev_version = False
            elif in_project and token_type == "close_bracket":
                raise ValueError("unable to find cmake version in project.")

        if not version or version_line_no is None:
            raise ValueError("unable to find cmake version.")
        return (
            version_line_no,
            version,
            project_dev_version_line_no,
            project_dev_version,
        )

    def is_dev_version(self) -> bool:
        return (
            int(self._project_dev_version) == 1
            if self._project_dev_version
            else False
        )

    def _tokenize(  # type: ignore
        self, content: str
    ) -> Generator[
        Tuple[int, str, str],
        Tuple[int, str, str],
        Tuple[int, str, str],
    ]:
        toks, remainder = self.__cmake_scanner.scan(content)
        if remainder != "":
            print(f"WARNING: unrecognized cmake tokens: {remainder}")

        line_num = 0

        for tok_type, tok_contents in toks:
            line_num += tok_contents.count("\n")
            yield line_num, tok_type, tok_contents.strip()
