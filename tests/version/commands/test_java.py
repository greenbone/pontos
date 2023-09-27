# Copyright (C) 2023 Greenbone AG
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
from pathlib import Path

from pontos.testing import temp_file
from pontos.version.commands import JavaVersionCommand
from pontos.version.schemes import SemanticVersioningScheme

TEMPLATE_UPGRADE_VERSION_JSON = """{
  "files": [
    {
      "path": "README.md",
      "line": 3
    }
  ]
}
"""

TEMPLATE_UPGRADE_VERSION_MARKDOWN = """# Task service

**task service**: Version {}

## starting the local 
"""


class GetCurrentJavaVersionCommandTestCase(unittest.TestCase):
    def test_getting_version(self):
        with temp_file(
            name="upgradeVersion.json",
            change_into=True,
        ):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_JSON, encoding="utf-8"
            )

            version = "2023.9.3"
            readme_file_path = Path("README.md")
            readme_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version), encoding="utf-8"
            )

            result_version = JavaVersionCommand(
                SemanticVersioningScheme
            ).get_current_version()

            self.assertEqual(
                result_version,
                SemanticVersioningScheme.parse_version(version)
            )

            version_file_path.unlink()
            readme_file_path.unlink()


class VerifyJavaVersionCommandTestCase(unittest.TestCase):
    def test_verify_version(self):
        with temp_file(
            name="upgradeVersion.json",
            change_into=True,
        ):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_JSON, encoding="utf-8"
            )

            version = "2023.9.3"
            readme_file_path = Path("README.md")
            readme_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version), encoding="utf-8"
            )

            JavaVersionCommand(
                SemanticVersioningScheme
            ).verify_version(SemanticVersioningScheme.parse_version(version))

            version_file_path.unlink()
            readme_file_path.unlink()


class UpdateJavaVersionCommandTestCase(unittest.TestCase):
    def test_update_version(self):
        with temp_file(
            name="upgradeVersion.json",
            change_into=True,
        ):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_JSON, encoding="utf-8"
            )

            version = "2023.9.3"
            readme_file_path = Path("README.md")
            readme_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(version), encoding="utf-8"
            )

            new_version = "2023.9.4"
            updated_version_obj = JavaVersionCommand(
                SemanticVersioningScheme
            ).update_version(SemanticVersioningScheme.parse_version(new_version))

            self.assertEqual(updated_version_obj.previous, SemanticVersioningScheme.parse_version(version))
            self.assertEqual(updated_version_obj.new, SemanticVersioningScheme.parse_version(new_version))
            self.assertEqual(
                updated_version_obj.changed_files, ["README.md"]
            )

            content = readme_file_path.read_text(encoding="UTF-8")
            self.assertEqual(content, TEMPLATE_UPGRADE_VERSION_MARKDOWN.format(new_version))

            version_file_path.unlink()
            readme_file_path.unlink()
