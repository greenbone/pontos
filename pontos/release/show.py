# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from argparse import Namespace
from enum import IntEnum, auto
from typing import Optional

from pontos.enum import StrEnum
from pontos.errors import PontosError
from pontos.git import Git
from pontos.github.actions import ActionIO
from pontos.release.command import Command
from pontos.release.helper import ReleaseType, get_next_release_version
from pontos.terminal import Terminal
from pontos.typing import SupportsStr
from pontos.version import Version, VersionError
from pontos.version.helper import get_last_release_version
from pontos.version.schemes import VersioningScheme


class ShowReleaseReturnValue(IntEnum):
    """
    Possible return values of ReleaseCommand
    """

    SUCCESS = 0
    NO_LAST_RELEASE_VERSION = auto()
    NO_RELEASE_VERSION = auto()


class OutputFormat(StrEnum):
    ENV = "env"
    JSON = "json"
    GITHUB_ACTION = "github-action"


class ShowReleaseCommand(Command):
    def __init__(self, *, terminal: Terminal, error_terminal: Terminal) -> None:
        super().__init__(terminal=terminal, error_terminal=error_terminal)
        self.git = Git()

    def run(  # type: ignore[override]
        self,
        *,
        output_format: OutputFormat = OutputFormat.ENV,
        versioning_scheme: VersioningScheme,
        release_type: ReleaseType,
        release_version: Optional[Version],
        release_series: Optional[str] = None,
        git_tag_prefix: Optional[str] = None,
    ) -> int:
        git_tag_prefix = git_tag_prefix or ""

        try:
            last_release_version = get_last_release_version(
                parse_version=versioning_scheme.parse_version,
                git_tag_prefix=git_tag_prefix,
                tag_name=(
                    f"{git_tag_prefix}{release_series}.*"
                    if release_series
                    else None
                ),
            )
        except PontosError as e:
            last_release_version = None
            self.print_warning(f"Could not determine last release version. {e}")

        if not last_release_version and not release_version:
            self.print_error("Unable to determine last release version.")
            return ShowReleaseReturnValue.NO_LAST_RELEASE_VERSION

        calculator = versioning_scheme.calculator()

        try:
            release_version = get_next_release_version(
                last_release_version=last_release_version,
                calculator=calculator,
                release_type=release_type,
                release_version=release_version,
            )
        except VersionError as e:
            self.print_error(f"Unable to determine release version. {e}")
            return ShowReleaseReturnValue.NO_RELEASE_VERSION

        if last_release_version:
            last_release_version_dict = {
                "last_release_version": str(last_release_version),
                "last_release_version_major": last_release_version.major,
                "last_release_version_minor": last_release_version.minor,
                "last_release_version_patch": last_release_version.patch,
            }
        else:
            last_release_version_dict = {
                "last_release_version": "",
                "last_release_version_major": "",
                "last_release_version_minor": "",
                "last_release_version_patch": "",
            }

        if output_format == OutputFormat.JSON:
            release_dict = {
                "release_version": str(release_version),
                "release_version_major": release_version.major,
                "release_version_minor": release_version.minor,
                "release_version_patch": release_version.patch,
            }
            release_dict.update(last_release_version_dict)
            self.terminal.print(json.dumps(release_dict, indent=2))
        elif output_format == OutputFormat.GITHUB_ACTION:
            with ActionIO.out() as output:
                output.write(
                    "last_release_version",
                    last_release_version_dict["last_release_version"],
                )
                output.write(
                    "last_release_version_major",
                    last_release_version_dict["last_release_version_major"],
                )
                output.write(
                    "last_release_version_minor",
                    last_release_version_dict["last_release_version_minor"],
                )
                output.write(
                    "last_release_version_patch",
                    last_release_version_dict["last_release_version_patch"],
                )
                output.write("release_version_major", release_version.major)
                output.write("release_version_minor", release_version.minor)
                output.write("release_version_patch", release_version.patch)
                output.write("release_version", release_version)
        else:
            self.terminal.print(
                "LAST_RELEASE_VERSION="
                f"{last_release_version_dict['last_release_version']}"
            )
            self.terminal.print(
                "LAST_RELEASE_VERSION_MAJOR="
                f"{last_release_version_dict['last_release_version_major']}"
            )
            self.terminal.print(
                "LAST_RELEASE_VERSION_MINOR="
                f"{last_release_version_dict['last_release_version_minor']}"
            )
            self.terminal.print(
                "LAST_RELEASE_VERSION_PATCH="
                f"{last_release_version_dict['last_release_version_patch']}"
            )
            self.terminal.print(f"RELEASE_VERSION={release_version}")
            self.terminal.print(
                f"RELEASE_VERSION_MAJOR={release_version.major}"
            )
            self.terminal.print(
                f"RELEASE_VERSION_MINOR={release_version.minor}"
            )
            self.terminal.print(
                f"RELEASE_VERSION_PATCH={release_version.patch}"
            )

        return ShowReleaseReturnValue.SUCCESS


def show(
    args: Namespace,
    terminal: Terminal,
    error_terminal: Terminal,
    **_kwargs,
) -> SupportsStr:
    return ShowReleaseCommand(
        terminal=terminal,
        error_terminal=error_terminal,
    ).run(
        versioning_scheme=args.versioning_scheme,
        release_type=args.release_type,
        release_version=args.release_version,
        git_tag_prefix=args.git_tag_prefix,
        release_series=args.release_series,
        output_format=args.output_format,
    )
