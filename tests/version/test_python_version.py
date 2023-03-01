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
from unittest.mock import MagicMock, PropertyMock, patch

import tomlkit

from pontos.testing import temp_directory, temp_file, temp_python_module
from pontos.version.errors import VersionError
from pontos.version.python import PythonVersionCommand
from pontos.version.version import Version, VersionCalculator


class PythonVersionCommandTestCase(unittest.TestCase):
    def test_get_version_calculator(self):
        python = PythonVersionCommand()

        self.assertIsInstance(
            python.get_version_calculator(), VersionCalculator
        )


class GetCurrentPythonVersionCommandTestCase(unittest.TestCase):
    def test_missing_tool_pontos_version_section(self):
        with temp_file(
            "[tool.pontos]", name="pyproject.toml", change_into=True
        ), self.assertRaisesRegex(
            VersionError, r"^\[tool\.pontos\.version\] section missing in .*\.$"
        ):
            cmd = PythonVersionCommand()
            cmd.get_current_version()

    def test_missing_version_module_file_key(self):
        with temp_file(
            '[tool.pontos.version]\nname="foo"',
            name="pyproject.toml",
            change_into=True,
        ), self.assertRaisesRegex(
            VersionError,
            r"^version-module-file key not set in \[tool\.pontos\.version\] "
            r"section .*\.$",
        ):
            cmd = PythonVersionCommand()
            cmd.get_current_version()

    def test_version_file_path(self):
        with temp_file(
            '[tool.pontos.version]\nversion-module-file="foo/__version__.py"',
            name="pyproject.toml",
            change_into=True,
        ):
            cmd = PythonVersionCommand()

            self.assertEqual(
                cmd.version_file_path, Path("foo") / "__version__.py"
            )

    def test_pyproject_toml_file_not_exists(self):
        with temp_directory(change_into=True), self.assertRaisesRegex(
            VersionError, "pyproject.toml file not found."
        ):
            cmd = PythonVersionCommand()
            cmd.get_current_version()

    def test_no_version_module(self):
        with temp_file(
            '[tool.pontos.version]\nversion-module-file = "foo.py"',
            name="pyproject.toml",
            change_into=True,
        ), self.assertRaisesRegex(
            VersionError, r"Could not load version from 'foo'\. .* not found."
        ):
            cmd = PythonVersionCommand()
            cmd.get_current_version()

    def test_get_current_version(self):
        with temp_python_module(
            "__version__ = '1.2.3'", name="foo", change_into=True
        ) as tmp_module:
            tmp_file = tmp_module.parent / "pyproject.toml"
            tmp_file.write_text(
                '[tool.poetry]\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )
            cmd = PythonVersionCommand()
            version = cmd.get_current_version()

            self.assertEqual(version, Version("1.2.3"))


class UpdatePythonVersionTestCase(unittest.TestCase):
    def test_update_version_file(self):
        content = "__version__ = '21.1'"
        with temp_python_module(content, name="foo", change_into=True) as temp:
            tmp_file = temp.parent / "pyproject.toml"
            tmp_file.write_text(
                '[tool.poetry]\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )

            cmd = PythonVersionCommand()
            updated = cmd.update_version(Version("22.2"))

            self.assertEqual(updated.new, Version("22.2"))
            self.assertEqual(updated.previous, Version("21.1"))
            self.assertEqual(updated.changed_files, [Path("foo.py"), tmp_file])

            text = temp.read_text(encoding="utf8")

        *_, version_line, _last_line = text.split("\n")

        self.assertEqual(version_line, '__version__ = "22.2"')

    def test_empty_pyproject_toml(self):
        with temp_file(
            "", name="pyproject.toml", change_into=True
        ), self.assertRaisesRegex(
            VersionError,
            r"Version information not found in .*pyproject\.toml file\.",
        ):
            cmd = PythonVersionCommand()
            cmd.update_version(Version("22.1.2"))

    def test_empty_tool_section(self):
        with temp_file(
            "[tool]", name="pyproject.toml", change_into=True
        ), self.assertRaisesRegex(
            VersionError,
            r"Version information not found in .*pyproject\.toml file\.",
        ):
            cmd = PythonVersionCommand()
            cmd.update_version(Version("22.1.2"))

    def test_empty_tool_poetry_section(self):
        content = "__version__ = '22.1'"
        with temp_python_module(content, name="foo", change_into=True) as temp:
            tmp_file = temp.parent / "pyproject.toml"
            tmp_file.write_text(
                "[tool.poetry]\n"
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )
            cmd = PythonVersionCommand()
            updated = cmd.update_version(Version("22.2"))

            self.assertEqual(updated.new, Version("22.2"))
            self.assertEqual(updated.previous, Version("22.1"))
            self.assertEqual(updated.changed_files, [Path("foo.py"), tmp_file])

            text = tmp_file.read_text(encoding="utf8")

            toml = tomlkit.parse(text)

            self.assertEqual(toml["tool"]["poetry"]["version"], "22.2")

    def test_override_existing_version(self):
        content = "__version__ = '1.2.3'"
        with temp_python_module(content, name="foo", change_into=True) as temp:
            tmp_file = temp.parent / "pyproject.toml"
            tmp_file.write_text(
                '[tool.poetry]\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )
            cmd = PythonVersionCommand()
            updated = cmd.update_version(Version("22.2"))

            self.assertEqual(updated.new, Version("22.2"))
            self.assertEqual(updated.previous, Version("1.2.3"))
            self.assertEqual(updated.changed_files, [Path("foo.py"), tmp_file])

            text = tmp_file.read_text(encoding="utf8")

            toml = tomlkit.parse(text)

            self.assertEqual(toml["tool"]["poetry"]["version"], "22.2")

    def test_development_version(self):
        content = "__version__ = '1.2.3'"
        with temp_python_module(content, name="foo", change_into=True) as temp:
            tmp_file = temp.parent / "pyproject.toml"
            tmp_file.write_text(
                '[tool.poetry]\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )
            cmd = PythonVersionCommand()
            updated = cmd.update_version(Version("22.2.dev1"))

            self.assertEqual(updated.new, Version("22.2.dev1"))
            self.assertEqual(updated.previous, Version("1.2.3"))
            self.assertEqual(updated.changed_files, [Path("foo.py"), tmp_file])

            text = tmp_file.read_text(encoding="utf8")

            toml = tomlkit.parse(text)

            self.assertEqual(toml["tool"]["poetry"]["version"], "22.2.dev1")

    def test_no_update(self):
        content = "__version__ = '1.2.3'"
        with temp_python_module(content, name="foo", change_into=True) as temp:
            tmp_file = temp.parent / "pyproject.toml"
            tmp_file.write_text(
                '[tool.poetry]\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )
            cmd = PythonVersionCommand()
            updated = cmd.update_version(Version("1.2.3"))

            self.assertEqual(updated.new, Version("1.2.3"))
            self.assertEqual(updated.previous, Version("1.2.3"))
            self.assertEqual(updated.changed_files, [])

    def test_forced_updated(self):
        content = "__version__ = '1.2.3'"
        with temp_python_module(content, name="foo", change_into=True) as temp:
            tmp_file = temp.parent / "pyproject.toml"
            tmp_file.write_text(
                '[tool.poetry]\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )
            cmd = PythonVersionCommand()
            updated = cmd.update_version(Version("1.2.3"), force=True)

            self.assertEqual(updated.new, Version("1.2.3"))
            self.assertEqual(updated.previous, Version("1.2.3"))
            self.assertEqual(updated.changed_files, [Path("foo.py"), tmp_file])

            text = tmp_file.read_text(encoding="utf8")

            toml = tomlkit.parse(text)

            self.assertEqual(toml["tool"]["poetry"]["version"], "1.2.3")


class VerifyVersionTestCase(unittest.TestCase):
    def test_current_version_not_equal_pyproject_toml_version(self):
        fake_version_py = Path("foo.py")
        with patch.object(
            PythonVersionCommand,
            "get_current_version",
            MagicMock(return_value=Version("1.2.3")),
        ), patch.object(
            PythonVersionCommand,
            "version_file_path",
            new=PropertyMock(return_value=fake_version_py),
        ):
            cmd = PythonVersionCommand()
            with self.assertRaisesRegex(
                VersionError,
                "The version .* in .* doesn't match the current version .*.",
            ):
                cmd.verify_version(Version("1.2.3"))

    def test_current_version(self):
        fake_version_py = Path("foo.py")
        content = (
            '[tool.poetry]\nversion = "1.2.3"\n'
            '[tool.pontos.version]\nversion-module-file = "foo.py"'
        )

        with temp_file(
            content, name="pyproject.toml", change_into=True
        ), patch.object(
            PythonVersionCommand,
            "get_current_version",
            MagicMock(return_value=Version("1.2.3")),
        ), patch.object(
            PythonVersionCommand,
            "version_file_path",
            new=PropertyMock(return_value=fake_version_py),
        ):
            cmd = PythonVersionCommand()
            cmd.verify_version("current")

    def test_provided_version_missmatch(self):
        fake_version_py = Path("foo.py")
        content = (
            '[tool.poetry]\nversion = "1.2.3"\n'
            '[tool.pontos.version]\nversion-module-file = "foo.py"'
        )

        with temp_file(
            content, name="pyproject.toml", change_into=True
        ), patch.object(
            PythonVersionCommand,
            "get_current_version",
            MagicMock(return_value=Version("1.2.3")),
        ), patch.object(
            PythonVersionCommand,
            "version_file_path",
            new=PropertyMock(return_value=fake_version_py),
        ):
            with self.assertRaisesRegex(
                VersionError,
                "Provided version .* does not match the current version .*.",
            ):
                cmd = PythonVersionCommand()
                cmd.verify_version(Version("1.2.4"))

    def test_verify_success(self):
        fake_version_py = Path("foo.py")
        content = (
            '[tool.poetry]\nversion = "1.2.3"\n'
            '[tool.pontos.version]\nversion-module-file = "foo.py"'
        )

        with temp_file(
            content, name="pyproject.toml", change_into=True
        ), patch.object(
            PythonVersionCommand,
            "get_current_version",
            MagicMock(return_value=Version("1.2.3")),
        ), patch.object(
            PythonVersionCommand,
            "version_file_path",
            new=PropertyMock(return_value=fake_version_py),
        ):
            cmd = PythonVersionCommand()

            cmd.verify_version(Version("1.2.3"))


class ProjectFilePythonVersionCommandTestCase(unittest.TestCase):
    def test_project_file_not_found(self):
        with temp_directory(change_into=True):
            cmd = PythonVersionCommand()

            self.assertFalse(cmd.project_found())

    def test_project_file_found(self):
        with temp_file(name="pyproject.toml", change_into=True):
            cmd = PythonVersionCommand()

            self.assertTrue(cmd.project_found())
