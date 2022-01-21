# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Greenbone Networks GmbH
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

# pylint: disable=W0212


import unittest
import contextlib
import io
import subprocess

from dataclasses import dataclass

from pathlib import Path
from unittest.mock import MagicMock, patch
from pontos.version.go import GoVersionCommand
from pontos.version.helper import VersionError


@dataclass
class StdOutput:
    stdout: bytes


class CMakeVersionCommandTestCase(unittest.TestCase):
    def test_raise_exception_file_not_exists(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'go.mod'
        fake_path.exists.return_value = False
        with self.assertRaises(VersionError):
            GoVersionCommand(project_file_path=fake_path)

    def test_raise_exception_file_not_found(self):
        with self.assertRaises(VersionError, msg="go.mod file not found"):
            GoVersionCommand()

    def test_should_call_print_current_version_without_raising_exception(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'go.mod'
        fake_path.exists.return_value = True

        called = []

        # fake runner
        def runner(cmd):
            called.append(cmd)
            return StdOutput('21.22')

        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            cmd = GoVersionCommand(project_file_path=fake_path)
            cmd.shell_cmd_runner = runner

            cmd.run(args=['show'])

            self.assertIn(
                'git describe --tags `git rev-list --tags --max-count=1`',
                called,
            )
            self.assertEqual(buf.getvalue(), '21.22\n')

    @patch('pontos.version.go.subprocess', autospec=True)
    def test_should_raising_exception(self, mock_subprocess):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'go.mod'
        fake_path.exists.return_value = True

        mock_subprocess.run.side_effect = subprocess.CalledProcessError(
            returncode=2,
            cmd=["'git describe --tags `git rev-list --tags --max-count=1`'"],
        )

        with self.assertRaises(subprocess.CalledProcessError):
            result = GoVersionCommand(project_file_path=fake_path).run(
                args=['show']
            )
            print(result)

    def test_verify_branch(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'go.mod'
        fake_path.exists.return_value = True

        GoVersionCommand.get_current_version = MagicMock(return_value='21.0.1')
        print_mock = MagicMock()
        GoVersionCommand._print = print_mock

        GoVersionCommand(project_file_path=fake_path).run(
            args=['verify', '21.0.1']
        )

        print_mock.assert_called_with('OK')

    def test_verify_branch_not_pep(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'go.mod'
        fake_path.exists.return_value = True

        GoVersionCommand.get_current_version = MagicMock(return_value='021.02a')

        # with self.assertRaises(
        #     VersionError,
        # ):
        result = GoVersionCommand(project_file_path=fake_path).run(
            args=['verify', '021.02a']
        )

        self.assertTrue(
            isinstance(result, str), "expected result to be an error string"
        )
        self.assertEqual(
            result, 'The version 021.02a is not PEP 440 compliant.'
        )
