# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Any, Literal, Tuple, Union

import tomlkit
from tomlkit.toml_document import TOMLDocument

from .._errors import VersionError
from .._version import Version, VersionUpdate
from ._command import VersionCommand


class CargoVersionCommand(VersionCommand):
    project_file_name = "Cargo.toml"

    def __has_package_version(self, toml: TOMLDocument):
        """
        Checks if the 'package' table contains a 'version'.
        """
        # get a pure python object (recursively)
        toml_dict = toml.unwrap()
        return "package" in toml_dict and "version" in toml_dict["package"]

    def __has_workspace_package_version(self, toml: TOMLDocument):
        """
        Checks if the 'workspace.package' table contains a 'version'.
        """
        # get a pure python object (recursively)
        toml_dict = toml.unwrap()
        return (
            "workspace" in toml_dict
            and "package" in toml_dict["workspace"]
            and "version" in toml_dict["workspace"]["package"]
        )

    def __as_project_document(
        self, origin: Path
    ) -> Tuple[Path, tomlkit.TOMLDocument]:
        """
        Parse the given origin and returns a tuple of path to a
        Cargo.toml that contains a version.
        Version should be in the table package or workspace.package

        If the origin is invalid toml than it will raise a VersionError.
        """
        version: Any = None
        content = origin.read_text(encoding="utf-8")
        content = tomlkit.parse(content)
        if self.__has_workspace_package_version(content):
            version = content.get("workspace").get("package").get("version")  # type: ignore[union-attr]

        if self.__has_package_version(content):
            version = content.get("package").get("version")  # type: ignore[union-attr]

        if version:
            return (origin, content)
        else:
            raise VersionError(
                f"No {origin} file found. This file is required for pontos."
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

        project_path, project = self.__as_project_document(
            self.project_file_path
        )

        if self.__has_workspace_package_version(project):
            # Set the version for all members of the workspace. Members of the
            # workspace should use `version.workspace=true` in the 'package' table,
            # if they are released together with the parent crate.
            project["workspace"]["package"]["version"] = str(new_version)  # type: ignore[index] # noqa: E501

        if self.__has_package_version(project):
            # Set the 'version' of the 'package' table for the parent crate
            project["package"]["version"] = str(new_version)  # type: ignore[index] # noqa: E501

        project_path.write_text(tomlkit.dumps(project))
        return VersionUpdate(
            previous=previous_version,
            new=new_version,
            changed_files=[project_path],
        )

    def get_current_version(self) -> Version:
        (_, document) = self.__as_project_document(self.project_file_path)

        version: Any = None
        if self.__has_workspace_package_version(document):
            version = document["workspace"]["package"]["version"]  # type: ignore[index, arg-type]

        if self.__has_package_version(document):
            # If the 'package' table has a 'version', it always has precedence over the
            # 'version' in the 'workspace.package' table (they are assumed to be equal, if
            # managed by pontos)
            version = document["package"]["version"]  # type: ignore[index, arg-type]

        if isinstance(version, str):
            current_version = self.versioning_scheme.parse_version(version)

        return self.versioning_scheme.from_version(current_version)

    def verify_version(
        self, version: Union[Literal["current"], Version, None]
    ) -> None:
        current_version = self.get_current_version()

        if not version or version == "current":
            return

        if current_version != version:
            raise VersionError(
                f"Provided version {version} does not match the "
                f"current version {current_version}."
            )
