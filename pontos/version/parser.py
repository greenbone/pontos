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

import argparse
from typing import List, Optional

from pontos.errors import PontosError
from pontos.version.schemes import (
    VERSIONING_SCHEMES,
    VersioningScheme,
    versioning_scheme_argument_type,
)


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
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="Valid subcommands",
        help="Additional help",
        dest="command",
        required=True,
    )

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument(
        "version",
        help="Version string to compare",
        nargs="?",
    )
    verify_parser.add_argument(
        "--versioning-scheme",
        help="Versioning scheme to use for parsing and handling version "
        f"information. Choices are {', '.join(VERSIONING_SCHEMES.keys())}. "
        "Default: %(default)s",
        default="pep440",
        type=versioning_scheme_argument_type,
    )

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument(
        "--versioning-scheme",
        help="Versioning scheme to use for parsing and handling version "
        f"information. Choices are {', '.join(VERSIONING_SCHEMES.keys())}. "
        "Default: %(default)s",
        default="pep440",
        type=versioning_scheme_argument_type,
    )

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument(
        "version",
        help="Version string to use",
    )
    update_parser.add_argument(
        "--versioning-scheme",
        help="Versioning scheme to use for parsing and handling version "
        f"information. Choices are {', '.join(VERSIONING_SCHEMES.keys())}. "
        "Default: %(default)s",
        default="pep440",
        type=versioning_scheme_argument_type,
    )
    update_parser.add_argument(
        "--force",
        help="Don't check if version is already set. "
        "This will override existing version information!",
        action="store_true",
    )

    next_parser = subparsers.add_parser(
        "next", help="Calculate the next release version"
    )
    next_parser.add_argument(
        "type",
        help="Next version type",
        choices=[
            "dev",
            "calendar",
            "alpha",
            "beta",
            "rc",
            "patch",
            "minor",
            "major",
        ],
    )
    next_parser.add_argument(
        "--versioning-scheme",
        help="Versioning scheme to use for parsing and handling version "
        f"information. Choices are {', '.join(VERSIONING_SCHEMES.keys())}. "
        "Default: %(default)s",
        default="pep440",
        type=versioning_scheme_argument_type,
    )
    return parser


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = initialize_default_parser()

    parsed_args = parser.parse_args(args)
    scheme: VersioningScheme = parsed_args.versioning_scheme

    version = getattr(parsed_args, "version", None)
    if version and version != "current":
        try:
            parsed_args.version = scheme.parse_version(parsed_args.version)
        except PontosError as e:
            parser.error(str(e))
    return parsed_args
