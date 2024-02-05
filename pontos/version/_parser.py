# SPDX-FileCopyrightText: 2023-2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import argparse
from typing import Optional, Sequence

import shtab

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
    shtab.add_argument_to(parser)
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="Valid subcommands",
        help="Additional help",
        dest="command",
        required=True,
    )

    verify_parser = subparsers.add_parser(
        "verify", help="Verify version in the current project"
    )
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

    show_parser = subparsers.add_parser(
        "show", help="Show version information of the current project"
    )
    show_parser.add_argument(
        "--versioning-scheme",
        help="Versioning scheme to use for parsing and handling version "
        f"information. Choices are {', '.join(VERSIONING_SCHEMES.keys())}. "
        "Default: %(default)s",
        default="pep440",
        type=versioning_scheme_argument_type,
    )

    update_parser = subparsers.add_parser(
        "update", help="Update version in the current project"
    )
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


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
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
