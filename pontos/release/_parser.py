# SPDX-FileCopyrightText: 2020-2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import argparse
import os
from argparse import (
    ArgumentParser,
    ArgumentTypeError,
    BooleanOptionalAction,
    Namespace,
)
from pathlib import Path
from typing import Optional, Sequence, Tuple

import shtab

from pontos.enum import enum_choice, enum_type, to_choices
from pontos.version.schemes import (
    VERSIONING_SCHEMES,
    PEP440VersioningScheme,
    VersioningScheme,
    versioning_scheme_argument_type,
)

from .create import create_release
from .helper import ReleaseType
from .show import OutputFormat, show
from .sign import sign

DEFAULT_SIGNING_KEY = "0ED1E580"


class ReleaseVersionAction(
    argparse._StoreAction
):  # pylint: disable=protected-access
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, "release_type", ReleaseType.VERSION)
        setattr(namespace, self.dest, values)


def repository_type(value: str) -> str:
    """
    Validates the repository format of owner/name
    """
    splitted = value.split("/")
    if len(splitted) != 2:
        raise ArgumentTypeError(
            f"Invalid repository format {value}. Format must be owner/name."
        )
    return value


def add_create_parser(
    subparsers: argparse._SubParsersAction,
) -> None:
    create_parser: ArgumentParser = subparsers.add_parser(
        "create",
        aliases=["release"],
        help="Create a new release",
        description="Create a new release",
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
        choices=enum_choice(ReleaseType),
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
        "--repository",
        help="GitHub repository name (owner/name) where to publish the new "
        "release. For example octocat/Hello-World",
        type=repository_type,
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


def add_sign_parser(
    subparsers: argparse._SubParsersAction,
) -> None:
    sign_parser: ArgumentParser = subparsers.add_parser(
        "sign",
        help="Create signatures for an existing release",
        description="Create signatures for an existing release",
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
        "--repository",
        help="GitHub repository name (owner/name) where to download the "
        "release files from. For example octocat/Hello-World",
        type=repository_type,
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


def add_show_parser(
    subparsers: argparse._SubParsersAction,
) -> None:
    show_parser: ArgumentParser = subparsers.add_parser(
        "show",
        help="Show release information about the current release version and "
        "determine the next release version",
        description="Show release information about the current release "
        "version and determine the next release version",
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
        choices=enum_choice(ReleaseType),
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
        choices=enum_choice(OutputFormat),
    )


def parse_args(
    args: Optional[Sequence[str]] = None,
) -> Tuple[Optional[str], Optional[str], Namespace]:
    """
    Return user, token, parsed arguments
    """
    parser = ArgumentParser(
        description="Release handling utility.",
        prog="pontos-release",
    )
    shtab.add_argument_to(parser)

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Don't print messages to the terminal",
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="Valid subcommands",
        help="Additional help",
        dest="command",
        required=True,
    )

    add_create_parser(subparsers)
    add_sign_parser(subparsers)
    add_show_parser(subparsers)

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
