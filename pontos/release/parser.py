# Copyright (C) 2020-2023 Greenbone Networks GmbH
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
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from enum import Enum
from pathlib import Path
from typing import Callable, Tuple, Type

from pontos.release.helper import ReleaseType

from .prepare import prepare
from .release import release
from .sign import sign

DEFAULT_CHANGELOG_CONFIG_FILE = "changelog.toml"
DEFAULT_SIGNING_KEY = "0ED1E580"


def to_choices(enum: Type[Enum]) -> list[str]:
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


def parse_args(args) -> Tuple[str, str, Namespace]:
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

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.set_defaults(func=prepare)
    prepare_parser.add_argument(
        "--release-version",
        help="Version for the created release. Must be PEP 440 compliant."
        "Implicitly sets --release-type version.",
        action=ReleaseVersionAction,
    )

    version_group = prepare_parser.add_mutually_exclusive_group()
    version_group.add_argument(
        "--calendar",
        dest="release_type",
        help=(
            "Automatically calculate calendar release version, from current"
            " version and date. Deprecated, user --release-type "
            f"{ReleaseType.CALENDAR.value} instead."
        ),
        const=ReleaseType.CALENDAR,
        action="store_const",
    )
    version_group.add_argument(
        "--patch",
        dest="release_type",
        help="Release next patch version: "
        "e.g. x.x.3 -> x.x.4. Deprecated, "
        f"use --release-type {ReleaseType.PATCH.value} instead.",
        const=ReleaseType.PATCH,
        action="store_const",
    )
    version_group.add_argument(
        "--release-type",
        help="Select the release type for calculating the release version. "
        f"Possible choices are: {to_choices(ReleaseType)}.",
        type=enum_type(ReleaseType),
    )

    prepare_parser.add_argument(
        "--git-signing-key",
        help="The key to sign the commits and tag for a release",
    )
    prepare_parser.add_argument(
        "--git-tag-prefix",
        default="v",
        help="Prefix for git tag versions. Default: %(default)s",
    )
    prepare_parser.add_argument(
        "--space",
        default="greenbone",
        help="User/Team name in github",
    )
    prepare_parser.add_argument(
        "--project",
        help="The github project",
    )
    prepare_parser.add_argument(
        "--conventional-commits-config",
        dest="cc_config",
        default=Path(DEFAULT_CHANGELOG_CONFIG_FILE),
        type=Path,
        help="Conventional commits config file (toml), including conventions.",
    )

    release_parser = subparsers.add_parser("release")
    release_parser.set_defaults(func=release)
    release_parser.add_argument(
        "--release-version",
        help=(
            "Will release changelog as version. Must be PEP 440 compliant. "
            "default: lookup version in project definition."
        ),
    )

    release_parser.add_argument(
        "--next-version",
        help=(
            "Sets the next PEP 440 compliant version in project definition "
            "after the release. default: set to next dev version"
        ),
    )

    release_parser.add_argument(
        "--git-remote-name",
        help="The git remote name to push the commits and tag to",
    )
    release_parser.add_argument(
        "--git-tag-prefix",
        default="v",
        help="Prefix for git tag versions. Default: %(default)s",
    )
    release_parser.add_argument(
        "--git-signing-key",
        help="The key to sign the commits and tag for a release",
    )
    release_parser.add_argument(
        "--project",
        help="The github project",
    )
    release_parser.add_argument(
        "--space",
        default="greenbone",
        help="User/Team name in github",
    )

    sign_parser = subparsers.add_parser("sign")
    sign_parser.set_defaults(func=sign)
    sign_parser.add_argument(
        "--signing-key",
        default=DEFAULT_SIGNING_KEY,
        help="The key to sign zip, tarballs of a release. Default %(default)s.",
    )
    sign_parser.add_argument(
        "--release-version",
        help="Will release changelog as version. Must be PEP 440 compliant.",
    )
    sign_parser.add_argument(
        "--git-tag-prefix",
        default="v",
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
    parsed_args = parser.parse_args(args)

    if parsed_args.func is prepare:
        # check for release-type
        if not getattr(parsed_args, "release_type"):
            parser.error("--release-type is required.")

        if (
            getattr(parsed_args, "release_version")
            and parsed_args.release_type != ReleaseType.VERSION
        ):
            parser.error(
                "--release-version requires --release-type "
                f"{ReleaseType.VERSION.value}"
            )

        if parsed_args.release_type == ReleaseType.VERSION and not getattr(
            parsed_args, "release_version"
        ):
            parser.error(
                f"--release-type {ReleaseType.VERSION.value} requires to set "
                "--release-version"
            )

    token = os.environ.get("GITHUB_TOKEN")
    user = os.environ.get("GITHUB_USER")
    return user, token, parsed_args
