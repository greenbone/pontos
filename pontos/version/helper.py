# -*- coding: utf-8 -*-
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
#

import argparse
import re

from packaging.version import InvalidVersion, Version


class VersionError(Exception):
    """
    Some error has occurred during version handling
    """


def strip_version(version: str) -> str:
    """
    Strips a leading 'v' from a version string

    E.g. v1.2.3 will be converted to 1.2.3
    """
    if version and version[0] == "v":
        return version[1:]

    return version


def check_develop(version: str) -> bool:
    """
    Checks if the given Version is a develop version

    Returns True if yes, False if not
    """
    return True if Version(version).dev is not None else False


def is_version_pep440_compliant(version: str) -> bool:
    """
    Checks if the provided version is a PEP 440 compliant version string
    """
    return version == safe_version(version)


def initialize_default_parser() -> argparse.ArgumentParser:
    """
    Returns a default argument parser containing:
    - verify
    - show
    - update
    """
    parser = argparse.ArgumentParser(
        description="Version handling utilities.",
        prog="version",
    )
    parser.add_argument(
        "--quiet", help="don't print messages", action="store_true"
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="additional help",
        dest="command",
    )

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("version", help="version string to compare")
    subparsers.add_parser("show")

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("version", help="version string to use")
    update_parser.add_argument(
        "--force",
        help="don't check if version is already set",
        action="store_true",
    )
    update_parser.add_argument(
        "--develop",
        help="indicates if it is a develop version",
        action="store_true",
    )
    return parser


def safe_version(version: str) -> str:
    """
    Returns the version as a string in `PEP440`_ compliant
    format.

    .. _PEP440:
       https://www.python.org/dev/peps/pep-0440
    """
    try:
        return str(Version(version))
    except InvalidVersion:
        version = version.replace(" ", ".")
        return re.sub("[^A-Za-z0-9.]+", "-", version)


def versions_equal(new_version: str, old_version: str) -> bool:
    """
    Checks if new_version and old_version are equal
    """
    return safe_version(old_version) == safe_version(new_version)
