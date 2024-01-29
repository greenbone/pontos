# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest

from pontos.testing import temp_directory, temp_python_module
from pontos.version.project import Project, ProjectError
from pontos.version.schemes import PEP440VersioningScheme


class ProjectTestCase(unittest.TestCase):
    def test_no_project_found(self):
        with (
            temp_directory(change_into=True),
            self.assertRaisesRegex(
                ProjectError, "No project settings file found"
            ),
        ):
            Project(PEP440VersioningScheme)

    def test_python_project(self):
        current_version = PEP440VersioningScheme.parse_version("1.2.3")
        new_version = PEP440VersioningScheme.parse_version("1.2.4")

        content = f"__version__ = '{current_version}'"
        with temp_python_module(
            content, name="foo", change_into=True
        ) as temp_module:
            pyproject_toml = temp_module.parent / "pyproject.toml"
            pyproject_toml.write_text(
                f'[tool.poetry]\nversion = "{current_version}"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )

            project = Project(PEP440VersioningScheme)
            self.assertEqual(project.get_current_version(), current_version)

            update = project.update_version(new_version)

            self.assertEqual(update.previous, current_version)
            self.assertEqual(update.new, new_version)

            self.assertEqual(len(update.changed_files), 2)

    def test_go_project(self):
        current_version = PEP440VersioningScheme.parse_version("1.2.3")
        new_version = PEP440VersioningScheme.parse_version("1.2.4")

        with temp_directory(change_into=True) as temp_dir:
            project_file = temp_dir / "go.mod"
            project_file.touch()
            version_file = temp_dir / "version.go"
            version_file.write_text(f'var version = "{current_version}"')

            project = Project(PEP440VersioningScheme)
            self.assertEqual(project.get_current_version(), current_version)

            update = project.update_version(new_version)

            self.assertEqual(update.previous, current_version)
            self.assertEqual(update.new, new_version)

            self.assertEqual(len(update.changed_files), 1)

    def test_javascript_project(self):
        current_version = PEP440VersioningScheme.parse_version("1.2.3")
        new_version = PEP440VersioningScheme.parse_version("1.2.4")

        with temp_directory(change_into=True) as temp_dir:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                f'{{"name": "foo", "version": "{current_version}"}}',
                encoding="utf8",
            )

            project = Project(PEP440VersioningScheme)
            self.assertEqual(project.get_current_version(), current_version)

            update = project.update_version(new_version)

            self.assertEqual(update.previous, current_version)
            self.assertEqual(update.new, new_version)

            self.assertEqual(len(update.changed_files), 1)

    def test_cmake_project_version(self):
        current_version = PEP440VersioningScheme.parse_version("1.2.3")
        new_version = PEP440VersioningScheme.parse_version("1.2.4")

        with temp_directory(change_into=True) as temp_dir:
            version_file = temp_dir / "CMakeLists.txt"
            version_file.write_text("project(VERSION 1.2.3)", encoding="utf8")

            project = Project(PEP440VersioningScheme)
            self.assertEqual(project.get_current_version(), current_version)

            update = project.update_version(new_version)

            self.assertEqual(update.previous, current_version)
            self.assertEqual(update.new, new_version)

            self.assertEqual(len(update.changed_files), 1)

    def test_all(self):
        current_version = PEP440VersioningScheme.parse_version("1.2.3")
        new_version = PEP440VersioningScheme.parse_version("1.2.4")

        content = f"__version__ = '{current_version}'"
        with temp_python_module(
            content, name="foo", change_into=True
        ) as temp_module:
            temp_dir = temp_module.parent
            pyproject_toml = temp_dir / "pyproject.toml"
            pyproject_toml.write_text(
                f'[tool.poetry]\nversion = "{current_version}"\n'
                '[tool.pontos.version]\nversion-module-file = "foo.py"',
                encoding="utf8",
            )

            go_mod_file = temp_dir / "go.mod"
            go_mod_file.touch()
            go_version_file = temp_dir / "version.go"
            go_version_file.write_text(f'var version = "{current_version}"')

            package_json = temp_dir / "package.json"
            package_json.write_text(
                f'{{"name": "foo", "version": "{current_version}"}}',
                encoding="utf8",
            )

            cmake_lists_txt = temp_dir / "CMakeLists.txt"
            cmake_lists_txt.write_text(
                "project(VERSION 1.2.3)", encoding="utf8"
            )

            project = Project(PEP440VersioningScheme)
            self.assertEqual(project.get_current_version(), current_version)

            update = project.update_version(new_version)

            self.assertEqual(update.previous, current_version)
            self.assertEqual(update.new, new_version)

            self.assertEqual(len(update.changed_files), 5)
