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


import re
import subprocess
import sys
from argparse import ArgumentParser, FileType, Namespace
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Union

import tomlkit
from tomlkit.toml_document import TOMLDocument

from pontos.helper import shell_cmd_runner
from pontos.release.helper import get_project_name
from pontos.terminal import Terminal
from pontos.terminal.terminal import ConsoleTerminal

ADDRESS = "https://github.com/"


class ChangelogBuilder:
    """Creates Changelog files from conventional commits
    using the git log, from the latest tag"""

    def __init__(
        self,
        terminal: Terminal,
        args: Namespace,
    ):
        self._terminal = terminal
        self.config: TOMLDocument = tomlkit.parse(
            args.config.read_text(encoding="utf-8")
        )
        self.project: str = (
            args.project
            if args.project is not None
            else get_project_name(shell_cmd_runner)
        )
        self.space: str = args.space
        changelog_dir: Path = Path.cwd() / self.config.get("changelog_dir")
        changelog_dir.mkdir(parents=True, exist_ok=True)
        self.output_file: Path = changelog_dir / args.output
        self.current_version: str = args.current_version
        self.next_version: str = args.next_version

    def create_changelog_file(self) -> Union[Path, None]:
        commit_list = self._get_git_log()
        commit_dict = self._sort_commits(commit_list)
        return self._build_changelog_file(commit_dict=commit_dict)

    def _get_git_log(self) -> Union[List[str], None]:
        """Getting the git log for the current branch.

        If a last tag is found, the `git log` is searched up to the
          last tag, found by `git tag | sort -V | tail -1`.
        Else if no tag is found, the `git log` is searched full, assuming
          this is a initial release.

        Returns:
            A list of `git log` entries or None
        """
        # https://stackoverflow.com/a/12083016/6725620
        # uses only latest tag for this branch
        # catch this CalledProcessError on
        # "No names found, cannot describe anything."
        cmd: str = "git log HEAD --oneline"
        try:
            # https://gist.github.com/rponte/fdc0724dd984088606b0
            proc: subprocess.CompletedProcess = shell_cmd_runner(
                "git tag | sort -V | tail -1"
            )
        except subprocess.CalledProcessError:
            self._terminal.warning("No tag found.")

        if proc.stdout and proc.stdout != "":
            cmd: str = f'git log "{proc.stdout.strip()}..HEAD" --oneline'

        proc = shell_cmd_runner(cmd)
        if proc.stdout and proc.stdout != "":
            return proc.stdout.strip().split("\n")
        return None

    def _sort_commits(self, commits: List[str]):
        """Sort the commits by commit type and group them
        in a dict
        ```
        {
            'Added:': [
                'commit 1 [1234567](..)',
                'commit 2 [1234568](..)',
                '...',
            ],
            'Fixed:': [
                ...
            ],
        }
        ```

        Returns
            The dict containing the commit messages"""
        # get the commit types from the toml
        commit_types = self.config.get("commit_types")

        commit_link = f"{ADDRESS}{self.space}/{self.project}/commit/"

        commit_dict = {}
        if commits and len(commits) > 0:
            for commit in commits:
                commit = commit.split(" ", maxsplit=1)
                for commit_type in commit_types:
                    reg = re.compile(
                        rf'{commit_type["message"]}\s?[:|-]', flags=re.I
                    )
                    match = reg.match(commit[1])
                    if match:
                        if commit_type["group"] not in commit_dict:
                            commit_dict[commit_type["group"]] = []

                        # remove the commit tag from commit message
                        cleaned_msg = (
                            commit[1].replace(match.group(0), "").strip()
                        )
                        commit_dict[commit_type["group"]].append(
                            f"{cleaned_msg} [{commit[0]}]"
                            f"({commit_link}{commit[0]})"
                        )
                        self._terminal.info(f"{commit[0]}: {cleaned_msg}")
        if not commit_dict:
            self._terminal.warning("No conventional commits found.")
            sys.exit(1)
        return commit_dict

    def _build_changelog_file(self, commit_dict: Dict) -> Union[str, None]:
        """Building the changelog file with the passed dict.

        Arguments:
            commit_dict     dict containing sorted commits

        Returns:
            The path to the changelog file or None"""

        # changelog header
        changelog = (
            "# Changelog\n\n"
            "All notable changes to this project "
            "will be documented in this file.\n\n"
        )
        if self.next_version:
            changelog += (
                f"## [{self.next_version}] - {date.today().isoformat()}\n"
            )
        else:
            changelog += "## [Unreleased]\n\n"

        # changelog entries
        commit_types = self.config.get("commit_types")
        for commit_type in commit_types:
            if commit_type["group"] in commit_dict.keys():
                changelog += f"\n## {commit_type['group']}\n"
                for msg in commit_dict[commit_type["group"]]:
                    changelog += f"* {msg}\n"

        # comparison line (footer)
        pre = "\n[Unreleased]: "
        compare_link = f"{ADDRESS}{self.space}/{self.project}/compare/"
        if self.next_version and self.current_version:
            pre = f"\n[{self.next_version}]: "
            diff = f"{self.current_version}...{self.next_version}"
        elif self.current_version:
            diff = f"\n{self.current_version}...HEAD"
        else:
            diff = "???...HEAD"

        changelog += f"{pre}{compare_link}{diff}"

        if changelog:
            self.output_file.write_text(changelog, encoding="utf-8")
            return self.output_file
        return None


def parse_args(args: Iterable[str] = None) -> ArgumentParser:
    parser = ArgumentParser(
        description="Conventional commits utility.",
        prog="pontos-changelog",
    )

    parser.add_argument(
        "--config",
        "-C",
        default=Path("changelog.toml"),
        type=FileType("r"),
        help="Conventional commits config file (toml), including conventions.",
    )

    parser.add_argument(
        "--project",
        help="The github project",
    )

    parser.add_argument(
        "--space",
        default="greenbone",
        help="User/Team name in github",
    )

    parser.add_argument(
        "--current-version",
        default="greenbone",
        help="Current version before these changes",
    )

    parser.add_argument(
        "--next-version",
        help="The planned release version",
    )

    parser.add_argument(
        "--output",
        "-o",
        default=Path("unreleased.md"),
        type=FileType("r"),
        help="The path to the output file (.md)",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Don't print messages to the terminal",
    )

    parser.add_argument(
        "--log-file",
        dest="log_file",
        type=str,
        help="Activate logging using the given file path",
    )

    return parser.parse_args(args=args)


def main(
    args=None,
):

    parsed_args = parse_args(args)

    term = ConsoleTerminal(
        verbose=1 if not parsed_args.quiet else 0,
        log_file=parsed_args.log_file,
    )

    term.bold_info("pontos-changelog")

    with term.indent():
        try:
            changelog_builder = ChangelogBuilder(
                terminal=term,
                args=parsed_args,
            )
            changelog_builder.create_changelog_file()
        except subprocess.CalledProcessError as e:
            term.error(f'Could not run command "{e.cmd}".')
            term.out(f"Error was: {e.stderr}")
            sys.exit(1)

    return sys.exit(0)
