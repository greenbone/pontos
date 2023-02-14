# Copyright (C) 2023 Greenbone Networks GmbH
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

from pontos.testing import temp_directory, temp_python_module
from pontos.version.commands import get_current_version, update_version
from pontos.version.errors import VersionError


class GetCurrentVersionTestCase(unittest.TestCase):
    def test_no_project(self):
        with temp_directory(change_into=True), self.assertRaisesRegex(
            VersionError, "No project settings file found"
        ):
            get_current_version()

    def test_python_project_version(self):
        content = "__version__ = '1.2.3'"
        with temp_python_module(
            content, name="foo", change_into=True
        ) as temp_module:
            temp_dir = temp_module.parent / "pyproject.toml"
            temp_dir.write_text(
                '[tool.poetry]\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )
            self.assertEqual(get_current_version(), "1.2.3")

    def test_go_project_version(self):
        with temp_directory(change_into=True) as temp_dir:
            project_file = temp_dir / "go.mod"
            project_file.touch()
            version_file = temp_dir / "version.go"
            version_file.write_text('var version = "1.2.3"')
            self.assertEqual(get_current_version(), "1.2.3")

    def test_javascript_project_version(self):
        with temp_directory(change_into=True) as temp_dir:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}', encoding="utf8"
            )
            self.assertEqual(get_current_version(), "1.2.3")

    def test_cmake_project_version(self):
        with temp_directory(change_into=True) as temp_dir:
            version_file = temp_dir / "CMakeLists.txt"
            version_file.write_text("project(VERSION 1.2.3)", encoding="utf8")
            self.assertEqual(get_current_version(), "1.2.3")


class UpdateVersionTestCase(unittest.TestCase):
    def test_no_project(self):
        with temp_directory(change_into=True), self.assertRaisesRegex(
            VersionError, "No project settings file found"
        ):
            update_version("1.2.3")

    def test_python_project_version(self):
        content = "__version__ = '1.2.3'"
        with temp_python_module(
            content, name="foo", change_into=True
        ) as temp_module:
            temp_dir = temp_module.parent / "pyproject.toml"
            temp_dir.write_text(
                '[tool.poetry]\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )

            update_version("1.2.4")

            self.assertEqual(get_current_version(), "1.2.4")

    def test_python_project_dev_version(self):
        content = "__version__ = '1.2.3'"
        with temp_python_module(
            content, name="foo", change_into=True
        ) as temp_module:
            temp_dir = temp_module.parent / "pyproject.toml"
            temp_dir.write_text(
                '[tool.poetry]\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )

            update_version("1.2.4", develop=True)

            self.assertEqual(get_current_version(), "1.2.4.dev1")

    def test_go_project_version(self):
        with temp_directory(change_into=True) as temp_dir:
            project_file = temp_dir / "go.mod"
            project_file.touch()
            version_file = temp_dir / "version.go"
            version_file.write_text('var version = "1.2.3"')

            update_version("1.2.4")

            self.assertEqual(get_current_version(), "1.2.4")

    def test_go_project_dev_version(self):
        with temp_directory(change_into=True) as temp_dir:
            project_file = temp_dir / "go.mod"
            project_file.touch()
            version_file = temp_dir / "version.go"
            version_file.write_text('var version = "1.2.3"')

            update_version("1.2.4", develop=True)

            self.assertEqual(get_current_version(), "1.2.4.dev1")

    def test_javascript_project_version(self):
        with temp_directory(change_into=True) as temp_dir:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}', encoding="utf8"
            )

            update_version("1.2.4")

            self.assertEqual(get_current_version(), "1.2.4")

    def test_javascript_project_dev_version(self):
        with temp_directory(change_into=True) as temp_dir:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}', encoding="utf8"
            )

            update_version("1.2.4", develop=True)

            self.assertEqual(get_current_version(), "1.2.4.dev1")

    def test_cmake_project_version(self):
        with temp_directory(change_into=True) as temp_dir:
            version_file = temp_dir / "CMakeLists.txt"
            version_file.write_text("project(VERSION 1.2.3)", encoding="utf8")

            update_version("1.2.4")

            self.assertEqual(get_current_version(), "1.2.4")

    def test_cmake_project_dev_version(self):
        with temp_directory(change_into=True) as temp_dir:
            version_file = temp_dir / "CMakeLists.txt"
            version_file.write_text("project(VERSION 1.2.3)", encoding="utf8")

            update_version("1.2.4", develop=True)

            # cmake is special
            self.assertEqual(get_current_version(), "1.2.4")
