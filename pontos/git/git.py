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

import subprocess
from enum import Enum
from os import PathLike, fspath
from pathlib import Path
from typing import List, Optional, Union


class GitError(subprocess.CalledProcessError):
    """
    Error raised while executing a git command
    """

    def __str__(self) -> str:
        cmd = " ".join(self.cmd)
        return (
            f"Git command '{cmd}' returned "
            f"non-zero exit status {str(self.returncode)}"
        )


def exec_git(
    *args: str,
    ignore_errors: Optional[bool] = False,
    cwd: Optional[PathLike] = None,
) -> str:
    """
    Internal module function to abstract calling git via subprocess. Most of the
    cases the Git class should be used.

    Args:
        ignore_errors: Set to True if errors while running git should be
            ignored. Default: False.
        cwd: Set the current working directory

    Raises:
        GitError: Will be raised if ignore_errors is False and git returns with
            an exit code != 0.

    Returns:
        stdout output of git command or empty string if ignore_errors is True
        and git returns with an exit code != 0.
    """
    try:
        cmd_args = ["git"]
        cmd_args.extend(args)
        output = subprocess.check_output(
            cmd_args, cwd=fspath(cwd) if cwd else None
        )
        return output.decode()
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            return ""
        raise GitError(e.returncode, e.cmd, e.output, e.stderr) from None


class MergeStrategy(Enum):
    ORT = "ort"
    ORT_OURS = "ort-ours"
    RECURSIVE = "recursive"
    RESOLVE = "resolve"
    OCTOPUS = "octopus"
    OURS = "ours"
    SUBTREE = "subtree"


class ConfigScope(Enum):
    GLOBAL = "global"
    LOCAL = "local"
    SYSTEM = "system"
    WORKTREE = "worktree"


class TagSort(Enum):
    VERSION = "version:refname"


