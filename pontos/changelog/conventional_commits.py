# Copyright (C) 2021-2022 Greenbone Networks GmbH
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


from argparse import Namespace, ArgumentParser, FileType
from datetime import date
from pathlib import Path
import re
import sys
import subprocess
from typing import Callable, Dict, List, Union

import tomlkit
from tomlkit.toml_document import TOMLDocument

from pontos.terminal import _set_terminal, error, info, out, warning
from pontos.terminal.terminal import Terminal
from pontos.release.helper import (
    get_project_name,
)


class ChangelogBuilder:
    """Creates Changelog files from conventional commits
    using the git log, from the latest tag"""

    def __init__(
        self,
        shell_cmd_runner: Callable,
        args: Namespace,
    ):
        self.shell_cmd_runner: Callable = shell_cmd_runner
        self.config: TOMLDocument = tomlkit.parse(
            args.config.read_text(encoding='utf-8')
        )
        self.project: str = (
            args.project
            if args.project is not None
            else get_project_name(self.shell_cmd_runner)
        )
        self.space: str = args.space
        changelog_dir: Path = Path.cwd() / self.config.get('changelog_dir')
        changelog_dir.mkdir(parents=True, exist_ok=True)
        self.output_file: Path = changelog_dir / args.output
        self.current_version: str = args.current_version
        self.next_version: str = args.next_version

    def create_changelog_file(self) -> Union[Path, None]:
        commit_list = self.get_git_log()
        commit_dict = self.sort_commits(commit_list)
        self.build_changelog_file(commit_dict=commit_dict)

        return self.output_file if self.output_file else None

    def get_git_log(self) -> Union[List[str], None]:
        # https://stackoverflow.com/a/12083016/6725620
        # uses only latest tag for this branch
        proc = self.shell_cmd_runner(
            'git log "$(git describe --tags --abbrev=0)..HEAD" --oneline'
        )
        if proc.stdout and proc.stdout != '':
            return proc.stdout.strip().split('\n')
        return None

    def sort_commits(self, commits: List[str]):
        # get the commit types from the toml
        commit_types = self.config.get('commit_types')

        commit_dict = {}
        if commits and len(commits) > 0:
            for commit in commits:
                commit = commit.split(' ', maxsplit=1)
                for commit_type in commit_types:
                    reg = re.compile(
                        fr'{commit_type["message"]}\s?[:|-]', flags=re.I
                    )
                    match = reg.match(commit[1])
                    if match:
                        cleaned_msg = (
                            commit[1].replace(match.group(0), '').strip()
                        )
                        info(
                            f'{cleaned_msg} [{commit[0]}](https://github.com/'
                            f'{self.space}/{self.project}/commit/{commit[0]})'
                        )
                        if commit_type['group'] not in commit_dict:
                            commit_dict[commit_type['group']] = []
                        commit_dict[commit_type['group']].append(
                            f'{cleaned_msg} [{commit[0]}](https://github.com/'
                            f'{self.space}/{self.project}/commit/{commit[0]})'
                        )
        else:
            warning("No conventional commits found.")
            sys.exit(1)
        if not commit_dict:
            warning("No conventional commits found.")
            sys.exit(1)
        return commit_dict

    def build_changelog_file(self, commit_dict: Dict):
        # changelog header
        changelog = (
            "# Changelog\n\n"
            "All notable changes to this project "
            "will be documented in this file.\n\n"
        )
        if self.next_version:
            changelog += (
                f'## [{self.next_version}] - {date.today().isoformat()}\n'
            )
        else:
            changelog += '## [Unreleased]\n\n'
        commit_types = self.config.get('commit_types')

        # changelog entries
        for commit_type in commit_types:
            if commit_type['group'] in commit_dict.keys():
                changelog += f"\n## {commit_type['group']}\n"
                for msg in commit_dict[commit_type['group']]:
                    changelog += f"* {msg}\n"

        # comparison line
        if self.next_version and self.current_version:
            changelog += (
                f'\n[{self.next_version}]: https://github.com/{self.space}/'
                f'{self.project}/compare/{self.current_version}...'
                f'{self.next_version}'
            )
        elif self.current_version:
            changelog += (
                f'\n[Unreleased]: https://github.com/{self.space}/'
                f'{self.project}/compare/{self.current_version}...HEAD'
            )
        else:
            changelog += (
                f'\n[Unreleased]: https://github.com/{self.space}/'
                f'{self.project}/compare/<?>...HEAD'
            )

        self.output_file.write_text(changelog, encoding='utf-8')


def initialize_default_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description='Conventional commits utility.',
        prog='pontos-changelog',
    )

    parser.add_argument(
        '--config',
        '-C',
        default=Path('changelog.toml'),
        type=FileType('r'),
        help="Conventional commits config file (toml), including conventions.",
    )

    parser.add_argument(
        '--project',
        help='The github project',
    )

    parser.add_argument(
        '--space',
        default='greenbone',
        help='User/Team name in github',
    )

    parser.add_argument(
        '--current-version',
        default='greenbone',
        help='Current version before these changes',
    )

    parser.add_argument(
        '--next-version',
        help='The planned release version',
    )

    parser.add_argument(
        '--output',
        '-o',
        default=Path('unreleased.md'),
        type=FileType('r'),
        help='The path to the output file (.md)',
    )

    return parser


def main(
    shell_cmd_runner=lambda x: subprocess.run(
        x,
        shell=True,
        check=True,
        errors="utf-8",  # use utf-8 encoding for error output
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ),
    args=None,
):
    term = Terminal()
    _set_terminal(term)

    term.bold_info('pontos-changelog')

    parser = initialize_default_parser()
    parsed_args = parser.parse_args(args)

    with term.indent():
        try:
            changelog_builder = ChangelogBuilder(
                shell_cmd_runner=shell_cmd_runner,
                args=parsed_args,
            )
            changelog_builder.create_changelog_file()
        except subprocess.CalledProcessError as e:
            error(f'Could not run command "{e.cmd}".')
            out(f'Error was: {e.stderr}')
            sys.exit(1)

    return sys.exit(0)
