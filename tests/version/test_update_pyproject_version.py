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

# pylint: disable = protected-access

import unittest

from pathlib import Path
from unittest.mock import MagicMock

import tomlkit

from pontos.version.helper import VersionError
from pontos.version.python import PythonVersionCommand


class UpdatePyprojectVersionTestCase(unittest.TestCase):
    def test_empty_pyproject_toml(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = "meh.toml"
        fake_path.read_text.return_value = ''

        with self.assertRaises(
            VersionError, msg="Version information not found in meh.toml file."
        ):
            PythonVersionCommand(project_file_path=fake_path)

    def test_empty_tool_section(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = "meh.toml"
        fake_path.read_text.return_value = "[tool]"

        with self.assertRaises(
            VersionError, msg="Version information not found in meh.toml file."
        ):
            PythonVersionCommand(project_file_path=fake_path)

    def test_empty_tool_poetry_section(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        cmd = PythonVersionCommand(project_file_path=fake_path)
        cmd._update_pyproject_version('20.04dev1')

        text = fake_path.write_text.call_args[0][0]

        toml = tomlkit.parse(text)

        self.assertEqual(toml['tool']['poetry']['version'], '20.4.dev1')

    def test_override_existing_version(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        cmd = PythonVersionCommand(project_file_path=fake_path)
        cmd._update_pyproject_version('20.04dev1')

        text = fake_path.write_text.call_args[0][0]

        toml = tomlkit.parse(text)

        self.assertEqual(toml['tool']['poetry']['version'], '20.4.dev1')
