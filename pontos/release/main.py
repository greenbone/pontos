# -*- coding: utf-8 -*-
# pontos/release/release.py
# Copyright (C) 2020-2022 Greenbone Networks GmbH
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

from argparse import FileType, Namespace, ArgumentParser
import sys
import subprocess
import os

from pathlib import Path
from typing import Tuple

import requests

from pontos import changelog
from pontos.terminal import _set_terminal, error, out
from pontos.terminal.terminal import Terminal
from pontos import version

from .prepare import prepare
from .sign import sign
from .release import release


def initialize_default_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description='Release handling utility.',
        prog='pontos-release',
    )

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='additional help',
        dest='command',
    )

    prepare_parser = subparsers.add_parser('prepare')
    prepare_parser.set_defaults(func=prepare)
    version_group = prepare_parser.add_mutually_exclusive_group(required=True)
    version_group.add_argument(
        '--release-version',
        help='Will release changelog as version. Must be PEP 440 compliant',
    )
    version_group.add_argument(
        '--calendar',
        help=(
            'Automatically calculate calendar release version, from current'
            ' version and date.'
        ),
        action='store_true',
    )
    version_group.add_argument(
        '--patch',
        help=('Release next patch version: ' 'e.g. x.x.3 -> x.x.4'),
        action='store_true',
    )

    prepare_parser.add_argument(
        '--git-signing-key',
        help='The key to sign the commits and tag for a release',
    )
    prepare_parser.add_argument(
        '--git-tag-prefix',
        default='v',
        help='Prefix for git tag versions. Default: %(default)s',
    )
    prepare_parser.add_argument(
        '--changelog',
        help=(
            'The CHANGELOG file path, defaults '
            'to CHANGELOG.md in the repository root directory'
        ),
    )
    prepare_parser.add_argument(
        '--space',
        default='greenbone',
        help='User/Team name in github',
    )
    prepare_parser.add_argument(
        '--project',
        help='The github project',
    )
    prepare_parser.add_argument(
        '--conventional-commits',
        '-CC',
        help=(
            'Wether to use conventional commits and create '
            'the changelog directly from the git log'
        ),
        action='store_true',
    )
    prepare_parser.add_argument(
        '--conventional-commits-config',
        dest='cc_config',
        default=Path('changelog.toml'),
        type=FileType('r'),
        help="Conventional commits config file (toml), including conventions.",
    )

    release_parser = subparsers.add_parser('release')
    release_parser.set_defaults(func=release)
    release_parser.add_argument(
        '--release-version',
        help=(
            'Will release changelog as version. Must be PEP 440 compliant. '
            'default: lookup version in project definition.'
        ),
    )

    release_parser.add_argument(
        '--next-version',
        help=(
            'Sets the next PEP 440 compliant version in project definition '
            'after the release. default: set to next dev version'
        ),
    )

    release_parser.add_argument(
        '--git-remote-name',
        help='The git remote name to push the commits and tag to',
    )
    release_parser.add_argument(
        '--git-tag-prefix',
        default='v',
        help='Prefix for git tag versions. Default: %(default)s',
    )
    release_parser.add_argument(
        '--git-signing-key',
        help='The key to sign the commits and tag for a release',
    )
    release_parser.add_argument(
        '--project',
        help='The github project',
    )
    release_parser.add_argument(
        '--space',
        default='greenbone',
        help='User/Team name in github',
    )
    release_parser.add_argument(
        '--changelog',
        help=(
            'The CHANGELOG file path, defaults '
            'to CHANGELOG.md in the repository root directory'
        ),
    )
    release_parser.add_argument(
        '--conventional-commits',
        '-CC',
        help=(
            'Wether to use conventional commits and create '
            'the changelog directly from the git log'
        ),
        action='store_true',
    )

    sign_parser = subparsers.add_parser('sign')
    sign_parser.set_defaults(func=sign)
    sign_parser.add_argument(
        '--signing-key',
        default='0ED1E580',
        help='The key to sign zip, tarballs of a release. Default %(default)s.',
    )
    sign_parser.add_argument(
        '--release-version',
        help='Will release changelog as version. Must be PEP 440 compliant.',
    )
    sign_parser.add_argument(
        '--git-tag-prefix',
        default='v',
        help='Prefix for git tag versions. Default: %(default)s',
    )
    sign_parser.add_argument(
        '--project',
        help='The github project',
    )
    sign_parser.add_argument(
        '--space',
        default='greenbone',
        help='user/team name in github',
    )

    sign_parser.add_argument(
        '--passphrase',
        help=(
            'Use gpg in a headless mode e.g. for '
            'the CI and use this passphrase for signing.'
        ),
    )
    return parser


def parse(args=None) -> Tuple[str, str, Namespace]:
    parser = initialize_default_parser()
    commandline_arguments = parser.parse_args(args)
    token = os.environ['GITHUB_TOKEN'] if not args else 'TOKEN'
    user = os.environ['GITHUB_USER'] if not args else 'USER'
    return (user, token, commandline_arguments)


def main(
    shell_cmd_runner=lambda x: subprocess.run(
        x,
        shell=True,
        check=True,
        errors="utf-8",  # use utf-8 encoding for error output
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ),
    _path: Path = Path,
    _requests: requests = requests,
    _version: version = version,
    _changelog: changelog = changelog,
    leave: bool = True,
    args=None,
):
    username, token, parsed_args = parse(args)
    term = Terminal()
    _set_terminal(term)

    term.bold_info(f'pontos-release => {parsed_args.func.__name__}')

    with term.indent():
        try:
            if not parsed_args.func(
                shell_cmd_runner,
                parsed_args,
                path=_path,
                username=username,
                token=token,
                changelog_module=_changelog,
                requests_module=_requests,
                version_module=_version,
            ):
                return sys.exit(1) if leave else False
        except subprocess.CalledProcessError as e:
            if not '--passphrase' in e.cmd:
                error(f'Could not run command "{e.cmd}".')
            else:
                error('Headless signing failed.')
            out(f'Error was: {e.stderr}')
            sys.exit(1)

    return sys.exit(0) if leave else True


if __name__ == '__main__':
    main()
