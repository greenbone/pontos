# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
import unittest
from pathlib import Path
from string import Template

from pontos.testing import temp_directory, temp_file
from pontos.version import VersionError
from pontos.version.commands import JavaVersionCommand
from pontos.version.schemes import SemanticVersioningScheme

TEMPLATE_UPGRADE_VERSION_SINGLE_JSON = """{
  "files": [
    {
      "path": "README.md",
      "line": 3
    }
  ]
}
"""

TEMPLATE_UPGRADE_VERSION_MULTI_JSON = """{
  "files": [
    {
      "path": "README.md",
      "line": 3
    },
    {
      "path": "application.properties",
      "line": 2
    }
  ]
}
"""

TEMPLATE_UPGRADE_VERSION_WITH_LINE_JSON = Template(
    """{
  "files": [
    {
      "path": "README.md",
      "line": ${LINE_NO}
    }
  ]
}
"""
)

TEMPLATE_UPGRADE_VERSION_MARKDOWN = """# Task service

**task service**: Version {}

## starting the local 
"""

TEMPLATE_UPGRADE_VERSION_WITH_VERSION_PROPERTIES = """# application
sentry.release={}
server.port=8080
"""


class VerifyJavaVersionParsingTestCase(unittest.TestCase):
    def test_version_parsing(self):
        versions = {
            "2023.12.10",
            "2023.1.1",
            "2023.10.1",
            "2023.1.99",
            "0.0.1",
            "1.2.3-a1",
            "1.2.3-alpha1",
            "1.2.3-alpha1-dev1",
            "1.2.3-b1",
            "1.2.3-beta1",
            "1.2.3-beta1-dev1",
            "1.2.3-rc1",
            "1.2.3-rc1-dev1",
            "1.2.3-dev1",
            "22.4.1",
            "22.4.1-dev1",
            "0.5.0.dev1",
            "1.0.0-dev1",
            "1.0.0-alpha1",
            "1.0.0-alpha1-dev1",
            "1.0.0-beta1",
            "1.0.0-beta1-dev1",
            "1.0.0-rc1",
            "1.0.0-rc1-dev1",
        }
        for version in versions:
            with self.subTest(version=version):
                matches = JavaVersionCommand(
                    SemanticVersioningScheme
                ).parse_line(f"pre{version}post")

                self.assertEqual(matches.group("pre"), "pre")
                self.assertEqual(matches.group("version"), version)
                self.assertEqual(matches.group("post"), "post")


class GetCurrentJavaVersionCommandTestCase(unittest.TestCase):
    def test_getting_version(self):
        with temp_directory(change_into=True):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_SINGLE_JSON,
                encoding="utf-8",
            )

            version = "2023.9.3"
            readme_file_path = Path("README.md")
            readme_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version),
                encoding="utf-8",
            )

            result_version = JavaVersionCommand(
                SemanticVersioningScheme
            ).get_current_version()

            self.assertEqual(
                result_version, SemanticVersioningScheme.parse_version(version)
            )

            version_file_path.unlink()
            readme_file_path.unlink()

    def test_getting_version_no_files_configured(self):
        exp_err_msg = "no version found"
        with (
            temp_directory(change_into=True),
            self.assertRaisesRegex(
                VersionError,
                exp_err_msg,
            ),
        ):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                """{"files": []}""",
                encoding="utf-8",
            )

            JavaVersionCommand(SemanticVersioningScheme).get_current_version()

            version_file_path.unlink()

    def test_getting_version_without_version_config(self):
        exp_err_msg = (
            r"No /tmp/.*/upgradeVersion\.json config file found\. "
            r"This file is required for pontos"
        )
        with (
            temp_directory(change_into=True),
            self.assertRaisesRegex(
                VersionError,
                exp_err_msg,
            ),
        ):
            JavaVersionCommand(SemanticVersioningScheme).get_current_version()


class VerifyJavaVersionCommandTestCase(unittest.TestCase):
    def test_verify_version(self):
        with temp_directory(change_into=True):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MULTI_JSON, encoding="utf-8"
            )

            version = "2023.9.3"
            readme_file_path = Path("README.md")
            readme_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version),
                encoding="utf-8",
            )
            properties_file_path = Path("application.properties")
            properties_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_WITH_VERSION_PROPERTIES.format(
                    version
                ),
                encoding="latin-1",
            )

            JavaVersionCommand(SemanticVersioningScheme).verify_version(
                SemanticVersioningScheme.parse_version(version)
            )

            version_file_path.unlink()
            readme_file_path.unlink()
            properties_file_path.unlink()

    def test_verify_version_does_not_match(self):
        exp_err_msg = (
            r"Provided version 2023\.9\.4 does not match the "
            + r"current version 2023\.9\.3 "
            + r"in '/tmp/.*/upgradeVersion\.json'"
        )

        with (
            temp_directory(change_into=True),
            self.assertRaisesRegex(
                VersionError,
                exp_err_msg,
            ),
        ):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_SINGLE_JSON, encoding="utf-8"
            )

            version = "2023.9.3"
            new_version = "2023.9.4"
            readme_file_path = Path("README.md")
            readme_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version),
                encoding="utf-8",
            )

            JavaVersionCommand(SemanticVersioningScheme).verify_version(
                SemanticVersioningScheme.parse_version(new_version)
            )

            version_file_path.unlink()
            readme_file_path.unlink()


