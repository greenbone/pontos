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


import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pontos.testing import temp_directory, temp_file
from pontos.version.helper import VersionError
from pontos.version.javascript import JavaScriptVersionCommand


class GetCurrentJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_get_current_version(self):
        content = '{"name": "foo", "version": "1.2.3"}'
        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand(project_file_path=temp)
            version = cmd.get_current_version()

            self.assertEqual(version, "1.2.3")

    def test_no_project_file(self):
        cmd = JavaScriptVersionCommand(project_file_path=Path("foo/bar/baz"))
        with self.assertRaisesRegex(
            VersionError, "foo/bar/baz file not found."
        ):
            cmd.get_current_version()

    def test_no_package_version(self):
        content = '{"name": "foo"}'
        with temp_file(
            content, name="package.json", change_into=True
        ) as temp, self.assertRaisesRegex(
            VersionError, "Version field missing in"
        ):
            cmd = JavaScriptVersionCommand(project_file_path=temp)
            cmd.get_current_version()

    def test_no_valid_json_in_package_version(self):
        content = "{"
        with temp_file(
            content, name="package.json", change_into=True
        ) as temp, self.assertRaisesRegex(VersionError, "No valid JSON found."):
            cmd = JavaScriptVersionCommand(project_file_path=temp)
            cmd.get_current_version()


class UpdateJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_update_version_file(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand(project_file_path=temp)
            cmd.get_current_version()
            updated = cmd.update_version("22.4.0")

            self.assertEqual(updated.previous, "1.2.3")
            self.assertEqual(updated.new, "22.4.0")

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0")

    def test_update_version_check_develop(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand(project_file_path=temp)
            updated = cmd.update_version("22.4.0.dev1", develop=True)

            self.assertEqual(updated.previous, "1.2.3")
            self.assertEqual(updated.new, "22.4.0.dev1")

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0.dev1")

    def test_update_version_develop(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand(project_file_path=temp)
            updated = cmd.update_version("22.4.0", develop=True)

            self.assertEqual(updated.previous, "1.2.3")
            self.assertEqual(updated.new, "22.4.0.dev1")

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0.dev1")


class VerifyJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_current_version_not_pep440_compliant(self):
        with patch.object(
            JavaScriptVersionCommand,
            "get_current_version",
            MagicMock(return_value="01.02.003"),
        ), self.assertRaisesRegex(
            VersionError, "The version .* is not PEP 440 compliant."
        ):
            cmd = JavaScriptVersionCommand()
            cmd.verify_version("22.4")

    def test_versions_not_equal(self):
        with patch.object(
            JavaScriptVersionCommand,
            "get_current_version",
            MagicMock(return_value="1.2.3"),
        ), self.assertRaisesRegex(
            VersionError,
            "Provided version .* does not match the current version .*",
        ):
            cmd = JavaScriptVersionCommand()
            cmd.verify_version("22.4")

    def test_verify_success(self):
        with patch.object(
            JavaScriptVersionCommand,
            "get_current_version",
            MagicMock(return_value="22.4"),
        ):
            cmd = JavaScriptVersionCommand()
            cmd.verify_version("22.4")


class ProjectFileJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_project_file_not_found(self):
        with temp_directory() as temp:
            package_json = temp / "package.json"
            cmd = JavaScriptVersionCommand(project_file_path=package_json)

            self.assertIsNone(cmd.project_file_found())
            self.assertFalse(cmd.project_found())

    def test_project_file_found(self):
        with temp_file(name="package.json") as package_json:
            cmd = JavaScriptVersionCommand(project_file_path=package_json)

            self.assertEqual(cmd.project_file_found(), package_json)
            self.assertTrue(cmd.project_found())
