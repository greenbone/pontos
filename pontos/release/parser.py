# Copyright (C) 2020-2023 Greenbone AG
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
import os
from argparse import (
    ArgumentParser,
    ArgumentTypeError,
    BooleanOptionalAction,
    Namespace,
)
from enum import Enum
from pathlib import Path
from typing import Callable, Optional, Tuple, Type

from pontos.release.helper import ReleaseType
from pontos.release.show import OutputFormat, show
from pontos.version.schemes import (
    VERSIONING_SCHEMES,
    PEP440VersioningScheme,
    VersioningScheme,
    versioning_scheme_argument_type,
)

from .create import create_release
from .sign import sign

DEFAULT_SIGNING_KEY = "0ED1E580"


def to_choices(enum: Type[Enum]) -> str:
    return ", ".join([t.value for t in enum])


def enum_type(enum: Type[Enum]) -> Callable[[str], Enum]:
    def convert(value: str) -> Enum:
        try:
            return enum(value)
        except ValueError:
            raise ArgumentTypeError(
                f"invalid value {value}. Expected one of {to_choices(enum)}."
            ) from None

    return convert


class ReleaseVersionAction(
    argparse._StoreAction
):  # pylint: disable=protected-access
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, "release_type", ReleaseType.VERSION)
        setattr(namespace, self.dest, values)


