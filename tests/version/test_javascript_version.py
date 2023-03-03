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
from unittest.mock import MagicMock, patch

from pontos.testing import temp_directory, temp_file
from pontos.version.errors import VersionError
from pontos.version.javascript import JavaScriptVersionCommand
from pontos.version.version import Version


class GetCurrentJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_get_current_version(self):
        content = '{"name": "foo", "version": "1.2.3"}'
        with temp_file(content, name="package.json", change_into=True):
            cmd = JavaScriptVersionCommand()
            version = cmd.get_current_version()

            self.assertEqual(version, Version("1.2.3"))

    def test_no_project_file(self):
        with temp_directory(change_into=True), self.assertRaisesRegex(
            VersionError, ".* file not found."
        ):
            cmd = JavaScriptVersionCommand()
            cmd.get_current_version()

    def test_no_package_version(self):
        content = '{"name": "foo"}'
        with temp_file(
            content, name="package.json", change_into=True
        ), self.assertRaisesRegex(VersionError, "Version field missing in"):
            cmd = JavaScriptVersionCommand()
            cmd.get_current_version()

    def test_no_valid_json_in_package_version(self):
        content = "{"
        with temp_file(
            content, name="package.json", change_into=True
        ), self.assertRaisesRegex(VersionError, "No valid JSON found."):
            cmd = JavaScriptVersionCommand()
            cmd.get_current_version()


class UpdateJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_update_version_file(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand()
            cmd.get_current_version()
            updated = cmd.update_version(Version("22.4.0"))

            self.assertEqual(updated.previous, Version("1.2.3"))
            self.assertEqual(updated.new, Version("22.4.0"))
            self.assertEqual(updated.changed_files, [temp])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0")

    def test_update_js_version_file(self):
        content = '{"name":"foo", "version":"1.2.3"}'
        js_content = """const foo = "bar";
const VERSION = "1.2.3";
const func = () => ();
"""

        with temp_directory(change_into=True) as temp_dir:
            package_json = temp_dir / "package.json"
            package_json.write_text(content, encoding="utf8")
            js_version_file = (
                temp_dir / JavaScriptVersionCommand.version_file_path
            )
            js_version_file.parent.mkdir()
            js_version_file.write_text(js_content, encoding="utf8")

            cmd = JavaScriptVersionCommand()
            updated = cmd.update_version(Version("22.4.0"))

            self.assertEqual(updated.previous, Version("1.2.3"))
            self.assertEqual(updated.new, Version("22.4.0"))
            self.assertEqual(
                updated.changed_files,
                [package_json, JavaScriptVersionCommand.version_file_path],
            )

            with package_json.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0")

            self.assertEqual(
                js_version_file.read_text(encoding="utf8"),
                'const foo = "bar";\nconst VERSION = "22.4.0";\n'
                "const func = () => ();\n",
            )

    def test_update_version_develop(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand()
            updated = cmd.update_version(Version("22.4.0.dev1"))

            self.assertEqual(updated.previous, Version("1.2.3"))
            self.assertEqual(updated.new, Version("22.4.0.dev1"))
            self.assertEqual(updated.changed_files, [temp])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0.dev1")

    def test_no_update(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand()
            updated = cmd.update_version(Version("1.2.3"))

            self.assertEqual(updated.previous, Version("1.2.3"))
            self.assertEqual(updated.new, Version("1.2.3"))
            self.assertEqual(updated.changed_files, [])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "1.2.3")

    def test_forced_update(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand()
            updated = cmd.update_version(Version("1.2.3"), force=True)

            self.assertEqual(updated.previous, Version("1.2.3"))
            self.assertEqual(updated.new, Version("1.2.3"))
            self.assertEqual(updated.changed_files, [temp])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "1.2.3")


class VerifyJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_versions_not_equal(self):
        with patch.object(
            JavaScriptVersionCommand,
            "get_current_version",
            MagicMock(return_value=Version("1.2.3")),
        ), self.assertRaisesRegex(
            VersionError,
            "Provided version .* does not match the current version .*",
        ):
            cmd = JavaScriptVersionCommand()
            cmd.verify_version(Version("22.4"))

    def test_verify_success(self):
        with patch.object(
            JavaScriptVersionCommand,
            "get_current_version",
            MagicMock(return_value=Version("22.4")),
        ):
            cmd = JavaScriptVersionCommand()
            cmd.verify_version(Version("22.4"))

    def test_verify_js_mismatch(self):
        with patch.object(
            JavaScriptVersionCommand,
            "get_current_version",
            MagicMock(return_value=Version("22.4")),
        ), patch.object(
            JavaScriptVersionCommand,
            "_get_current_js_file_version",
            MagicMock(return_value=Version("22.5")),
        ), self.assertRaisesRegex(
            VersionError,
            "Provided version 22.4 does not match the current version 22.5 in "
            "src/version.js.",
        ):
            cmd = JavaScriptVersionCommand()
            cmd.verify_version(Version("22.4"))

    def test_verify_current(self):
        with patch.object(
            JavaScriptVersionCommand,
            "get_current_version",
            MagicMock(return_value=Version("22.4")),
        ):
            cmd = JavaScriptVersionCommand()
            cmd.verify_version("current")

    def test_verify_current_failure(self):
        with temp_directory(change_into=True), self.assertRaisesRegex(
            VersionError, "^.*package.json file not found"
        ):
            cmd = JavaScriptVersionCommand()
            cmd.verify_version("current")

    def test_verify_current_js_version_matches(self):
        content = '{"name":"foo", "version":"1.2.3"}'
        js_content = 'const VERSION = "1.2.3";'

        with temp_directory(change_into=True) as temp_dir:
            package_json = temp_dir / "package.json"
            package_json.write_text(content, encoding="utf8")
            js_version_file = (
                temp_dir / JavaScriptVersionCommand.version_file_path
            )
            js_version_file.parent.mkdir()
            js_version_file.write_text(js_content, encoding="utf8")

            cmd = JavaScriptVersionCommand()
            cmd.verify_version("current")

    def test_verify_current_js_mismatch(self):
        content = '{"name":"foo", "version":"1.2.3"}'
        js_content = 'const VERSION = "1.2.4";'

        with temp_directory(
            change_into=True
        ) as temp_dir, self.assertRaisesRegex(
            VersionError,
            "The version 1.2.4 in src/version.js doesn't match the current "
            "version 1.2.3.",
        ):
            package_json = temp_dir / "package.json"
            package_json.write_text(content, encoding="utf8")
            js_version_file = (
                temp_dir / JavaScriptVersionCommand.version_file_path
            )
            js_version_file.parent.mkdir()
            js_version_file.write_text(js_content, encoding="utf8")

            cmd = JavaScriptVersionCommand()
            cmd.verify_version("current")


class ProjectFileJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_project_file_not_found(self):
        with temp_directory(change_into=True):
            cmd = JavaScriptVersionCommand()

            self.assertFalse(cmd.project_found())

    def test_project_file_found(self):
        with temp_file(name="package.json", change_into=True):
            cmd = JavaScriptVersionCommand()

            self.assertTrue(cmd.project_found())
