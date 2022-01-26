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

import unittest

from pathlib import Path
from unittest.mock import MagicMock

from pontos.version.helper import VersionError
from pontos.version.python import PythonVersionCommand

from . import use_cwd


class PythonVersionCommandTestCase(unittest.TestCase):
    def test_missing_pyproject_toml_file(self):
        with use_cwd(Path(__file__).parent), self.assertRaisesRegex(
            VersionError, r'^.* not found\.$'
        ):
            PythonVersionCommand()

    def test_missing_tool_pontos_version_section(self):
        project_file_path = MagicMock(spec=Path).return_value
        project_file_path.exists.return_value = True
        project_file_path.read_text.return_value = '[tool.pontos]'

        with self.assertRaisesRegex(
            VersionError, r'^\[tool\.pontos\.version\] section missing in .*\.$'
        ):
            PythonVersionCommand(project_file_path=project_file_path)

    def test_missing_version_module_file_key(self):
        project_file_path = MagicMock(spec=Path).return_value
        project_file_path.exists.return_value = True
        project_file_path.read_text.return_value = (
            '[tool.pontos.version]\nname="foo"'
        )

        with self.assertRaisesRegex(
            VersionError,
            r'^version-module-file key not set in \[tool\.pontos\.version\] '
            r'section .*\.$',
        ):
            PythonVersionCommand(project_file_path=project_file_path)

    def test_with_all_settings(self):
        project_file_path = MagicMock(spec=Path).return_value
        project_file_path.exists.return_value = True
        project_file_path.read_text.return_value = (
            '[tool.pontos.version]\nversion-module-file="foo/__version__.py"'
        )

        cmd = PythonVersionCommand(project_file_path=project_file_path)

        self.assertEqual(cmd.version_file_path, Path('foo') / '__version__.py')
