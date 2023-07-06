# Copyright (C) 2021-2022 Greenbone AG
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
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, TypedDict, Union

import tomlkit

from pontos.changelog.errors import ChangelogBuilderError
from pontos.git import Git
from pontos.typing import SupportsStr

ADDRESS = "https://github.com/"

DEFAULT_CHANGELOG_CONFIG = """commit_types = [
    { message = "^add", group = "Added"},
    { message = "^remove", group = "Removed"},
    { message = "^change", group = "Changed"},
    { message = "^fix", group = "Bug Fixes"},
    { message = "^deps", group = "Dependencies"},
]
"""

CommitID = str


class CommitType(TypedDict):
    message: str
    group: str


class ConventionalCommits:
    """
    Extracts conventional commits from the git log

    Example:
        Collect the conventional commits between the tags "v1.2.3" and "v2.0.0"
        using the default config settings. Afterwards get the list of commits
        for the "Added" category.

        .. code-block:: python

            from pontos.changelog import ConventionalCommits

            collector = ConventionalCommits(space="my-org", project="my-project)
            commits = collector.get_commits(
                from_ref="v1.2.3",
                to_ref="v2.0.0",
            )
            added = commits.get("Added")
    """

    def __init__(
        self,
        space: str,
        project: str,
        config: Optional[Path] = None,
    ) -> None:
        """
        Create a new ConventionalCommits instance for collecting conventional
        commits from a git log.

        Args:
            space: GitHub space to use (organization or user name).
            project: GitHub project to create a changelog for
            config: Optional TOML config for conventional commit parsing
                settings.
        """
        if config:
            if not config.exists():
                raise ChangelogBuilderError(
                    f"Changelog Config file '{config.absolute()}' does not "
                    "exist."
                )

            self._config = tomlkit.parse(config.read_text(encoding="utf-8"))
        else:
            self._config = tomlkit.parse(DEFAULT_CHANGELOG_CONFIG)

        self._space = space
        self._project = project

    def get_commits(
        self,
        from_ref: Optional[SupportsStr] = None,
        to_ref: SupportsStr = "HEAD",
    ) -> dict[str, list[str]]:
        """
        Get all commits by conventional commit type between a range of git
        references.

        Args:
            from_ref: Git commit ID or reference where to start looking for
                conventional commits. If None, to_ref is ignored and all
                 conventional commits are returned.
            to_ref: Git commit ID or reference where to stop looking for
                conventional commits. By default HEAD is used.

        Returns:
            A dict containing the grouped commit messages
        """
        commit_list = self._get_git_log(from_ref, to_ref)
        return self._sort_commits(commit_list)

    def commit_types(self) -> list[CommitType]:
        return self._config.get("commit_types", [])

    def _get_git_log(
        self, from_ref: Optional[SupportsStr], to_ref: SupportsStr = "HEAD"
    ) -> list[str]:
        """Getting the git log for the a range of commits.

        Requires the fitting branch to be checked out if to_ref is not set.

        Args:
            from_ref: Git commit ID or reference of the first log entry. If
                None, to_ref is ignored and all log entries of the current
                checked out branch are returned.
            to_ref: Git commit ID or reference where to stop considering the
                log entries. By default HEAD is used which points to the last
                commit of the checked out branch.

        Returns:
            A list of `git log` entries
        """
        git = Git()
        if not from_ref:
            return git.log(oneline=True)

        return git.log(
            f"{from_ref}..{to_ref}",
            oneline=True,
        )

    def _sort_commits(self, commits: list[str]) -> dict[str, list[str]]:
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
            The dict containing the commit messages
        """
        commit_link = f"{ADDRESS}{self._space}/{self._project}/commit/"

        commit_dict = {}
        if commits and len(commits) > 0:
            for commit in commits:
                commit = commit.split(" ", maxsplit=1)
                for commit_type in self.commit_types():
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

        return commit_dict


class ChangelogBuilder:
    """
    Creates Changelog from conventional commits using the git log
    from the latest version.

    Example:
        Create a changelog as a string from the changes between git tags
        "v1.2.3" and "v2.0.0" using the default config settings.

        .. code-block:: python

            from pontos.changelog import ChangelogBuilder

            builder = ChangelogBuilder(space="my-org", project="my-project)
            changelog = builder.create_changelog(
                last_version="1.2.3",
                next_version="2.0.0",
            )
    """

    def __init__(
        self,
        *,
        space: str,
        project: str,
        git_tag_prefix: Optional[str] = "v",
        config: Optional[Path] = None,
    ) -> None:
        """
        Create a new ChangelogBuilder instance.

        Args:
            space: GitHub space to use (organization or user name).
            project: GitHub project to create a changelog for
            git_tag_prefix: Git tag prefix to use when checking for git tags.
                Default is "v".
            config: TOML config for conventional commit parsing settings
        """
        self.project = project
        self.space = space

        self.git_tag_prefix = git_tag_prefix
        self._conventional_commits = ConventionalCommits(
            self.space,
            self.project,
            config,
        )

    def create_changelog(
        self,
        *,
        last_version: Optional[SupportsStr] = None,
        next_version: Optional[SupportsStr] = None,
    ) -> str:
        """
        Create a changelog

        Args:
            last_version: Version of the last release. If None it is considered
                as the first release.
            next_version: Version of the to be created release the changelog
                corresponds to. If None a changelog for an unrelease version
                will be created.

        Returns:
            The created changelog content.
        """
        commit_dict = self._conventional_commits.get_commits(
            f"{self.git_tag_prefix}{last_version}" if last_version else None
        )
        return self._build_changelog(last_version, next_version, commit_dict)

    def create_changelog_file(
        self,
        output: Union[str, Path],
        *,
        last_version: Optional[SupportsStr] = None,
        next_version: Optional[SupportsStr] = None,
    ) -> None:
        """
        Create a changelog and write the changelog to a file

        Args:
            output: A file path where to store the changelog
            last_version: Version of the last release. If None it is considered
                as the first release.
            next_version: Version of the to be created release the changelog
                corresponds to. If None a changelog for an unrelease version
                will be created.
        """
        changelog = self.create_changelog(
            last_version=last_version, next_version=next_version
        )
        self._write_changelog_file(changelog, output)

    def _get_first_commit(self) -> str:
        """
        Git the first commit ID for the current branch
        """
        git = Git()
        return git.rev_list("HEAD", max_parents=0, abbrev_commit=True)[0]

    def _build_changelog(
        self,
        last_version: Optional[SupportsStr],
        next_version: Optional[SupportsStr],
        commit_dict: Dict[str, List[str]],
    ) -> str:
        """
        Building the changelog from the passed commit information.

        Args:
            commit_dict: dict containing sorted commits

        Returns:
            The changelog content
        """

        # changelog header
        changelog = []
        if next_version:
            changelog.append(
                f"## [{next_version}] - {date.today().isoformat()}"
            )
        else:
            changelog.append("## [Unreleased]")

        # changelog entries
        for commit_type in self._conventional_commits.commit_types():
            if commit_type["group"] in commit_dict.keys():
                changelog.append(f"\n## {commit_type['group']}")
                for msg in commit_dict[commit_type["group"]]:
                    changelog.append(f"* {msg}")

        # comparison line (footer)
        pre = "\n[Unreleased]: "
        compare_link = f"{ADDRESS}{self.space}/{self.project}/compare/"
        if next_version and last_version:
            pre = f"\n[{next_version}]: "
            diff = (
                f"{self.git_tag_prefix}{last_version}..."
                f"{self.git_tag_prefix}{next_version}"
            )
        elif next_version:
            first_commit = self._get_first_commit()
            pre = f"\n[{next_version}]: "
            diff = f"{first_commit}...{self.git_tag_prefix}{next_version}"
        elif last_version:
            # unreleased version
            diff = f"{self.git_tag_prefix}{last_version}...HEAD"
        else:
            # unreleased version
            first_commit = self._get_first_commit()
            diff = f"{first_commit}...HEAD"

        changelog.append(f"{pre}{compare_link}{diff}")

        return "\n".join(changelog)

    def _write_changelog_file(
        self, changelog: str, output: Union[str, Path]
    ) -> None:
        """
        Write changelog to an output file

        Args:
            changelog: Changelog content to write to output file
            output: File name to write changelog into
        """

        changelog_file = Path(output)

        changelog_dir = changelog_file.parent
        changelog_dir.mkdir(parents=True, exist_ok=True)

        changelog_file.write_text(changelog, encoding="utf-8")
