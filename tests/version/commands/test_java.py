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
    },
  ]
}
"""

TEMPLATE_UPGRADE_VERSION_MARKDOWN = """# Task service

**task service**: Version 2023.9.3

## starting the local 
"""


class GetCurrentJavaVersionCommandTestCase(unittest.TestCase):
    def test_getting_version(self):
        with temp_file(
            name="go.mod",
            change_into=True,
        ):
            version_file_path = Path("upgradeVersion.json")
            version_file_path.write_text(
                TEMPLATE_UPGRADE_VERSION_JSON, encoding="utf-8"
            )

            result_version = JavaVersionCommand(
                SemanticVersioningScheme
            ).get_current_version()

            self.assertEqual(
                result_version, SemanticVersioningScheme.parse_version("2023.9.3")
            )
            version_file_path.unlink()
