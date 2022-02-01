# Copyright (C) 2022 Greenbone Networks GmbH
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

# pylint: disable=no-member

from argparse import Namespace
import io
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from pontos.github.api import FileStatus

from pontos.github.cmds import file_status
from pontos.terminal import _set_terminal

here = Path(__file__).parent


class TestArgparsing(unittest.TestCase):
    def setUp(self):
        self.term = Mock()
        _set_terminal(self.term)

    @patch("pontos.github.cmds.GitHubRESTApi")
    def test_file_status(self, api_mock):
        api_mock.return_value.pull_request_exists.return_value = True
        api_mock.return_value.pull_request_files.return_value = {
            FileStatus.ADDED: [Path('tests/github/foo/bar')],
            FileStatus.MODIFIED: [
                Path("tests/github/bar/baz"),
                Path("tests/github/baz/boo"),
            ],
        }
        test_file = Path("some.file")
        output = io.open(test_file, mode='w', encoding='utf-8')

        args = Namespace(
            command='FS',
            func=file_status,
            repo='foo/bar',
            pull_request=8,
            output=output,
            status=[FileStatus.ADDED, FileStatus.MODIFIED],
            token='GITHUB_TOKEN',
        )

        file_status(args)

        output.close()

        content = test_file.read_text(encoding='utf-8')
        self.assertEqual(
            content, f"{here}/foo/bar\n{here}/bar/baz\n{here}/baz/boo\n"
        )

        test_file.unlink()
