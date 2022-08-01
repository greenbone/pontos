# Copyright (C) 2021-2022 Greenbone Networks GmbH
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

import json
import re
from pathlib import Path

from pontos.version.helper import (
    VersionError,
    check_develop,
    is_version_pep440_compliant,
    safe_version,
    versions_equal,
)

from .version import VersionCommand

GREENBONE_JS_VERSION_FILE = Path("src/version.js")

# This class is used for JavaScript Version command(s)
class JavaScriptVersionCommand(VersionCommand):
    def __init__(self, *, project_file_path: Path = None) -> None:
        if not project_file_path:
            project_file_path = Path.cwd() / "package.json"

        if not project_file_path.exists():
            raise VersionError(f"{str(project_file_path)} file not found.")

        with project_file_path.open(mode="r", encoding="utf-8") as fp:
            self.package = json.load(fp)
        if not self.package.get("version", None):
            raise VersionError(
                f"Version field missing in {str(project_file_path)}."
            )

        super().__init__(
            project_file_path=project_file_path,
        )

    def get_current_version(self) -> str:
        """Get the current version of this project
        In go the version is only defined within the repository
        tags, thus we need to check git, what tag is the latest"""
        try:
            return self.package["version"]
        except EnvironmentError as e:
            self._print(
                "No version tag found. Maybe this "
                "module has not been released at all."
            )
            raise e
        except json.JSONDecodeError as e:
            self._print("Couldn't load JSON")
            raise e

    def verify_version(self, version: str) -> None:
        """Verify the current version of this project"""
        current_version = self.get_current_version()
        if not is_version_pep440_compliant(current_version):
            raise VersionError(
                f"The version {current_version} is not PEP 440 compliant."
            )

        if versions_equal(self.get_current_version(), version):
            self._print("OK")

    def _update_package_json(self, new_version: str) -> None:
        """
        Update the version in the package.json file
        """
        try:
            self.package["version"] = new_version
            with self.project_file_path.open(mode="w") as fp:
                json.dump(obj=self.package, fp=fp, indent=2)
        except EnvironmentError as e:
            self._print(
                "No version tag found. Maybe this "
                "module has not been released at all."
            )
            raise e
        except json.JSONDecodeError as e:
            self._print("Couldn't load JSON")
            raise e

    def _update_version_file(self, new_version: str) -> None:
        """
        Update the version file with the new version
        """
        if GREENBONE_JS_VERSION_FILE.exists():
            content = GREENBONE_JS_VERSION_FILE.read_text(encoding="utf-8")
            content = re.sub(
                pattern=(
                    r'VERSION = (?P<quote>[\'"])[\d+\.]{2,3}'
                    r"{.dev[\d]}(?P=quote);"
                ),
                repl=f"VERSION = {new_version};",
                string=content,
            )
            GREENBONE_JS_VERSION_FILE.write_text(content, encoding="utf-8")

    def update_version(
        self, new_version: str, *, develop: bool = False, force: bool = False
    ) -> None:

        new_version = safe_version(new_version)
        if check_develop(new_version) and develop:
            develop = False
        if develop:
            new_version = f"{new_version}.dev1"

        package_version = self.get_current_version()
        if not force and versions_equal(new_version, package_version):
            self._print("Version is already up-to-date.")
            return

        self._update_package_json(new_version=new_version)

        self._update_version_file(new_version=new_version)

        self._print(f"Updated version from {package_version} to {new_version}")
