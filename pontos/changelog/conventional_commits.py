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
from argparse import ArgumentParser
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import tomlkit

from pontos.errors import PontosError
from pontos.git import Git, GitError, TagSort
from pontos.release.helper import get_git_repository_name
from pontos.terminal import Terminal
from pontos.terminal.null import NullTerminal
from pontos.terminal.rich import RichTerminal

ADDRESS = "https://github.com/"

DEFAULT_CHANGELOG_CONFIG = """commit_types = [
    { message = "^add", group = "Added"},
    { message = "^remove", group = "Removed"},
    { message = "^change", group = "Changed"},
    { message = "^fix", group = "Bug Fixes"},
]

changelog_dir = "changelog"
"""


class ChangelogBuilderError(PontosError):
    """
    An error while building a changelog
    """


class ChangelogBuilder:
    """
    Creates Changelog files from conventional commits using the git log,
    from the latest tag.
    """

    def __init__(
        self,
        *,
        terminal: Terminal,
        current_version: str,
        next_version: str,
        space: str,
        project: Optional[str] = None,
        config: Optional[Path] = None,
    ):
        self._terminal = terminal

        if config:
            if not config.exists():
                raise ChangelogBuilderError(
                    f"Changelog Config file '{config.absolute()}' does not "
                    "exist."
                )

            self.config = tomlkit.parse(config.read_text(encoding="utf-8"))
        else:
            self.config = tomlkit.parse(DEFAULT_CHANGELOG_CONFIG)

        self.project = (
            project if project is not None else get_git_repository_name()
        )
        self.space = space

        self.current_version = current_version
        self.next_version = next_version

    def create_changelog_file(self, output: str) -> Optional[Path]:
        commit_list = self._get_git_log()
        commit_dict = self._sort_commits(commit_list)
        return self._build_changelog_file(commit_dict, output)

    def _get_git_log(self) -> List[str]:
        """Getting the git log for the current branch.

        If a last tag is found, the `git log` is searched up to the
          last tag, found by `git tag | sort -V | tail -1`.
        Else if no tag is found, the `git log` is searched full, assuming
          this is a initial release.

        Returns:
            A list of `git log` entries
        """
        git = Git()
        latest_tag = None
        try:
            latest_tag = git.list_tags(sort=TagSort.VERSION)[-1]
        except (GitError, IndexError):
            self._terminal.warning("No tag found.")

        if latest_tag:
            return git.log(f"{latest_tag}..HEAD", oneline=True)

        return git.log(oneline=True)

    def _sort_commits(self, commits: List[str]) -> Dict[str, List[str]]:
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
            raise ChangelogBuilderError("No conventional commits found.")

        return commit_dict

    def _build_changelog_file(
        self, commit_dict: Dict[str, List[str]], output: str
    ) -> Optional[Path]:
        """
        Building the changelog file with the passed dict.

        Args:
            commit_dict: dict containing sorted commits
            output: File name to write changelog into

        Returns:
            The path to the changelog file or None
        """

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

        if not changelog:
            return None

        changelog_dir: Path = Path.cwd() / self.config.get("changelog_dir")
        changelog_dir.mkdir(parents=True, exist_ok=True)

        output_path = changelog_dir / output
        output_path.write_text(changelog, encoding="utf-8")
        return output_path


def parse_args(args: Iterable[str] = None) -> ArgumentParser:
    parser = ArgumentParser(
        description="Conventional commits utility.",
        prog="pontos-changelog",
    )

    parser.add_argument(
        "--config",
        "-C",
        default="changelog.toml",
        type=Path,
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
        default="unreleased.md",
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
) -> None:
    parsed_args = parse_args(args)

    if parsed_args.quiet:
        term = NullTerminal()
    else:
        term = RichTerminal()

    term.bold_info("pontos-changelog")

    with term.indent():
        try:
            changelog_builder = ChangelogBuilder(
                terminal=term,
                config=parsed_args.config,
                project=args.project,
                space=args.space,
                current_version=args.current_version,
                next_version=args.next_version,
            )
            changelog_builder.create_changelog_file(args.output)
        except ChangelogBuilderError as e:
            term.error(str(e))
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            term.error(f'Could not run command "{e.cmd}".')
            term.out(f"Error was: {e.stderr}")
            sys.exit(1)

    sys.exit(0)
