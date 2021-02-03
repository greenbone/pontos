# Copyright (C) 2020-2021 Greenbone Networks GmbH
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

from pontos.version.version import PontosVersionCommand, VersionError

from . import use_cwd


class PontosVersionCommandTestCase(unittest.TestCase):
    def test_missing_pyproject_toml_file(self):
        with use_cwd(Path(__file__).parent), self.assertRaisesRegex(
            VersionError, r'^.* not found\.$'
        ):
            PontosVersionCommand()

    def test_missing_tool_pontos_version_section(self):
        pyproject_toml_path = MagicMock(spec=Path).return_value
        pyproject_toml_path.exists.return_value = True
        pyproject_toml_path.read_text.return_value = '[tool.pontos]'

        with self.assertRaisesRegex(
            VersionError, r'^\[tool\.pontos\.version\] section missing in .*\.$'
        ):
            PontosVersionCommand(pyproject_toml_path=pyproject_toml_path)

    def test_missing_version_module_file_key(self):
        pyproject_toml_path = MagicMock(spec=Path).return_value
        pyproject_toml_path.exists.return_value = True
        pyproject_toml_path.read_text.return_value = (
            '[tool.pontos.version]\nname="foo"'
        )

        with self.assertRaisesRegex(
            VersionError,
            r'^version-module-file key not set in \[tool\.pontos\.version\] '
            r'section .*\.$',
        ):
            PontosVersionCommand(pyproject_toml_path=pyproject_toml_path)

    def test_with_all_settings(self):
        pyproject_toml_path = MagicMock(spec=Path).return_value
        pyproject_toml_path.exists.return_value = True
        pyproject_toml_path.read_text.return_value = (
            '[tool.pontos.version]\nversion-module-file="foo/__version__.py"'
        )

        cmd = PontosVersionCommand(pyproject_toml_path=pyproject_toml_path)

        self.assertEqual(cmd.version_file_path, Path('foo') / '__version__.py')
