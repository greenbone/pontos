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
from typing import Optional
from unittest.mock import MagicMock, PropertyMock, patch

import tomlkit

from pontos.testing import temp_directory, temp_file, temp_python_module
from pontos.version.helper import VersionError
from pontos.version.python import PythonVersionCommand


def mock_path(content: Optional[str] = None) -> Path:
    path = MagicMock(spec=Path).return_value
    path.exists.return_value = True
    path.read_text.return_value = content
    return path


class GetCurrentPythonVersionCommandTestCase(unittest.TestCase):
    def test_missing_tool_pontos_version_section(self):
        project_file_path = mock_path("[tool.pontos]")
        project_file_path.exists.return_value = True

        with self.assertRaisesRegex(
            VersionError, r"^\[tool\.pontos\.version\] section missing in .*\.$"
        ):
            cmd = PythonVersionCommand(project_file_path=project_file_path)
            cmd.get_current_version()

    def test_missing_version_module_file_key(self):
        project_file_path = mock_path('[tool.pontos.version]\nname="foo"')
        project_file_path.exists.return_value = True

        with self.assertRaisesRegex(
            VersionError,
            r"^version-module-file key not set in \[tool\.pontos\.version\] "
            r"section .*\.$",
        ):
            cmd = PythonVersionCommand(project_file_path=project_file_path)
            cmd.get_current_version()

    def test_version_file_path(self):
        project_file_path = mock_path(
            '[tool.pontos.version]\nversion-module-file="foo/__version__.py"'
        )
        project_file_path.exists.return_value = True

        cmd = PythonVersionCommand(project_file_path=project_file_path)

        self.assertEqual(cmd.version_file_path, Path("foo") / "__version__.py")

    def test_pyproject_toml_file_not_exists(self):
        fake_path = mock_path()
        fake_path.__str__.return_value = "pyproject.toml"
        fake_path.exists.return_value = False

        with self.assertRaisesRegex(
            VersionError, "pyproject.toml file not found."
        ):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            cmd.get_current_version()

        fake_path.exists.assert_called_with()

    def test_no_version_module(self):
        fake_path = mock_path(
            '[tool.pontos.version]\nversion-module-file = "foo.py"'
        )
        fake_path.__str__.return_value = "pyproject.toml"
        fake_path.exists.return_value = True

        with self.assertRaisesRegex(
            VersionError, r"Could not load version from 'foo'\. .* not found."
        ):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            cmd.get_current_version()

        fake_path.exists.assert_called_with()
        fake_path.read_text.assert_called_with(encoding="utf-8")

    def test_get_current_version(self):
        fake_path = mock_path(
            '[tool.poetry]\nversion = "1.2.3"\n'
            '[tool.pontos.version]\nversion-module-file = "foo.py"'
        )
        fake_path.__str__.return_value = "pyproject.toml"
        fake_path.exists.return_value = True

        content = "__version__ = '1.2.3'"
        with temp_python_module(content, name="foo", change_into=True):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            version = cmd.get_current_version()

            self.assertEqual(version, "1.2.3")

        fake_path.exists.assert_called_with()
        fake_path.read_text.assert_called_with(encoding="utf-8")


