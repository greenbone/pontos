# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional, Sequence

import shtab

from pontos.version.schemes import (
    VERSIONING_SCHEMES,
    VersioningScheme,
    versioning_scheme_argument_type,
)


def parse_args(args: Optional[Sequence[str]] = None) -> Namespace:
    parser = ArgumentParser(
        description="Conventional commits utility. Create a changelog markdown "
        " text from conventional commits between the current and next release.",
        prog="pontos-changelog",
    )
    shtab.add_argument_to(parser)

    parser.add_argument(
        "--config",
        "-C",
        type=Path,
        help="Optional. Conventional commits config file (toml), including "
        "conventions. If not provided defaults are used.",
    ).complete = shtab.FILE  # type: ignore[attr-defined]

    parser.add_argument(
        "--repository",
        required=True,
        help="The github repository (owner/name). Used for building the links "
        "to the repository.",
    )

    parser.add_argument(
        "--versioning-scheme",
        help="Versioning scheme to use for parsing and handling version "
        f"information. Choices are {', '.join(VERSIONING_SCHEMES.keys())}. "
        "Default: %(default)s",
        default="pep440",
        type=versioning_scheme_argument_type,
    )

    parser.add_argument(
        "--current-version",
        help="Version to start looking for changes. All commits since this "
        "releases are take into account for creating the changelog text.",
    )

    parser.add_argument(
        "--next-version",
        "--release-version",
        dest="next_version",
        help="The planned release version",
    )

    parser.add_argument(
        "--git-tag-prefix",
        default="v",
        help="Prefix for git tag versions. Used to determine existing "
        "releases. Default: %(default)s",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Write changelog to this file.",
    ).complete = shtab.FILE  # type: ignore[attr-defined]

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Don't print messages to the terminal",
    )

    parsed_args = parser.parse_args(args=args)

    scheme: VersioningScheme = parsed_args.versioning_scheme
    current_version = getattr(parsed_args, "current_version", None)
    if current_version:
        parsed_args.current_version = scheme.parse_version(current_version)

    next_version = getattr(parsed_args, "next_version", None)
    if next_version:
        parsed_args.next_version = scheme.parse_version(next_version)

    return parsed_args
