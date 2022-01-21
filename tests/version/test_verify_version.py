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

# pylint: disable=protected-access

import unittest

from pathlib import Path
from unittest.mock import MagicMock

from pontos.version.python import PythonVersionCommand
from pontos.version.helper import VersionError


class VerifyVersionTestCase(unittest.TestCase):
    def test_current_version_not_pep440_compliant(self):
        fake_version_py = Path('foo.py')
        PythonVersionCommand.get_current_version = MagicMock(
            return_value='1.02.03'
        )
        fake_pyproject = Path(__file__).parent.parent / 'fake_pyproject.toml'
        cmd = PythonVersionCommand(project_file_path=fake_pyproject)
        cmd.version_file_path = fake_version_py

        with self.assertRaisesRegex(
            VersionError,
            'The version .* in foo.py is not PEP 440 compliant.',
        ):
            cmd.verify_version('1.2.3')

    def test_current_version_not_equal_pyproject_toml_version(self):
        fake_version_py = Path('foo.py')
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.1.1"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        PythonVersionCommand.get_current_version = MagicMock(
            return_value='1.2.3'
        )
        cmd = PythonVersionCommand(
            project_file_path=fake_path,
        )
        cmd.version_file_path = fake_version_py

        with self.assertRaisesRegex(
            VersionError,
            'The version .* in .* doesn\'t match the current version .*.',
        ):
            cmd.verify_version('1.2.3')

    def test_current_version(self):
        fake_version_py = Path('foo.py')
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        print_mock = MagicMock()
        PythonVersionCommand.get_current_version = MagicMock(
            return_value='1.2.3'
        )
        PythonVersionCommand._print = print_mock

        cmd = PythonVersionCommand(
            project_file_path=fake_path,
        )
        cmd.version_file_path = fake_version_py

        cmd.verify_version('current')

        print_mock.assert_called_with('OK')

    def test_provided_version_missmatch(self):
        fake_version_py = Path('foo.py')
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        PythonVersionCommand.get_current_version = MagicMock(
            return_value='1.2.3'
        )

        cmd = PythonVersionCommand(
            project_file_path=fake_path,
        )
        cmd.version_file_path = fake_version_py

        with self.assertRaisesRegex(
            VersionError,
            'Provided version .* does not match the current version .*.',
        ):
            cmd.verify_version('1.2.4')

    def test_verify_success(self):
        fake_version_py = Path('foo.py')
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        print_mock = MagicMock()
        PythonVersionCommand.get_current_version = MagicMock(
            return_value='1.2.3'
        )
        PythonVersionCommand._print = print_mock

        cmd = PythonVersionCommand(
            project_file_path=fake_path,
        )
        cmd.version_file_path = fake_version_py

        cmd.verify_version('1.2.3')

        print_mock.assert_called_with('OK')

    def test_verify_branch(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "21.0.1"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        fake_path.exists.return_value = True
        PythonVersionCommand.get_current_version = MagicMock(
            return_value='21.0.1'
        )
        print_mock = MagicMock()
        PythonVersionCommand._print = print_mock

        PythonVersionCommand(project_file_path=fake_path).run(
            args=['verify', '21.0.1']
        )

        print_mock.assert_called_with('OK')
