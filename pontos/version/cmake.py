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
from typing import Generator, Optional, Tuple

from packaging.version import Version

from .helper import (
    VersionError,
    check_develop,
    is_version_pep440_compliant,
    safe_version,
    versions_equal,
)
from .version import UpdatedVersion, VersionCommand


class CMakeVersionCommand(VersionCommand):
    project_file_name = "CMakeLists.txt"

    def update_version(
        self, new_version: str, *, develop: bool = False, force: bool = False
    ) -> UpdatedVersion:
        content = self.project_file_path.read_text(encoding="utf-8")
        cmvp = CMakeVersionParser(content)
        previous_version = self.get_current_version()

        if not force and versions_equal(new_version, previous_version):
            return UpdatedVersion(previous=previous_version, new=new_version)

        new_content = cmvp.update_version(new_version, develop=develop)
        self.project_file_path.write_text(new_content, encoding="utf-8")
        return UpdatedVersion(previous=previous_version, new=new_version)

    def get_current_version(self) -> str:
        content = self.project_file_path.read_text(encoding="utf-8")
        return CMakeVersionParser(content).get_current_version()

    def verify_version(self, version: str) -> None:
        current_version = self.get_current_version()
        if not is_version_pep440_compliant(current_version):
            raise VersionError(
                f"The version {current_version} is not PEP 440 compliant."
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

    def get_current_version(self) -> str:
        if self.is_dev_version():
            return f"{self._current_version}.dev1"
        return self._current_version

    def update_version(self, new_version: str, *, develop: bool = False) -> str:
        if not is_version_pep440_compliant(new_version):
            raise VersionError(
                f"version {new_version} is not pep 440 compliant."
            )

        new_version = safe_version(new_version)
        if check_develop(new_version):
            vers = Version(new_version)
            if vers.dev is not None:
                new_version = str(
                    Version(
                        f"{str(vers.major)}.{str(vers.minor)}"
                        f".{str(vers.micro)}"
                    )
                )
            develop = True

        to_update = self._cmake_content_lines[self._version_line_number]
        updated = to_update.replace(self._current_version, new_version)
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
