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

import subprocess
from subprocess import CalledProcessError

from .helper import (
    VersionError,
    is_version_pep440_compliant,
    strip_version,
    versions_equal,
)
from .version import UpdatedVersion, VersionCommand


# This class is used for Python Version command(s)
class GoVersionCommand(VersionCommand):
    project_file_name = "go.mod"

    def get_current_version(self) -> str:
        """Get the current version of this project
        In go the version is only defined within the repository
        tags, thus we need to check git, what tag is the latest"""
        try:
            proc = subprocess.run(
                "git describe --tags `git rev-list --tags --max-count=1`",
                shell=True,
                check=True,
                errors="ignore",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            version = strip_version(proc.stdout)
            return version.strip() if version is not None else ""
        except CalledProcessError as e:
            raise VersionError(
                "No version tag found. Maybe this "
                "module has not been released at all."
            ) from e

    def verify_version(self, version: str) -> None:
        """Verify the current version of this project"""
        current_version = self.get_current_version()
        if not is_version_pep440_compliant(current_version):
            raise VersionError(
                f"The version {current_version} is not PEP 440 compliant."
            )

        if not versions_equal(current_version, version):
            raise VersionError(
                f"Provided version {version} does not match the "
                f"current version {current_version}."
            )

    def update_version(
        self, new_version: str, *, develop: bool = False, force: bool = False
    ) -> UpdatedVersion:
        """Update the current version of this project"""
        raise VersionError(
            "Updating the version of a go module is not possible."
        )