class Git:
    """
    Run git commands as subprocesses
    """

    def __init__(self, cwd: Optional[Path] = None) -> None:
        """
        Create a new Git instance

        Args:
            cwd: Set the current working directory for the git commands
        """
        self._cwd = cwd.absolute() if cwd else None

    @property
    def cwd(self) -> Optional[Path]:
        """
        Get the current working directory as Path
        """
        return self._cwd

    @cwd.setter
    def cwd(self, cwd: Path) -> None:
        """
        Set the current working directory for all following git commands
        """
        self._cwd = cwd.absolute()

    def init(self, *, bare: Optional[bool] = False) -> None:
        """
        Init a git repository

        Args:
            bare: Wether to create a `bare` repository or not.
                  Defaults to false.
        """
        args = ["init"]
        if bare:
            args.append("--bare")
        exec_git(*args, cwd=self._cwd)

    def create_branch(
        self, branch: str, *, start_point: Optional[str] = None
    ) -> None:
        """
        Create a new branch

        Args:
            branch: Name of the branch to be created
            start_point: An optional git reference (branch, tag, sha, ...) from
                         where to start the branch
        """
        args = ["checkout", "-b", branch]
        if start_point:
            args.append(start_point)

        exec_git(*args, cwd=self._cwd)

    def rebase(
        self,
        base: str,
        *,
        head: Optional[str] = None,
        onto: Optional[str] = None,
        strategy: Optional[MergeStrategy] = None,
    ) -> None:
        """
        Rebase a branch

        Args:
            base: Apply changes of this branch.
            head: Apply changes on this branch. If not set the current branch is
                  used.
            onto: Apply changes on top of this branch.
            strategy: Merge strategy to use.
        """
        args = ["rebase"]

        if strategy:
            if strategy == MergeStrategy.ORT_OURS:
                args.extend(["--strategy", "ort", "-X", "ours"])
            else:
                args.extend(["--strategy", strategy.value])

        if onto:
            args.extend(["--onto", onto])

        args.append(base)

        if head:
            args.append(head)

        exec_git(*args, cwd=self._cwd)

    def clone(
        self,
        repo_url: str,
        destination: Path,
        *,
        branch: Optional[str] = None,
        remote: Optional[str] = None,
        depth: Optional[int] = None,
    ) -> None:
        """
        Clone a repository

        Args:
            repo_url: URL of the repo to clone
            destination: Where to checkout the clone
            branch: Branch to checkout. By default the default branch is used.
            remote: Store repo url under this remote name
        """
        args = ["clone"]
        if remote:
            args.extend(["-o", remote])
        if branch:
            args.extend(["-b", branch])
        if depth:
            args.extend(["--depth", str(depth)])
        args.extend([repo_url, str(destination.absolute())])

        exec_git(
            *args,
            cwd=self._cwd,
        )

    def push(
        self,
        *,
        remote: Optional[str] = None,
        branch: Optional[str] = None,
        follow_tags: bool = False,
        force: Optional[bool] = None,
    ) -> None:
        """
        Push changes to remote repository

        Args:
            remote: Push changes to the named remote
            branch: Branch to push. Will only be considered in combination with
                    a remote.
            follow_tags: Push all tags pointing to a commit included in the to
                         be pushed branch.
            force: Force push changes.
        """
        args = ["push"]
        if follow_tags:
            args.append("--follow-tags")
        if force:
            args.append("--force")
        if remote:
            args.append(remote)
            if branch:
                args.append(branch)

        exec_git(*args, cwd=self._cwd)

    def config(
        self,
        key: str,
        value: Optional[str] = None,
        *,
        scope: Optional[ConfigScope] = None,
    ) -> str:
        """
        Get and set a git config

        Args:
            key: Key of the Git config setting. For example: core.filemode
            value: Value to set for a Git setting.
            scope: Scope of the setting.
        """
        args = ["config"]
        if scope:
            args.append(f"--{scope.value}")

        args.append(key)

        if value is not None:
            args.append(value)

        return exec_git(*args, cwd=self._cwd)

    def cherry_pick(self, commits: Union[str, List[str]]) -> None:
        """
        Apply changes of a commit(s) to the current branch

        Args:
            commit: A single git reference (e.g. sha) of the commit or a list
                    of git references.
        """
        if isinstance(commits, str):
            commits = [commits]

        args = ["cherry-pick"]
        args.extend(commits)

        exec_git(*args, cwd=self._cwd)

    def list_tags(self, *, sort: Optional[TagSort] = None) -> List[str]:
        """
        List all available tags
        """
        args = ["tag", "-l"]
        if sort:
            args.append(f"--sort={sort.value}")
        return exec_git(*args, cwd=self._cwd).splitlines()

    def add(self, files: Union[PathLike, List[PathLike]]) -> None:
        """
        Add files to the git staging area

        Args:
            files: A single file or a list of files to add to the staging area
        """
        if isinstance(files, (PathLike, str, bytes)):
            files = [files]

        args = ["add"]
        args.extend([fspath(file) for file in files])

        exec_git(*args, cwd=self._cwd)

    def commit(
        self,
        message: str,
        *,
        verify: Optional[bool] = None,
        gpg_signing_key: Optional[str] = None,
    ) -> None:
        """
        Create a new commit

        Args:
            message: Message of the commit
            verify: Set to False to skip git hooks
            gpg_signing_key: GPG Key ID to use to sign the commit
        """
        args = ["commit"]
        if verify is False:
            args.append("--no-verify")
        if gpg_signing_key:
            args.append(f"-S{gpg_signing_key}")

        args.extend(["-m", message])

        exec_git(*args, cwd=self._cwd)

    def tag(
        self,
        tag: str,
        *,
        gpg_key_id: Optional[str] = None,
        message: Optional[str] = None,
        force: Optional[bool] = False,
    ) -> None:
        """
        Create a Tag

        Args:
            tag: Tag name to create.
            gpg_key_id: GPG Key to sign the tag.
            message: Use message to annotate the given tag.
            force: True to replace an existing tag.
        """
        args = ["tag"]

        if gpg_key_id:
            args.extend(["-u", gpg_key_id])

        if message:
            args.extend(["-m", message])

        if force:
            args.append("--force")

        args.append(tag)

        exec_git(*args, cwd=self._cwd)

    def fetch(
        self,
        remote: Optional[str] = None,
        refspec: Optional[str] = None,
        *,
        verbose: bool = False,
    ) -> None:
        """
        Fetch from changes from remote

        Args:
            remote: Remote to fetch changes from
            refspec: Specifies which refs to fetch and which local refs to
                update.
            verbose: Print verbose output.
        """
        args = ["fetch"]

        if remote:
            args.append(remote)
        if refspec:
            args.append(refspec)

        if verbose:
            args.append("-v")

        exec_git(*args, cwd=self._cwd)

    def add_remote(self, remote: str, url: str) -> None:
        """
        Add a new git remote

        Args:
            remote: Name of the new remote
            url: Git URL of the remote repository
        """

        args = ["remote", "add", remote, url]

        exec_git(*args, cwd=self._cwd)

    def remote_url(self, remote: str = "origin") -> str:
        """
        Get the url of a remote

        Args:
            remote: Name of the remote. Default: origin.
        """
        args = ["remote", "get-url", remote]
        return exec_git(*args, cwd=self._cwd)

    def checkout(
        self, branch: str, *, start_point: Optional[str] = None
    ) -> None:
        """
        Checkout a branch

        Args:
            branch: Branch to checkout or new branch name if starting_point is
                given.
            start_point: Create a new branch from this git ref.
        """

        if start_point:
            args = ["checkout", "-b", branch, start_point]
        else:
            args = ["checkout", branch]

        exec_git(*args, cwd=self._cwd)

    def log(self, *log_args: str, oneline: Optional[bool] = None) -> List[str]:
        """
        Get log of a git repository

        Args:
        """
        args = ["log"]
        if oneline:
            args.append("--oneline")

        args.extend(log_args)

        return exec_git(*args, cwd=self._cwd).splitlines()
