# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import NoReturn, Optional, Sequence

from pontos.changelog.conventional_commits import ChangelogBuilder
from pontos.errors import PontosError
from pontos.terminal.null import NullTerminal
from pontos.terminal.rich import RichTerminal
from pontos.version.helper import get_last_release_version
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

    parser.add_argument(
        "--config",
        "-C",
        type=Path,
        help="Optional. Conventional commits config file (toml), including "
        "conventions. If not provided defaults are used.",
    )

    parser.add_argument(
        "--project",
        required=True,
        help="The github project. Used for building the links to the "
        "repository.",
    )

    parser.add_argument(
        "--space",
        default="greenbone",
        help="User/Team name in github. Used for building the links to the "
        "repository",
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
    )

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


def main(args: Optional[Sequence[str]] = None) -> NoReturn:
    parsed_args = parse_args(args)

    term = NullTerminal() if parsed_args.quiet else RichTerminal()

    if parsed_args.current_version:
        last_version = parsed_args.current_version
    else:
        last_version = get_last_release_version(
            parsed_args.versioning_scheme.parse_version,
            git_tag_prefix=parsed_args.git_tag_prefix,
        )

    try:
        changelog_builder = ChangelogBuilder(
            config=parsed_args.config,
            project=parsed_args.project,
            space=parsed_args.space,
        )
        if parsed_args.output:
            changelog_builder.create_changelog_file(
                parsed_args.output,
                last_version=last_version,
                next_version=parsed_args.next_version,
            )
        else:
            changelog = changelog_builder.create_changelog(
                last_version=last_version,
                next_version=parsed_args.next_version,
            )
            term.out(changelog)
    except PontosError as e:
        term.error(str(e))
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
