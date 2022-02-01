# Copyright (C) 2022 Greenbone Networks GmbH
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

""" Argument parser for pontos-github """

from argparse import ArgumentParser, FileType, Namespace
import os
from pathlib import Path
from typing import List

from pontos.github.cmds import file_status, pull_request
from pontos.github.api import FileStatus

body_template = Path(__file__).parent / "pr_template.md"


def from_env(name: str) -> str:
    return os.environ.get(name, name)


def parse_args(
    args: List[str] = None,
) -> Namespace:
    """Parsing args for nasl-lint

    Arguments:
    args        The programm arguments passed by exec
    term        The terminal to print"""

    parser = ArgumentParser(
        description="Greenbone GitHub API.",
    )

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        required=True,
        help='additional help',
        dest='command',
    )

    # create a PR from command line
    pr_parser = subparsers.add_parser(
        'pull-request', aliases=['pr', 'PR', 'pullrequest']
    )

    pr_parser.set_defaults(func=pull_request)

    pr_parser.add_argument(
        "repo", help=("GitHub repository (owner/name) to use")
    )

    pr_parser.add_argument(
        "head",
        help=("Branch to create a pull request from"),
    )

    pr_parser.add_argument(
        "target",
        default="main",
        help="Branch as as target for the pull. Default: %(default)s",
    )

    pr_parser.add_argument(
        "title",
        help=("Title for the pull request"),
    )

    pr_parser.add_argument(
        "-b",
        "--body",
        default=body_template.read_text(encoding="utf-8"),
        help=(
            "Description for the pull request. Can be formatted in Markdown."
        ),
    )

    pr_parser.add_argument(
        "-t",
        "--token",
        default="GITHUB_TOKEN",
        type=from_env,
        help=(
            "GitHub Token to access the repository. "
            "Default looks for environment variable 'GITHUB_TOKEN'"
        ),
    )

    # get files
    file_status_parser = subparsers.add_parser(
        'file-status', aliases=['status', 'FS']
    )

    file_status_parser.set_defaults(func=file_status)

    file_status_parser.add_argument(
        "repo", help=("GitHub repository (owner/name) to use")
    )

    file_status_parser.add_argument(
        "pull_request", help="Specify the Pull Request number", type=int
    )

    file_status_parser.add_argument(
        "-s",
        "--status",
        choices=FileStatus,
        default=[FileStatus.ADDED, FileStatus.MODIFIED],
        nargs='+',
        help=("What file status should be returned" "Default: %(default)s"),
    )

    file_status_parser.add_argument(
        "-o",
        "--output",
        type=FileType('w', encoding="utf-8"),
        help=(
            "Specify an output file. "
            "If none is given, output will be prompted"
            "The file will contain all files, with status "
            "changes, as given, separated by a newline"
        ),
    )

    file_status_parser.add_argument(
        "-t",
        "--token",
        default="GITHUB_TOKEN",
        type=from_env,
        help=(
            "GitHub Token to access the repository. "
            "Default looks for environment variable 'GITHUB_TOKEN'"
        ),
    )

    return parser.parse_args(args)
