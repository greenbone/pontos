# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import tomlkit

from pontos.testing import temp_directory, temp_python_module
from pontos.version import VersionError
from pontos.version.commands._uv import UvVersionCommand
from pontos.version.schemes import PEP440VersioningScheme


class GetCurrentUvVersionCommandTestCase(unittest.TestCase):
    def test_missing_version_module_file_key(self):
        with temp_directory(change_into=True):
            Path("pyproject.toml").write_text(
                '[project]\nversion = "1.2.3"\n[tool.pontos.version]\n',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)

            with self.assertRaisesRegex(VersionError, "version-module-file"):
                command.get_current_version()

    def test_get_current_version(self):
        with temp_python_module(
            "__version__ = '1.2.3'", name="foo", change_into=True
        ) as version_file:
            version_file.parent.joinpath("pyproject.toml").write_text(
                '[project]\nname = "example"\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)

            self.assertEqual(
                command.get_current_version(),
                PEP440VersioningScheme.parse_version("1.2.3"),
            )

    def test_get_version_from_project_section(self):
        with temp_python_module(
            "__version__ = '1.2.3'", name="foo", change_into=True
        ) as version_file:
            version_file.parent.joinpath("pyproject.toml").write_text(
                '[project]\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)

            self.assertEqual(
                command.get_version_from_pyproject_toml(),
                PEP440VersioningScheme.parse_version("1.2.3"),
            )

    def test_project_version_is_required(self):
        with temp_directory(change_into=True):
            Path("pyproject.toml").write_text(
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)

            with self.assertRaisesRegex(VersionError, "Version information"):
                command.get_version_from_pyproject_toml()


class UpdateUvVersionTestCase(unittest.TestCase):
    def test_update_pyproject_version_creates_project_section(self):
        with temp_directory(change_into=True):
            project_file = Path("pyproject.toml")
            project_file.write_text(
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)
            new_version = PEP440VersioningScheme.parse_version("2.0.0")

            command.update_pyproject_version(new_version)

            project = tomlkit.parse(project_file.read_text(encoding="utf-8"))
            self.assertEqual(project["project"]["version"], "2.0.0")

    def test_update_version_updates_project_lock_and_module(self):
        with temp_python_module(
            "__version__ = '1.2.3'", name="foo", change_into=True
        ) as version_file:
            project_file = version_file.parent / "pyproject.toml"
            project_file.write_text(
                '[project]\nname = "example"\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            lock_file = version_file.parent / "uv.lock"
            lock_file.write_text(
                '[[package]]\nname = "other"\nversion = "9.9.9"\n\n'
                '[[package]]\nname = "example"\nversion = "1.2.3"\n',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)
            new_version = PEP440VersioningScheme.parse_version("2.0.0")

            update = command.update_version(new_version)

            self.assertEqual(
                update.previous,
                PEP440VersioningScheme.parse_version("1.2.3"),
            )
            self.assertEqual(update.new, new_version)
            self.assertEqual(
                update.changed_files,
                [
                    Path("foo.py"),
                    lock_file.resolve(),
                    project_file.resolve(),
                ],
            )
            self.assertEqual(
                tomlkit.parse(project_file.read_text(encoding="utf-8"))[
                    "project"
                ]["version"],
                "2.0.0",
            )
            self.assertEqual(
                tomlkit.parse(lock_file.read_text(encoding="utf-8"))["package"][
                    1
                ]["version"],
                "2.0.0",
            )
            self.assertEqual(
                tomlkit.parse(lock_file.read_text(encoding="utf-8"))["package"][
                    0
                ]["version"],
                "9.9.9",
            )
            self.assertIn(
                '__version__ = "2.0.0"',
                version_file.read_text(encoding="utf-8"),
            )

    def test_update_lock_file_requires_package_section(self):
        with temp_directory(change_into=True):
            lock_file = Path("uv.lock")
            lock_file.write_text("[resolution]\n", encoding="utf-8")
            command = UvVersionCommand(PEP440VersioningScheme)
            new_version = PEP440VersioningScheme.parse_version("2.0.0")

            with self.assertRaisesRegex(VersionError, r"\[\[package\]\]"):
                command._update_uv_lock_file(new_version)

    def test_update_lock_file_requires_project_package(self):
        with temp_python_module(
            "__version__ = '1.2.3'", name="foo", change_into=True
        ) as version_file:
            version_file.parent.joinpath("pyproject.toml").write_text(
                '[project]\nname = "example"\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            Path("uv.lock").write_text(
                '[[package]]\nname = "other"\nversion = "1.2.3"\n',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)
            new_version = PEP440VersioningScheme.parse_version("2.0.0")

            with self.assertRaisesRegex(VersionError, "Package 'example'"):
                command._update_uv_lock_file(new_version)

    def test_update_lock_file_requires_lock_file(self):
        with temp_directory(change_into=True):
            command = UvVersionCommand(PEP440VersioningScheme)
            new_version = PEP440VersioningScheme.parse_version("2.0.0")

            with self.assertRaisesRegex(VersionError, "uv.lock file not found"):
                command._update_uv_lock_file(new_version)

    def test_update_lock_file_requires_project_name(self):
        with temp_directory(change_into=True):
            Path("pyproject.toml").write_text(
                '[project]\nversion = "1.2.3"\n', encoding="utf-8"
            )
            Path("uv.lock").write_text(
                '[[package]]\nname = "example"\nversion = "1.2.3"\n',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)
            new_version = PEP440VersioningScheme.parse_version("2.0.0")

            with self.assertRaisesRegex(VersionError, "Project name not found"):
                command._update_uv_lock_file(new_version)

    def test_update_version_wraps_project_file_os_error(self):
        command = UvVersionCommand(PEP440VersioningScheme)
        new_version = PEP440VersioningScheme.parse_version("2.0.0")
        with (
            patch.object(
                command,
                "update_pyproject_version",
                side_effect=OSError("write"),
            ),
            self.assertRaisesRegex(VersionError, "pyproject.toml"),
        ):
            command.update_version(new_version)

    def test_update_version_falls_back_to_pyproject_version(self):
        with temp_directory(change_into=True):
            Path("pyproject.toml").write_text(
                '[project]\nname = "example"\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)
            new_version = PEP440VersioningScheme.parse_version("2.0.0")

            with (
                patch.object(
                    command, "get_current_version", side_effect=VersionError
                ),
                patch.object(command, "update_pyproject_version"),
                patch.object(command, "_update_uv_lock_file"),
                patch.object(command, "update_version_file"),
            ):
                update = command.update_version(new_version)

            self.assertEqual(
                update.previous, PEP440VersioningScheme.parse_version("1.2.3")
            )

    def test_update_version_ignores_missing_current_version(self):
        with temp_directory(change_into=True):
            Path("pyproject.toml").write_text(
                '[project]\n[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)
            new_version = PEP440VersioningScheme.parse_version("2.0.0")

            with (
                patch.object(
                    command, "get_current_version", side_effect=VersionError
                ),
                patch.object(
                    command,
                    "get_version_from_pyproject_toml",
                    side_effect=VersionError,
                ),
                patch.object(command, "update_pyproject_version"),
                patch.object(command, "_update_uv_lock_file"),
                patch.object(command, "update_version_file"),
            ):
                update = command.update_version(new_version)

            self.assertIsNone(update.previous)

    def test_update_version_wraps_lock_file_os_error(self):
        command = UvVersionCommand(PEP440VersioningScheme)
        new_version = PEP440VersioningScheme.parse_version("2.0.0")
        with (
            patch.object(command, "update_pyproject_version"),
            patch.object(
                command, "_update_uv_lock_file", side_effect=OSError("write")
            ),
            self.assertRaisesRegex(VersionError, "uv.lock"),
        ):
            command.update_version(new_version)

    def test_update_version_wraps_version_file_os_error(self):
        command = UvVersionCommand(PEP440VersioningScheme)
        new_version = PEP440VersioningScheme.parse_version("2.0.0")
        with (
            patch.object(command, "update_pyproject_version"),
            patch.object(command, "_update_uv_lock_file"),
            patch.object(
                command, "update_version_file", side_effect=OSError("write")
            ),
            self.assertRaisesRegex(VersionError, "version"),
        ):
            command.update_version(new_version)

    def test_development_version(self):
        with temp_python_module(
            "__version__ = '1.2.3'", name="foo", change_into=True
        ) as version_file:
            project_file = version_file.parent / "pyproject.toml"
            project_file.write_text(
                '[project]\nname = "example"\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            (version_file.parent / "uv.lock").write_text(
                '[[package]]\nname = "example"\nversion = "1.2.3"\n',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)
            new_version = PEP440VersioningScheme.parse_version("2.0.0.dev1")

            update = command.update_version(new_version)

            self.assertEqual(
                update.previous, PEP440VersioningScheme.parse_version("1.2.3")
            )
            self.assertEqual(update.new, new_version)

    def test_no_update(self):
        with temp_python_module(
            "__version__ = '1.2.3'", name="foo", change_into=True
        ) as version_file:
            version_file.parent.joinpath("pyproject.toml").write_text(
                '[project]\nname = "example"\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            (version_file.parent / "uv.lock").write_text(
                '[[package]]\nname = "example"\nversion = "1.2.3"\n',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)
            version = PEP440VersioningScheme.parse_version("1.2.3")

            update = command.update_version(version)

            self.assertEqual(update.previous, version)
            self.assertEqual(update.new, version)
            self.assertEqual(update.changed_files, [])

    def test_forced_update(self):
        with temp_python_module(
            "__version__ = '1.2.3'", name="foo", change_into=True
        ) as version_file:
            project_file = version_file.parent / "pyproject.toml"
            project_file.write_text(
                '[project]\nname = "example"\nversion = "1.2.3"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf-8",
            )
            lock_file = version_file.parent / "uv.lock"
            lock_file.write_text(
                '[[package]]\nname = "example"\nversion = "1.2.3"\n',
                encoding="utf-8",
            )
            command = UvVersionCommand(PEP440VersioningScheme)
            version = PEP440VersioningScheme.parse_version("1.2.3")

            update = command.update_version(version, force=True)

            self.assertEqual(update.previous, version)
            self.assertEqual(update.new, version)
            self.assertEqual(
                update.changed_files,
                [Path("foo.py"), lock_file.resolve(), project_file.resolve()],
            )


class VerifyVersionTestCase(unittest.TestCase):
    def test_verify_version(self):
        fake_version_file = Path("foo.py")
        with (
            temp_directory(change_into=True),
            patch.object(
                UvVersionCommand,
                "get_current_version",
                MagicMock(
                    return_value=PEP440VersioningScheme.parse_version("1.2.3")
                ),
            ),
            patch.object(
                UvVersionCommand,
                "version_file_path",
                new=PropertyMock(return_value=fake_version_file),
            ),
        ):
            Path("pyproject.toml").write_text(
                '[project]\nversion = "1.2.3"\n', encoding="utf-8"
            )
            command = UvVersionCommand(PEP440VersioningScheme)

            command.verify_version("current")

    def test_verify_version_rejects_mismatch(self):
        with (
            temp_directory(change_into=True),
            patch.object(
                UvVersionCommand,
                "get_current_version",
                MagicMock(
                    return_value=PEP440VersioningScheme.parse_version("1.2.3")
                ),
            ),
        ):
            Path("pyproject.toml").write_text(
                '[project]\nversion = "1.2.4"\n', encoding="utf-8"
            )
            command = UvVersionCommand(PEP440VersioningScheme)

            with self.assertRaisesRegex(VersionError, "doesn't match"):
                command.verify_version("current")


class ProjectFileUvVersionCommandTestCase(unittest.TestCase):
    def test_project_found_requires_project_and_lock_files(self):
        with temp_directory(change_into=True):
            command = UvVersionCommand(PEP440VersioningScheme)
            self.assertFalse(command.project_found())

            Path("pyproject.toml").touch()
            self.assertFalse(command.project_found())

            Path("uv.lock").touch()
            self.assertTrue(command.project_found())
