# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Union

from .._errors import VersionError
from .._version import Version, VersionUpdate
from ._command import VersionCommand


# This class is used for Java Version command(s)
class JavaVersionCommand(VersionCommand):
    VERSION_PATTERN = (
        r"^(?P<pre>.*[^\d])?"
        r"("
        r"?P<version>\d+\.\d+\.\d+"
        r"([-\.]+(dev|rc|beta|a|alpha|b)\d+)*"
        r")"
        r"(?P<post>.*$)"
    )

    project_file_name = "upgradeVersion.json"

    def get_current_version(self) -> Version:
        file_versions = self._read_versions_from_files()

        last_version = self._verify_version(file_versions)

        if last_version == "":
            raise VersionError("no version found")

        return self.versioning_scheme.parse_version(last_version)

    def verify_version(
        self, version: Union[Literal["current"], Version, None]
    ) -> None:
        file_versions = self._read_versions_from_files()

        last_version = self._verify_version(file_versions)

        if last_version != str(version):
            raise VersionError(
                f"Provided version {version} does not match the "
                f"current version {last_version} "
                f"in '{self.project_file_path}'"
            )

    def update_version(
        self, new_version: Version, *, force: bool = False
    ) -> VersionUpdate:
        try:
            current_version = self.get_current_version()
            if not force and new_version == current_version:
                return VersionUpdate(previous=current_version, new=new_version)
        except VersionError:
            # just ignore current version and override it
            current_version = None

        changed_files = self._update_version_files(new_version)

        return VersionUpdate(
            previous=current_version,
            new=new_version,
            changed_files=changed_files,
        )

    def parse_line(self, version_line: str):
        return re.match(self.VERSION_PATTERN, version_line, re.DOTALL)

    def _update_version_files(self, new_version) -> List[Path]:
        config = self._load_config()

        changed_files: List[Path] = []
        for file_config in config["files"]:
            file_path = file_config["path"]
            with (Path.cwd() / file_path).open("r") as input_file_handle:
                lines = input_file_handle.readlines()
                line_number = file_config["line"]
                version_line = lines[line_number - 1]

                matches = self.parse_line(version_line)
                if matches is None:
                    raise VersionError(
                        f"Line has no version, "
                        f"file:'{file_path}' "
                        f"lineNo:{line_number} "
                        f"content:'{version_line}'"
                    )
                lines[line_number - 1] = (
                    matches.group("pre")
                    + str(new_version)
                    + matches.group("post")
                )

                content = "".join(lines)
                with (Path.cwd() / file_path).open("w") as output_file_handle:
                    output_file_handle.write(content)
                changed_files.append(Path(file_config["path"]))
        return changed_files

    def _load_config(self) -> Dict[str, Any]:
        version_config_file = Path.cwd() / "upgradeVersion.json"
        if not version_config_file.exists():
            raise VersionError(
                f"No {version_config_file} config file found. "
                "This file is required for pontos"
            )

        with version_config_file.open("r") as f:
            json_string = f.read()
            config = json.loads(json_string)
            return config

    def _read_versions_from_files(self) -> Dict[str, str]:
        config = self._load_config()

        file_versions = {}
        for file_config in config["files"]:
            file_path = file_config["path"]
            file = Path.cwd() / file_path
            if not file.exists():
                raise VersionError(f"No {file} file found.")

            with file.open("r") as f:
                line_number = file_config["line"]
                readlines = f.readlines()
                if line_number - 1 > len(readlines):
                    raise VersionError(
                        f"Line number:{line_number} "
                        f"is beyond file lines:{len(readlines) + 1} "
                        f"file:'{file_path}'"
                    )
                version_line = readlines[line_number - 1]
                matches = self.parse_line(version_line)
                if matches is None:
                    raise VersionError(
                        f"Line has no version, "
                        f"file:'{file_path}' "
                        f"lineNo:{line_number} "
                        f"content:'{version_line}'"
                    )
                file_versions[file_path] = matches.group("version")
        return file_versions

    def _verify_version(self, file_versions: Dict[str, str]) -> str:
        last_version = ""
        last_file_name = ""
        for file_name, version in file_versions.items():
            if last_version == "":
                last_version = version
                last_file_name = file_name
                continue

            if last_version != version:
                raise VersionError(
                    f"Versions are not the same "
                    f"last_file_name:'{last_file_name}' "
                    f"last_version:'{last_version}' "
                    f"file_name:'{file_name}' "
                    f"version:'{version}'"
                )
        return last_version
