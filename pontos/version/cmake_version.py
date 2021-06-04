# Copyright (C) 2020 Greenbone Networks GmbH
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
import traceback

from typing import Tuple, Generator, Union
from pathlib import Path

from .version import (
    is_version_pep440_compliant,
    VersionError,
    initialize_default_parser,
)


class CMakeVersionCommand:
    __cmake_filepath = None
    __quiet = False

    def __init__(self, *, cmake_lists_path: Path = None):
        if not cmake_lists_path:
            cmake_lists_path = Path.cwd() / 'CMakeLists.txt'
        if not cmake_lists_path.exists():
            raise VersionError(
                '{} file not found.'.format(str(cmake_lists_path))
            )

        self.__cmake_filepath = cmake_lists_path
        self.parser = initialize_default_parser()

    def run(self, args=None) -> Union[int, str]:
        commandline_arguments = self.parser.parse_args(args)

        if not getattr(commandline_arguments, 'command', None):
            self.parser.print_usage()
            return 0

        self.__quiet = commandline_arguments.quiet

        try:
            if commandline_arguments.command == 'update':
                self.update_version(
                    commandline_arguments.version,
                    develop=commandline_arguments.develop,
                )
            elif commandline_arguments.command == 'show':
                self.print_current_version()
            elif commandline_arguments.command == 'verify':
                self.verify_version(commandline_arguments.version)
        except VersionError as e:
            traceback.print_exc()
            return str(e)

        return 0

    def __print(self, *args):
        if not self.__quiet:
            print(*args)

    def update_version(self, version: str, *, develop: bool = False):
        self.__print("in update: {}, {}".format(version, develop))
        content = self.__cmake_filepath.read_text()
        cmvp = CMakeVersionParser(content)
        previous_version = cmvp.get_current_version()
        new_content = cmvp.update_version(version, develop=develop)
        self.__cmake_filepath.write_text(new_content)
        self.__print(
            'Updated version from {} to {}'.format(previous_version, version)
        )

    def print_current_version(self):
        content = self.__cmake_filepath.read_text()
        cmvp = CMakeVersionParser(content)
        self.__print(cmvp.get_current_version())

    def get_current_version(self) -> str:
        content = self.__cmake_filepath.read_text()
        cmvp = CMakeVersionParser(content)
        return cmvp.get_current_version()

    def verify_version(self, version: str):
        if not is_version_pep440_compliant(version):
            raise VersionError(
                "Version {} is not PEP 440 compliant.".format(version)
            )

        self.__print('OK')


class CMakeVersionParser:
    def __init__(self, cmake_content_lines: str):
        line_no, current_version, pd_line_no, pd = self._find_version_in_cmake(
            cmake_content_lines
        )
        self._cmake_content_lines = cmake_content_lines.split('\n')
        self._version_line_number = line_no
        self._current_version = current_version
        self._project_dev_version_line_number = pd_line_no
        self._project_dev_version = pd

    __cmake_scanner = re.Scanner(
        [
            (r'#.*', lambda _, token: ("comment", token)),
            (r'"[^"]*"', lambda _, token: ("string", token)),
            (r'"[0-9]+"', lambda _, token: ("number", token)),
            (r"\(", lambda _, token: ("open_bracket", token)),
            (r"\)", lambda _, token: ("close_bracket", token)),
            (r'[^ \t\r\n()#"]+', lambda _, token: ("word", token)),
            (r'\n', lambda _, token: ("newline", token)),
            # to have spaces etc correctly
            (r"\s+", lambda _, token: ("special_printable", token)),
        ]
    )

    def get_current_version(self) -> str:
        return self._current_version

    def update_version(self, new_version: str, *, develop: bool = False) -> str:
        if not is_version_pep440_compliant(new_version):
            raise VersionError(
                "version {} is not pep 440 compliant.".format(new_version)
            )

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

        return '\n'.join(self._cmake_content_lines)

    def _find_version_in_cmake(self, content: str) -> Tuple[int, str]:
        in_project = False
        in_version = False

        version_line_no: int = None
        version: str = None

        in_set = False
        in_project_dev_version = False

        project_dev_version_line_no: int = None
        project_dev_version: int = None

        for lineno, token_type, value in self._tokenize(content):
            if token_type == 'word' and value == 'project':
                in_project = True
            elif in_project and token_type == 'word' and value == 'VERSION':
                in_version = True
            elif in_version and (
                token_type == 'word' or token_type == 'string'
            ):
                version_line_no = lineno
                version = value
                in_project = False
                in_version = False
            elif token_type == 'word' and value == 'set':
                in_set = True
            elif (
                in_set
                and token_type == 'word'
                and value == 'PROJECT_DEV_VERSION'
            ):
                in_project_dev_version = True
            elif in_project_dev_version and (
                token_type == 'word' or token_type == 'number'
            ):
                project_dev_version_line_no = lineno
                project_dev_version = value
                in_project_dev_version = False
            elif in_project and token_type == 'close_bracket':
                raise ValueError('unable to find cmake version in project.')

        if not version or version_line_no is None:
            raise ValueError('unable to find cmake version.')
        return (
            version_line_no,
            version,
            project_dev_version_line_no,
            project_dev_version,
        )

    def _tokenize(
        self, content: str
    ) -> Generator[
        Tuple[int, str, str],
        Tuple[int, str, str],
        Tuple[int, str, str],
    ]:
        toks, remainder = self.__cmake_scanner.scan(content)
        if remainder != '':
            print('WARNING: unrecognized cmake tokens: {}'.format(remainder))

        line_num = 0

        for tok_type, tok_contents in toks:
            line_num += tok_contents.count('\n')
            yield line_num, tok_type, tok_contents.strip()
