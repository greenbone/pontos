# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Literal

import tomlkit
from tomlkit.toml_document import TOMLDocument

from .._errors import VersionError
from .._version import Version, VersionUpdate
from ._command import VersionCommand


class CargoVersionCommand(VersionCommand):
    project_file_name = "Cargo.toml"
    cargo_lock_file_name = "Cargo.lock"
    _cargo_lock_file_path: Path | None = None

    @property
    def cargo_toml(self) -> tomlkit.TOMLDocument:
        if not self.project_file_path.exists():
            raise VersionError(f"{self.project_file_name} file not found.")

        return tomlkit.parse(self.project_file_path.read_text(encoding="utf-8"))

    @property
    def cargo_lock_file_path(self) -> Path:
        if self._cargo_lock_file_path:
            return self._cargo_lock_file_path

        self._cargo_lock_file_path = (
            self.project_file_path.parent / self.cargo_lock_file_name
        )
        return self._cargo_lock_file_path

    def _has_package_version(self, toml: TOMLDocument):
        """
        Checks if the 'package' table contains a 'version'.
        """
        return "package" in toml and "version" in toml["package"]

    def _has_workspace_package_version(self, toml: TOMLDocument):
        """
        Checks if the 'workspace.package' table contains a 'version'.
        """
        return (
            "workspace" in toml
            and "package" in toml["workspace"]
            and "version" in toml["workspace"]["package"]
        )

    def _get_version_from_cargo_toml(
        self,
    ) -> Version:
        """Get the current version from the Cargo.toml file."""
        cargo_toml = self.cargo_toml
        version: str | None = None
        if self._has_workspace_package_version(cargo_toml):
            version = (
                cargo_toml.get("workspace").get("package").get("version")  # type: ignore
            )

        if self._has_package_version(cargo_toml):
            version = cargo_toml.get("package").get("version")  # type: ignore

        if version is not None:
            return self.versioning_scheme.parse_version(version)

        raise VersionError(
            f"No version information in {self.project_file_path} file found. This file is required for pontos."
        )

    def _update_cargo_toml_file(self, new_version: Version) -> None:
        """
        Update the Cargo.toml file with the new version.
        """
        cargo_toml = self.cargo_toml
        if self._has_workspace_package_version(cargo_toml):
            cargo_toml["workspace"]["package"]["version"] = str(new_version)
        else:
            # ensure the [package] section exists
            if "package" not in cargo_toml:
                package_table = tomlkit.table()
                cargo_toml["package"] = package_table
                cargo_toml["package"]["version"] = str(new_version)

        if self._has_package_version(cargo_toml):
            cargo_toml["package"]["version"] = str(new_version)

        self.project_file_path.write_text(
            tomlkit.dumps(cargo_toml), encoding="utf-8"
        )

    def _update_cargo_lock_file(self, new_version: Version) -> None:
        """
        Update the Cargo.lock file with the new version.
        """
        if not self.cargo_lock_file_path.exists():
            raise VersionError(
                f"{self.cargo_lock_file_name} file not found. Cannot update version."
            )

        cargo_lock = tomlkit.parse(
            self.cargo_lock_file_path.read_text(encoding="utf-8")
        )

        if "package" not in cargo_lock:
            raise VersionError(
                f"[[package]] entries not found in {self.cargo_lock_file_path}. "
                "Cannot update version."
            )
        project_name = self.cargo_toml.get("package", {}).get("name")
        if project_name is None:
            raise VersionError(
                f"Project name not found in {self.project_file_path}. Cannot update version."
            )

        if "package" in cargo_lock:
            for package in cargo_lock["package"]:
                if package.get("name") == project_name:
                    package["version"] = str(new_version)

        self.cargo_lock_file_path.write_text(
            tomlkit.dumps(cargo_lock), encoding="utf-8"
        )

    def update_version(
        self, new_version: Version, *, force: bool = False
    ) -> VersionUpdate:
        try:
            previous_version = self.get_current_version()
            if not force and new_version == previous_version:
                return VersionUpdate(previous=previous_version, new=new_version)
        except VersionError:
            # just ignore current version and override it
            previous_version = None

        try:
            self._update_cargo_toml_file(new_version=new_version)
        except OSError as e:
            raise VersionError(
                f"Unable to update version in {self.project_file_path.absolute()}. Error was {e}"
            ) from e

        try:
            self._update_cargo_lock_file(new_version=new_version)
        except OSError as e:
            raise VersionError(
                f"Unable to update version in {self.cargo_lock_file_path.absolute()}. Error was {e}"
            ) from e

        return VersionUpdate(
            previous=previous_version,
            new=new_version,
            changed_files=[self.project_file_path],
        )

    def get_current_version(self) -> Version:
        return self._get_version_from_cargo_toml()

    def verify_version(
        self, version: Literal["current"] | Version | None
    ) -> None:
        current_version = self.get_current_version()

        if not version or version == "current":
            return

        if current_version != version:
            raise VersionError(
                f"Provided version {version} does not match the "
                f"current version {current_version}."
            )
