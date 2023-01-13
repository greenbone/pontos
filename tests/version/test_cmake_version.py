# -*- coding: utf-8 -*-
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
from unittest.mock import MagicMock, patch

from pontos.testing import temp_directory, temp_file
from pontos.version.cmake import CMakeVersionCommand, CMakeVersionParser
from pontos.version.helper import VersionError


class CMakeVersionCommandTestCase(unittest.TestCase):
    def test_return_error_string_incorrect_version_on_verify(self):
        with temp_file(
            "project(VERSION so_much_version_so_much_wow)\n"
            "set(PROJECT_DEV_VERSION 0)",
            name="CMakeLists.txt",
            change_into=True,
        ):
            cmake = CMakeVersionCommand()

            with self.assertRaisesRegex(
                VersionError,
                "The version so_much_version_so_much_wow is not PEP 440 "
                "compliant.",
            ):
                cmake.verify_version("so_much_version_so_much_wow")

    @patch(
        "pontos.version.cmake.CMakeVersionCommand.get_current_version",
        MagicMock(return_value="21.4"),
    )
    def test_return_0_correct_version_on_verify(self):
        with temp_file(
            "",
            name="CMakeLists.txt",
            change_into=True,
        ):
            cmake = CMakeVersionCommand()
            cmake.verify_version("21.4")

    def test_should_call_print_current_version_without_raising_exception(self):
        with temp_file(
            "project(VERSION 21)",
            name="CMakeLists.txt",
            change_into=True,
        ):
            cmake = CMakeVersionCommand()
            self.assertEqual(cmake.get_current_version(), "21")

    def test_raise_update_version(self):
        with temp_file(
            "project(VERSION 21)\nset(PROJECT_DEV_VERSION 0)",
            name="CMakeLists.txt",
            change_into=True,
        ) as temp:
            cmake = CMakeVersionCommand()
            updated = cmake.update_version("22", develop=True)

            self.assertEqual(
                "project(VERSION 22)\nset(PROJECT_DEV_VERSION 1)",
                temp.read_text(encoding="utf8"),
            )
            self.assertEqual(updated.previous, "21")
            self.assertEqual(updated.new, "22")

    def test_update_version_equal_not_force(self):
        with temp_file(
            "project(VERSION 22)\nset(PROJECT_DEV_VERSION 0)",
            name="CMakeLists.txt",
            change_into=True,
        ) as temp:
            cmake = CMakeVersionCommand()
            updated = cmake.update_version("22", develop=True)

            self.assertEqual(
                "project(VERSION 22)\nset(PROJECT_DEV_VERSION 0)",
                temp.read_text(encoding="utf8"),
            )
            self.assertEqual(updated.previous, "22")
            self.assertEqual(updated.new, "22")


class CMakeVersionParserTestCase(unittest.TestCase):
    def test_get_current_version_single_line_project(self):
        under_test = CMakeVersionParser("project(VERSION 2.3.4)")
        self.assertEqual(under_test.get_current_version(), "2.3.4")

    def test_update_version_project(self):
        under_test = CMakeVersionParser("project(VERSION 2.3.4)")
        self.assertEqual(
            under_test.update_version("2.3.5"), "project(VERSION 2.3.5)"
        )

    def test_update_raise_exception_when_version_is_incorrect(self):
        under_test = CMakeVersionParser("project(VERSION 2.3.4)")
        with self.assertRaises(VersionError):
            under_test.update_version("so_much_version_so_much_wow")

    def test_not_confuse_version_outside_project(self):
        under_test = CMakeVersionParser(
            "non_project(VERSION 2.3.5)\nproject(VERSION 2.3.4)"
        )
        self.assertEqual(under_test.get_current_version(), "2.3.4")

    def test_get_current_version_multiline_project(self):
        under_test = CMakeVersionParser("project\n(\nVERSION\n\t    2.3.4)")
        self.assertEqual(under_test.get_current_version(), "2.3.4")

    def test_find_project_dev_version(self):
        test_cmake_lists = """
        project(
            DESCRIPTION something
            VERSION 41.41.41
            LANGUAGES c
        )
        set(
            PROJECT_DEV_VERSION 1
        )
        """
        under_test = CMakeVersionParser(test_cmake_lists)
        self.assertEqual(under_test._project_dev_version_line_number, 7)
        self.assertEqual(under_test._project_dev_version, "1")

    def test_update_project_dev_version(self):
        test_cmake_lists = """
        project(
            DESCRIPTION something
            VERSION 41.41.41
            LANGUAGES c
        )
        set(
            PROJECT_DEV_VERSION 1
        )
        """
        under_test = CMakeVersionParser(test_cmake_lists)

        self.assertEqual(under_test._project_dev_version_line_number, 7)
        self.assertEqual(under_test._project_dev_version, "1")
        result = under_test.update_version("41.41.41", develop=False)
        self.assertEqual(under_test._project_dev_version, "0")
        self.assertEqual(
            result,
            test_cmake_lists.replace(
                "PROJECT_DEV_VERSION 1", "PROJECT_DEV_VERSION 0"
            ),
        )

    def test_update_project_dev_version_when_succeeded_by_another_set(self):
        test_cmake_lists = """
        cmake_minimum_required(VERSION 3.1)

        project(hello_world VERSION 41.41.41)
        set(PROJECT_DEV_VERSION 1)

        add_executable(app main.c)
        """
        under_test = CMakeVersionParser(test_cmake_lists)

        self.assertEqual(under_test._project_dev_version_line_number, 4)
        self.assertEqual(under_test._project_dev_version, "1")
        result = under_test.update_version("41.41.41", develop=False)
        self.assertEqual(under_test._project_dev_version, "0")
        self.assertEqual(
            result,
            test_cmake_lists.replace(
                "PROJECT_DEV_VERSION 1", "PROJECT_DEV_VERSION 0"
            ),
        )

    def test_get_current_version_multiline_project_combined_token(self):
        under_test = CMakeVersionParser(
            "project\n(\nDESCRIPTION something VERSION 2.3.4 LANGUAGES c\n)"
        )
        self.assertEqual(under_test.get_current_version(), "2.3.4")

    def test_raise_exception_project_no_version(self):
        with self.assertRaises(ValueError) as context:
            CMakeVersionParser("project(DESCRIPTION something LANGUAGES c)")
        self.assertEqual(
            str(context.exception), "unable to find cmake version in project."
        )

    def test_raise_exception_no_project(self):
        with self.assertRaises(ValueError) as context:
            CMakeVersionParser(
                "non_project(VERSION 2.3.5)",
            )

        self.assertEqual(
            str(context.exception), "unable to find cmake version."
        )


class ProjectFileCMakeVersionCommandTestCase(unittest.TestCase):
    def test_project_file_not_found(self):
        with temp_directory() as temp:
            cmake_lists_txt = temp / "CMakeLists.txt"
            cmd = CMakeVersionCommand(project_file_path=cmake_lists_txt)

            self.assertIsNone(cmd.project_file_found())
            self.assertFalse(cmd.project_found())

    def test_project_file_found(self):
        with temp_file(name="CMakeLists.txt") as cmake_lists_txt:
            cmd = CMakeVersionCommand(project_file_path=cmake_lists_txt)

            self.assertEqual(cmd.project_file_found(), cmake_lists_txt)
            self.assertTrue(cmd.project_found())