def parse_args(args) -> Tuple[Optional[str], Optional[str], Namespace]:
    """
    Return user, token, parsed arguments
    """
    parser = ArgumentParser(
        description="Release handling utility.",
        prog="pontos-release",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Don't print messages to the terminal",
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="additional help",
        dest="command",
        required=True,
    )

    create_parser = subparsers.add_parser(
        "create", help="Create a new release", aliases=["release"]
    )
    create_parser.set_defaults(func=create_release)
    create_parser.add_argument(
        "--versioning-scheme",
        help="Versioning scheme to use for parsing and handling version "
        f"information. Choices are {', '.join(VERSIONING_SCHEMES.keys())}. "
        "Default: %(default)s",
        default="pep440",
        type=versioning_scheme_argument_type,
    )
    create_parser.add_argument(
        "--release-type",
        help="Select the release type for calculating the release version. "
        f"Possible choices are: {to_choices(ReleaseType)}.",
        type=enum_type(ReleaseType),
    )
    create_parser.add_argument(
        "--release-version",
        help=(
            "Will release changelog as version. "
            "Default: lookup version in project definition."
        ),
        action=ReleaseVersionAction,
    )
    create_parser.add_argument(
        "--release-series",
        help="Create a release for a release series. Setting a release series "
        "is required if the latest tag version is newer then the to be "
        'released version. Examples: "1.2", "2", "22.4"',
    )

    next_version_group = create_parser.add_mutually_exclusive_group()

    next_version_group.add_argument(
        "--next-version",
        help=(
            "Sets the next version in project definition "
            "after the release. Default: set to next dev version"
        ),
    )

    next_version_group.add_argument(
        "--no-next-version",
        help="Don't set a next version after the release.",
        dest="next_version",
        action="store_false",
    )

    create_parser.add_argument(
        "--git-remote-name",
        help="The git remote name to push the commits and tag to",
    )
    create_parser.add_argument(
        "--git-tag-prefix",
        default="v",
        const="",
        nargs="?",
        help="Prefix for git tag versions. Default: %(default)s",
    )
    create_parser.add_argument(
        "--git-signing-key",
        help="The key to sign the commits and tag for a release",
        default=os.environ.get("GPG_SIGNING_KEY"),
    )
    create_parser.add_argument(
        "--project",
        help="The github project",
    )
    create_parser.add_argument(
        "--space",
        default="greenbone",
        help="User/Team name in github",
    )
    create_parser.add_argument(
        "--local",
        action="store_true",
        help="Only create release changes locally and do not upload them to a "
        "remote repository. Also do not create a GitHub release.",
    )
    create_parser.add_argument(
        "--conventional-commits-config",
        dest="cc_config",
        type=Path,
        help="Conventional commits config file (toml), including conventions."
        " If not set defaults are used.",
    )
    create_parser.add_argument(
        "--update-project",
        help="Update version in project files like pyproject.toml. By default "
        "project files are updated.",
        action=BooleanOptionalAction,
        default=True,
    )
    create_parser.add_argument(
        "--github-pre-release",
        help="Enforce uploading a release as GitHub pre-release. ",
        action="store_true",
    )

    sign_parser = subparsers.add_parser(
        "sign", help="Create signatures for an existing release"
    )
    sign_parser.set_defaults(func=sign)
    sign_parser.add_argument(
        "--signing-key",
        default=DEFAULT_SIGNING_KEY,
        help="The key to sign zip, tarballs of a release. Default %(default)s.",
    )
    sign_parser.add_argument(
        "--versioning-scheme",
        help="Versioning scheme to use for parsing and handling version "
        f"information. Choices are {', '.join(VERSIONING_SCHEMES.keys())}. "
        "Default: %(default)s",
        default="pep440",
        type=versioning_scheme_argument_type,
    )
    sign_parser.add_argument(
        "--release-version",
        help="Will release changelog as version. Must be PEP 440 compliant.",
    )
    sign_parser.add_argument(
        "--release-series",
        help="Sign release files for a release series. Setting a release "
        "series is required if the latest tag version is newer then the to be "
        'signed version. Examples: "1.2", "2", "22.4"',
    )
    sign_parser.add_argument(
        "--git-tag-prefix",
        default="v",
        const="",
        nargs="?",
        help="Prefix for git tag versions. Default: %(default)s",
    )
    sign_parser.add_argument(
        "--project",
        help="The github project",
    )
    sign_parser.add_argument(
        "--space",
        default="greenbone",
        help="user/team name in github",
    )

    sign_parser.add_argument(
        "--passphrase",
        help=(
            "Use gpg in a headless mode e.g. for "
            "the CI and use this passphrase for signing."
        ),
    )
    sign_parser.add_argument(
        "--dry-run", action="store_true", help="Do not upload signed files."
    )

    show_parser = subparsers.add_parser(
        "show",
        help="Show release information about the current release version and "
        "determine the next release version",
    )
    show_parser.set_defaults(func=show)
    show_parser.add_argument(
        "--versioning-scheme",
        help="Versioning scheme to use for parsing and handling version "
        f"information. Choices are {', '.join(VERSIONING_SCHEMES.keys())}. "
        "Default: %(default)s",
        default="pep440",
        type=versioning_scheme_argument_type,
    )
    show_parser.add_argument(
        "--release-type",
        help="Select the release type for calculating the release version. "
        f"Possible choices are: {to_choices(ReleaseType)}.",
        type=enum_type(ReleaseType),
    )
    show_parser.add_argument(
        "--release-version",
        help=(
            "Will release changelog as version. "
            "Default: lookup version in project definition."
        ),
        action=ReleaseVersionAction,
    )
    show_parser.add_argument(
        "--release-series",
        help="Create a release for a release series. Setting a release series "
        "is required if the latest tag version is newer then the to be "
        'released version. Examples: "1.2", "2", "22.4"',
    )
    show_parser.add_argument(
        "--git-tag-prefix",
        default="v",
        const="",
        nargs="?",
        help="Prefix for git tag versions. Default: %(default)s",
    )
    show_parser.add_argument(
        "--output-format",
        help="Print in the desired output format. "
        f"Possible choices are: {to_choices(OutputFormat)}.",
        type=enum_type(OutputFormat),
    )

    parsed_args = parser.parse_args(args)

    scheme: type[VersioningScheme] = getattr(
        parsed_args, "versioning_scheme", PEP440VersioningScheme
    )

    if parsed_args.func in (create_release, show):
        # check for release-type
        if not getattr(parsed_args, "release_type", None):
            parser.error("--release-type is required.")

        if (
            getattr(parsed_args, "release_version", None)
            and parsed_args.release_type != ReleaseType.VERSION
        ):
            parser.error(
                "--release-version requires --release-type "
                f"{ReleaseType.VERSION.value}"
            )

        if parsed_args.release_type == ReleaseType.VERSION and not getattr(
            parsed_args, "release_version", None
        ):
            parser.error(
                f"--release-type {ReleaseType.VERSION.value} requires to set "
                "--release-version"
            )

        next_version = getattr(parsed_args, "next_version", None)
        if next_version:
            parsed_args.next_version = scheme.parse_version(next_version)

    release_version = getattr(parsed_args, "release_version", None)
    if release_version:
        parsed_args.release_version = scheme.parse_version(release_version)

    token = os.environ.get("GITHUB_TOKEN")
    user = os.environ.get("GITHUB_USER")
    return user, token, parsed_args