class UpdatePythonVersionTestCase(unittest.TestCase):
    def test_update_version_file(self):
        fake_path = mock_path(
            '[tool.poetry]\nversion = "1.2.3"\n'
            '[tool.pontos.version]\nversion-module-file = "foo.py"'
        )

        content = "__version__ = '21.1'"
        with temp_python_module(content, name="foo", change_into=True) as temp:
            cmd = PythonVersionCommand(project_file_path=fake_path)
            updated = cmd.update_version("22.2")

            self.assertEqual(updated.new, "22.2")
            self.assertEqual(updated.previous, "21.1")

            text = temp.read_text(encoding="utf8")

        *_, version_line, _last_line = text.split("\n")

        self.assertEqual(version_line, '__version__ = "22.2"')

    def test_empty_pyproject_toml(self):
        fake_path = mock_path("")
        fake_path.__str__.return_value = "meh.toml"

        with self.assertRaisesRegex(
            VersionError, r"Version information not found in meh\.toml file\."
        ):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            cmd.update_version("22.1.2")

    def test_empty_tool_section(self):
        fake_path = mock_path("[tool]")
        fake_path.__str__.return_value = "meh.toml"

        with self.assertRaisesRegex(
            VersionError, r"Version information not found in meh\.toml file\."
        ):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            cmd.update_version("22.1.2")

    def test_empty_tool_poetry_section(self):
        fake_path = mock_path(
            """[tool.poetry]
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        )

        content = "__version__ = '22.1'"
        with temp_python_module(content, name="foo", change_into=True):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            updated = cmd.update_version("22.2")

            self.assertEqual(updated.new, "22.2")
            self.assertEqual(updated.previous, "22.1")

        text = fake_path.write_text.call_args[0][0]

        toml = tomlkit.parse(text)

        self.assertEqual(toml["tool"]["poetry"]["version"], "22.2")

    def test_override_existing_version(self):
        fake_path = mock_path(
            """[tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        )

        content = "__version__ = '1.2.3'"
        with temp_python_module(content, name="foo", change_into=True):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            updated = cmd.update_version("22.2")

            self.assertEqual(updated.new, "22.2")
            self.assertEqual(updated.previous, "1.2.3")

        text = fake_path.write_text.call_args[0][0]

        toml = tomlkit.parse(text)

        self.assertEqual(toml["tool"]["poetry"]["version"], "22.2")

    def test_sanitize_version(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path = mock_path(
            """[tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        )

        content = "__version__ = '1.2.3'"
        with temp_python_module(content, name="foo", change_into=True):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            updated = cmd.update_version("22.02")

            self.assertEqual(updated.new, "22.2")
            self.assertEqual(updated.previous, "1.2.3")

        text = fake_path.write_text.call_args[0][0]

        toml = tomlkit.parse(text)

        self.assertEqual(toml["tool"]["poetry"]["version"], "22.2")

    def test_development_version(self):
        fake_path = mock_path(
            """[tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        )

        content = "__version__ = '1.2.3'"
        with temp_python_module(content, name="foo", change_into=True):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            updated = cmd.update_version("22.2", develop=True)

            self.assertEqual(updated.new, "22.2.dev1")
            self.assertEqual(updated.previous, "1.2.3")

        text = fake_path.write_text.call_args[0][0]

        toml = tomlkit.parse(text)

        self.assertEqual(toml["tool"]["poetry"]["version"], "22.2.dev1")

    def test_not_override_development_version(self):
        fake_path = mock_path(
            """[tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        )

        content = "__version__ = '1.2.3'"
        with temp_python_module(content, name="foo", change_into=True):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            updated = cmd.update_version("22.2.dev1", develop=True)

            self.assertEqual(updated.new, "22.2.dev1")
            self.assertEqual(updated.previous, "1.2.3")

        text = fake_path.write_text.call_args[0][0]

        toml = tomlkit.parse(text)

        self.assertEqual(toml["tool"]["poetry"]["version"], "22.2.dev1")


class VerifyVersionTestCase(unittest.TestCase):
    def test_current_version_not_pep440_compliant(self):
        fake_version_py = Path("foo.py")
        fake_pyproject = Path(__file__).parent.parent / "fake_pyproject.toml"

        with patch.object(
            PythonVersionCommand,
            "get_current_version",
            MagicMock(return_value="1.02.03"),
        ), patch.object(
            PythonVersionCommand,
            "version_file_path",
            new=PropertyMock(return_value=fake_version_py),
        ):
            cmd = PythonVersionCommand(project_file_path=fake_pyproject)

            with self.assertRaisesRegex(
                VersionError,
                "The version .* in foo.py is not PEP 440 compliant.",
            ):
                cmd.verify_version("1.2.3")

    def test_current_version_not_equal_pyproject_toml_version(self):
        fake_version_py = Path("foo.py")
        fake_path = mock_path(
            """[tool.poetry]\nversion = "1.1.1"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        )

        with patch.object(
            PythonVersionCommand,
            "get_current_version",
            MagicMock(return_value="1.2.3"),
        ), patch.object(
            PythonVersionCommand,
            "version_file_path",
            new=PropertyMock(return_value=fake_version_py),
        ):
            cmd = PythonVersionCommand(
                project_file_path=fake_path,
            )
            with self.assertRaisesRegex(
                VersionError,
                "The version .* in .* doesn't match the current version .*.",
            ):
                cmd.verify_version("1.2.3")

    def test_current_version(self):
        fake_version_py = Path("foo.py")
        fake_path = mock_path(
            """[tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        )

        with patch.object(
            PythonVersionCommand,
            "get_current_version",
            MagicMock(return_value="1.2.3"),
        ), patch.object(
            PythonVersionCommand,
            "version_file_path",
            new=PropertyMock(return_value=fake_version_py),
        ):
            cmd = PythonVersionCommand(
                project_file_path=fake_path,
            )
            cmd.verify_version("current")

    def test_provided_version_missmatch(self):
        fake_version_py = Path("foo.py")
        fake_path = mock_path(
            """[tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        )

        with patch.object(
            PythonVersionCommand,
            "get_current_version",
            MagicMock(return_value="1.2.3"),
        ), patch.object(
            PythonVersionCommand,
            "version_file_path",
            new=PropertyMock(return_value=fake_version_py),
        ):
            with self.assertRaisesRegex(
                VersionError,
                "Provided version .* does not match the current version .*.",
            ):
                cmd = PythonVersionCommand(
                    project_file_path=fake_path,
                )
                cmd.verify_version("1.2.4")

    def test_verify_success(self):
        fake_version_py = Path("foo.py")
        fake_path = mock_path(
            """[tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        )

        with patch.object(
            PythonVersionCommand,
            "get_current_version",
            MagicMock(return_value="1.2.3"),
        ), patch.object(
            PythonVersionCommand,
            "version_file_path",
            new=PropertyMock(return_value=fake_version_py),
        ):
            cmd = PythonVersionCommand(
                project_file_path=fake_path,
            )

            cmd.verify_version("1.2.3")


class ProjectFilePythonVersionCommandTestCase(unittest.TestCase):
    def test_project_file_not_found(self):
        with temp_directory() as temp:
            pyproject_toml = temp / "pyproject.toml"
            cmd = PythonVersionCommand(project_file_path=pyproject_toml)

            self.assertIsNone(cmd.project_file_found())
            self.assertFalse(cmd.project_found())

    def test_project_file_found(self):
        with temp_file(name="pyproject.toml") as pyproject_toml:
            cmd = PythonVersionCommand(project_file_path=pyproject_toml)

            self.assertEqual(cmd.project_file_found(), pyproject_toml)
            self.assertTrue(cmd.project_found())
