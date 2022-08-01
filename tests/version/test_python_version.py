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
from tests.version import use_cwd


class PythonVersionCommandTestCase(unittest.TestCase):
    def test_missing_pyproject_toml_file(self):
        with use_cwd(Path(__file__).parent), self.assertRaisesRegex(
            VersionError, r"^.* not found\.$"
        ):
            PythonVersionCommand()

    def test_missing_tool_pontos_version_section(self):
        project_file_path = MagicMock(spec=Path).return_value
        project_file_path.exists.return_value = True
        project_file_path.read_text.return_value = "[tool.pontos]"

        with self.assertRaisesRegex(
            VersionError, r"^\[tool\.pontos\.version\] section missing in .*\.$"
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
            r"^version-module-file key not set in \[tool\.pontos\.version\] "
            r"section .*\.$",
        ):
            PythonVersionCommand(project_file_path=project_file_path)

    def test_with_all_settings(self):
        project_file_path = MagicMock(spec=Path).return_value
        project_file_path.exists.return_value = True
        project_file_path.read_text.return_value = (
            '[tool.pontos.version]\nversion-module-file="foo/__version__.py"'
        )

        cmd = PythonVersionCommand(project_file_path=project_file_path)

        self.assertEqual(cmd.version_file_path, Path("foo") / "__version__.py")

    def test_pyproject_toml_file_not_exists(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = "pyproject.toml"
        fake_path.exists.return_value = False

        with self.assertRaisesRegex(
            VersionError, "pyproject.toml file not found"
        ):
            PythonVersionCommand(project_file_path=fake_path)

        fake_path.exists.assert_called_with()

    def test_no_poerty_section(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = "pyproject.toml"
        fake_path.exists.return_value = True
        fake_path.read_text.return_value = (
            '[tool.pontos.version]\nversion-module-file = "foo.py"'
        )

        with self.assertRaisesRegex(
            VersionError, "Version information not found in pyproject.toml file"
        ):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            cmd._get_version_from_pyproject_toml()  # pylint: disable=protected-access

        fake_path.exists.assert_called_with()
        fake_path.read_text.assert_called_with(encoding="utf-8")

    def test_empty_poetry_section(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = "pyproject.toml"
        fake_path.exists.return_value = True
        fake_path.read_text.return_value = """
        [tool.poetry]
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        with self.assertRaisesRegex(
            VersionError, "Version information not found in pyproject.toml file"
        ):
            cmd = PythonVersionCommand(project_file_path=fake_path)
            cmd._get_version_from_pyproject_toml()  # pylint: disable=protected-access

        fake_path.exists.assert_called_with()
        fake_path.read_text.assert_called_with(encoding="utf-8")

    def test_get_version(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = "pyproject.toml"
        fake_path.exists.return_value = True
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        cmd = PythonVersionCommand(project_file_path=fake_path)
        # pylint: disable=protected-access
        version = cmd._get_version_from_pyproject_toml()

        self.assertEqual(version, "1.2.3")

        fake_path.exists.assert_called_with()
        fake_path.read_text.assert_called_with(encoding="utf-8")


class UpdatePythonVersionTestCase(unittest.TestCase):
    def test_update_version_file(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value

        fake_pyproject = Path(__file__).parent.parent / "fake_pyproject.toml"
        cmd = PythonVersionCommand(project_file_path=fake_pyproject)
        cmd.version_file_path = fake_path
        cmd._update_version_file("22.4.dev1")

        text = fake_path.write_text.call_args[0][0]

        *_, version_line, _last_line = text.split("\n")

        self.assertEqual(version_line, '__version__ = "22.4.dev1"')

    def test_empty_pyproject_toml(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = "meh.toml"
        fake_path.read_text.return_value = ""

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
        cmd._update_pyproject_version("20.04dev1")

        text = fake_path.write_text.call_args[0][0]

        toml = tomlkit.parse(text)

        self.assertEqual(toml["tool"]["poetry"]["version"], "20.04dev1")

    def test_override_existing_version(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        cmd = PythonVersionCommand(project_file_path=fake_path)
        cmd._update_pyproject_version("20.4.dev1")

        text = fake_path.write_text.call_args[0][0]

        toml = tomlkit.parse(text)

        self.assertEqual(toml["tool"]["poetry"]["version"], "20.4.dev1")


class VerifyVersionTestCase(unittest.TestCase):
    def test_current_version_not_pep440_compliant(self):
        fake_version_py = Path("foo.py")
        PythonVersionCommand.get_current_version = MagicMock(
            return_value="1.02.03"
        )
        fake_pyproject = Path(__file__).parent.parent / "fake_pyproject.toml"
        cmd = PythonVersionCommand(project_file_path=fake_pyproject)
        cmd.version_file_path = fake_version_py

        with self.assertRaisesRegex(
            VersionError,
            "The version .* in foo.py is not PEP 440 compliant.",
        ):
            cmd.verify_version("1.2.3")

    def test_current_version_not_equal_pyproject_toml_version(self):
        fake_version_py = Path("foo.py")
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.1.1"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        PythonVersionCommand.get_current_version = MagicMock(
            return_value="1.2.3"
        )
        cmd = PythonVersionCommand(
            project_file_path=fake_path,
        )
        cmd.version_file_path = fake_version_py

        with self.assertRaisesRegex(
            VersionError,
            "The version .* in .* doesn't match the current version .*.",
        ):
            cmd.verify_version("1.2.3")

    def test_current_version(self):
        fake_version_py = Path("foo.py")
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        print_mock = MagicMock()
        PythonVersionCommand.get_current_version = MagicMock(
            return_value="1.2.3"
        )
        PythonVersionCommand._print = print_mock

        cmd = PythonVersionCommand(
            project_file_path=fake_path,
        )
        cmd.version_file_path = fake_version_py

        cmd.verify_version("current")

        print_mock.assert_called_with("OK")

    def test_provided_version_missmatch(self):
        fake_version_py = Path("foo.py")
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        PythonVersionCommand.get_current_version = MagicMock(
            return_value="1.2.3"
        )

        cmd = PythonVersionCommand(
            project_file_path=fake_path,
        )
        cmd.version_file_path = fake_version_py

        with self.assertRaisesRegex(
            VersionError,
            "Provided version .* does not match the current version .*.",
        ):
            cmd.verify_version("1.2.4")

    def test_verify_success(self):
        fake_version_py = Path("foo.py")
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "1.2.3"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """

        print_mock = MagicMock()
        PythonVersionCommand.get_current_version = MagicMock(
            return_value="1.2.3"
        )
        PythonVersionCommand._print = print_mock

        cmd = PythonVersionCommand(
            project_file_path=fake_path,
        )
        cmd.version_file_path = fake_version_py

        cmd.verify_version("1.2.3")

        print_mock.assert_called_with("OK")

    def test_verify_branch(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.read_text.return_value = """
        [tool.poetry]\nversion = "21.0.1"
        [tool.pontos.version]\nversion-module-file = "foo.py"
        """
        fake_path.exists.return_value = True
        PythonVersionCommand.get_current_version = MagicMock(
            return_value="21.0.1"
        )
        print_mock = MagicMock()
        PythonVersionCommand._print = print_mock

        PythonVersionCommand(project_file_path=fake_path).run(
            args=["verify", "21.0.1"]
        )

        print_mock.assert_called_with("OK")
