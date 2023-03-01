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
from typing import Any, Dict, Literal, Union

from .errors import VersionError
from .version import Version, VersionCommand, VersionUpdate, parse_version

GREENBONE_JS_VERSION_FILE = Path("src", "version.js")


# This class is used for JavaScript Version command(s)
class JavaScriptVersionCommand(VersionCommand):
    project_file_name = "package.json"
    _package = None

    @property
    def package(self) -> Dict[str, Any]:
        if self._package:
            return self._package

        if not self.project_file_path.exists():
            raise VersionError(f"{self.project_file_path} file not found.")

        try:
            with self.project_file_path.open(mode="r", encoding="utf-8") as fp:
                self._package = json.load(fp)
        except OSError as e:
            raise VersionError(
                "No version tag found. Maybe this "
                "module has not been released at all."
            ) from e
        except json.JSONDecodeError as e:
            raise VersionError(
                "No valid JSON found. Maybe this "
                "module has not been released at all."
            ) from e

        if not self._package.get("version", None):
            raise VersionError(
                f"Version field missing in {self.project_file_path}."
            )

        return self._package

    def get_current_version(self) -> Version:
        """Get the current version of this project
        In go the version is only defined within the repository
        tags, thus we need to check git, what tag is the latest"""
        return parse_version(self.package["version"])

    def verify_version(
        self, version: Union[Literal["current"], Version]
    ) -> None:
        """Verify the current version of this project"""
        current_version = self.get_current_version()
        if current_version != version:
            raise VersionError(
                f"Provided version {version} does not match the "
                f"current version {current_version}."
            )

    def _update_package_json(self, new_version: Version) -> None:
        """
        Update the version in the package.json file
        """
        try:
            self.package["version"] = str(new_version)

            with self.project_file_path.open(mode="w") as fp:
                json.dump(obj=self.package, fp=fp, indent=2)

        except EnvironmentError as e:
            raise VersionError(
                "No version tag found. Maybe this "
                "module has not been released at all."
            ) from e
        except json.JSONDecodeError as e:
            raise VersionError("Couldn't load JSON") from e

    def _update_version_file(self, new_version: Version) -> bool:
        """
        Update the version file with the new version
        """
        if not GREENBONE_JS_VERSION_FILE.exists():
            return False

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
        return True

    def update_version(
        self, new_version: Version, *, force: bool = False
    ) -> VersionUpdate:
        package_version = self.get_current_version()
        if not force and new_version == package_version:
            return VersionUpdate(previous=package_version, new=new_version)

        changed_files = [self.project_file_path]
        self._update_package_json(new_version=new_version)

        updated = self._update_version_file(new_version=new_version)
        if updated:
            changed_files.append(GREENBONE_JS_VERSION_FILE)

        return VersionUpdate(
            previous=package_version,
            new=new_version,
            changed_files=changed_files,
        )
