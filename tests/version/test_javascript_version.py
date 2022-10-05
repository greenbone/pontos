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


import contextlib
import io
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pontos.version.helper import VersionError
from pontos.version.javascript import JavaScriptVersionCommand
from tests.version import use_cwd


class JavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_missing_pyproject_toml_file(self):
        with use_cwd(Path(__file__).parent), self.assertRaisesRegex(
            VersionError, r"^.* not found\.$"
        ):
            JavaScriptVersionCommand()

    @patch("pontos.version.javascript.json", spec=json)
    def test_missing_tool_pontos_version_section(self, json_mock):
        project_file_path = MagicMock(spec=Path).return_value
        project_file_path.exists.return_value = True
        json_mock.load.return_value = json.loads('{"name":"foo", "bar":"bar"}')

        with self.assertRaisesRegex(
            VersionError, r"Version field missing in .*\.$"
        ):
            JavaScriptVersionCommand(project_file_path=project_file_path)

    @patch("pontos.version.javascript.json", spec=json)
    def test_get_version(self, json_mock):
        project_file_path = MagicMock(spec=Path).return_value
        project_file_path.exists.return_value = True
        json_mock.load.return_value = json.loads(
            '{"name":"foo", "version":"1.2.3"}'
        )

        cmd = JavaScriptVersionCommand(project_file_path=project_file_path)
        # pylint: disable=protected-access
        version = cmd.get_current_version()

        self.assertEqual(version, "1.2.3")


class UpdateJavaScriptVersionTestCase(unittest.TestCase):
    def test_update_version_file(self):
        package_file = Path(__file__).parent / "fake_package.json"
        package_file.write_text(
            '{"name":"foo", "version":"1.2.3"}', encoding="utf-8"
        )
        with contextlib.redirect_stdout(io.StringIO()):
            cmd = JavaScriptVersionCommand(project_file_path=package_file)
            cmd.update_version("22.4.0.dev1")

        with package_file.open(mode="r", encoding="utf-8") as fp:
            fake_package = json.load(fp)

        self.assertEqual(fake_package["version"], "22.4.0.dev1")

        package_file.unlink()
