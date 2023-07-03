# Copyright (C) 2021-2022 Greenbone AG
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
from typing import Any, Dict, Literal, Optional, Union

from ..errors import VersionError
from ..version import Version, VersionUpdate
from ._command import VersionCommand


# This class is used for JavaScript Version command(s)
class JavaScriptVersionCommand(VersionCommand):
    project_file_name = "package.json"
    version_file_paths = (Path("src", "version.js"), Path("src", "version.ts"))
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

    def _get_current_file_version(
        self, version_file: Path
    ) -> Optional[Version]:
        if not version_file.exists():
            return None

        content = version_file.read_text(encoding="utf-8")
        match = re.search(r'VERSION = "(?P<version>.*)";', content)
        if not match:
            raise VersionError(f"VERSION variable not found in {version_file}")

        return self.versioning_scheme.parse_version(match.group("version"))

    def get_current_version(self) -> Version:
        """Get the current version of this project
        In go the version is only defined within the repository
        tags, thus we need to check git, what tag is the latest"""
        return self.versioning_scheme.parse_version(self.package["version"])

    def verify_version(
        self, version: Union[Literal["current"], Version, None]
    ) -> None:
        """Verify the current version of this project"""
        current_version = self.get_current_version()

        if not version or version == "current":
            for version_file in self.version_file_paths:
                file_version = self._get_current_file_version(version_file)
                if file_version and file_version != current_version:
                    raise VersionError(
                        f"The version {file_version} in "
                        f"{version_file} doesn't match the current "
                        f"version {current_version}."
                    )
            return

        if current_version != version:
            raise VersionError(
                f"Provided version {version} does not match the "
                f"current version {current_version} in "
                f"{self.project_file_path}."
            )

        for version_file in self.version_file_paths:
            file_version = self._get_current_file_version(version_file)
            if file_version and file_version != version:
                raise VersionError(
                    f"Provided version {version} does not match the "
                    f"current version {file_version} in {version_file}."
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

    def _update_version_file(
        self, version_file: Path, new_version: Version
    ) -> bool:
        """
        Update the version file with the new version
        """
        if not version_file.exists():
            return False

        content = version_file.read_text(encoding="utf-8")
        match = re.search(
            pattern=r'VERSION = (?P<quote>[\'"])(?P<version>.*)(?P=quote)',
            string=content,
        )
        if not match:
            return False

        content = content.replace(match.group("version"), str(new_version))
        version_file.write_text(content, encoding="utf-8")
        return True

    def update_version(
        self, new_version: Version, *, force: bool = False
    ) -> VersionUpdate:
        try:
            package_version = self.get_current_version()
            if not force and new_version == package_version:
                return VersionUpdate(previous=package_version, new=new_version)
        except VersionError:
            # just ignore current version and override it
            package_version = None

        changed_files = [self.project_file_path]
        self._update_package_json(new_version=new_version)

        for version_file in self.version_file_paths:
            updated = self._update_version_file(
                version_file, new_version=new_version
            )
            if updated:
                changed_files.append(version_file)

        return VersionUpdate(
            previous=package_version,
            new=new_version,
            changed_files=changed_files,
        )