class UpdateJavaVersionCommandTestCase(unittest.TestCase):
    def test_update_version(self):
        with temp_directory(change_into=True):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_SINGLE_JSON, encoding="utf-8"
            )

            version = "2023.9.3"
            readme_file_path = Path("README.md")
            readme_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version),
                encoding="utf-8",
            )

            new_version = "2023.9.4"
            updated_version_obj = JavaVersionCommand(
                SemanticVersioningScheme
            ).update_version(
                SemanticVersioningScheme.parse_version(new_version)
            )

            self.assertEqual(
                updated_version_obj.previous,
                SemanticVersioningScheme.parse_version(version),
            )
            self.assertEqual(
                updated_version_obj.new,
                SemanticVersioningScheme.parse_version(new_version),
            )
            self.assertEqual(
                updated_version_obj.changed_files, [Path("README.md")]
            )

            content = readme_file_path.read_text(encoding="UTF-8")
            self.assertEqual(
                content,
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(new_version),
            )

            version_file_path.unlink()
            readme_file_path.unlink()

    def test_no_update_version(self):
        with temp_directory(change_into=True):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_SINGLE_JSON,
                encoding="utf-8",
            )

            version = "2023.9.3"
            readme_file_path = Path("README.md")
            readme_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version),
                encoding="utf-8",
            )

            updated_version_obj = JavaVersionCommand(
                SemanticVersioningScheme
            ).update_version(SemanticVersioningScheme.parse_version(version))

            self.assertEqual(
                updated_version_obj.previous,
                SemanticVersioningScheme.parse_version(version),
            )
            self.assertEqual(
                updated_version_obj.new,
                SemanticVersioningScheme.parse_version(version),
            )
            self.assertEqual(
                updated_version_obj.changed_files,
                [],
            )

            content = readme_file_path.read_text(encoding="UTF-8")
            self.assertEqual(
                content,
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version),
            )

            version_file_path.unlink()
            readme_file_path.unlink()

    def test_forced_update_version(self):
        with temp_directory(change_into=True):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_SINGLE_JSON,
                encoding="utf-8",
            )

            version = "2023.9.3"
            readme_file_path = Path("README.md")
            readme_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version),
                encoding="utf-8",
            )

            updated_version_obj = JavaVersionCommand(
                SemanticVersioningScheme
            ).update_version(
                SemanticVersioningScheme.parse_version(version), force=True
            )

            self.assertEqual(
                updated_version_obj.previous,
                SemanticVersioningScheme.parse_version(version),
            )
            self.assertEqual(
                updated_version_obj.new,
                SemanticVersioningScheme.parse_version(version),
            )
            self.assertEqual(
                updated_version_obj.changed_files,
                [Path("README.md")],
            )

            content = readme_file_path.read_text(encoding="UTF-8")
            self.assertEqual(
                content,
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version),
            )

            version_file_path.unlink()
            readme_file_path.unlink()

    def test_update_version_upgrade_config_with_wrong_line_number(self):
        exp_err_msg = (
            "Line has no version, "
            "file:'README.md' "
            "lineNo:4 "
            "content:'\n'"
        )
        with (
            temp_directory(change_into=True),
            self.assertRaisesRegex(
                VersionError,
                exp_err_msg,
            ),
        ):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_WITH_LINE_JSON.substitute(LINE_NO="4"),
                encoding="utf-8",
            )

            version = "2023.9.3"
            readme_file_path = Path("README.md")
            readme_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version),
                encoding="utf-8",
            )

            new_version = "2023.9.4"
            JavaVersionCommand(SemanticVersioningScheme).update_version(
                SemanticVersioningScheme.parse_version(new_version)
            )

            version_file_path.unlink()
            readme_file_path.unlink()


class ProjectFileJavaVersionCommandTestCase(unittest.TestCase):
    def test_project_file_not_found(self):
        with temp_directory(change_into=True):
            cmd = JavaVersionCommand(SemanticVersioningScheme)

            self.assertFalse(cmd.project_found())

    def test_project_file_found(self):
        with temp_file(name="upgradeVersion.json", change_into=True):
            cmd = JavaVersionCommand(SemanticVersioningScheme)

            self.assertTrue(cmd.project_found())
