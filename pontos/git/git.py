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


def _exec_git(
    *args: str, ignore_errors: Optional[bool] = False, cwd: Optional[str] = None
) -> str:
    """
    Internal module function to abstract calling git via subprocess
    """
    try:
        cmd_args = ["git"]
        cmd_args.extend(args)
        output = subprocess.check_output(cmd_args, cwd=cwd)
        return output.decode()
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            return ""
        raise GitError(e.returncode, e.cmd, e.output, e.stderr) from None


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
    def cwd(self) -> Path:
        """
        Get the current working directory as Path
        """
        return self._cwd

    @cwd.setter
    def cwd(self, cwd: Path):
        """
        Set the current working directory for all following git commands
        """
        self._cwd = cwd.absolute()

    def init(self, *, bare: Optional[bool] = False):
        """
        Init a git repository

        Args:
            bare: Wether to create a `bare` repository or not.
                  Defaults to false.
        """
        args = ["init"]
        if bare:
            args.append("--bare")
        _exec_git(*args, cwd=self._cwd)

    def create_branch(self, branch: str, *, start_point: Optional[str] = None):
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

        _exec_git(*args, cwd=self._cwd)

    def rebase(
        self,
        base: str,
        *,
        head: Optional[str] = None,
        onto: Optional[str] = None,
    ):
        """
        Rebase a branch

        Args:
            base: Apply changes of this branch
            head: Apply changes on this branch. If not set the current branch is
                  used.
            onto: Apply changes on top of this branch
        """
        args = ["rebase"]

        if onto:
            args.extend(["--onto", onto])

        args.append(base)

        if head:
            args.append(head)

        _exec_git(*args, cwd=self._cwd)

    def clone(
        self,
        repo_url: str,
        destination: Path,
        *,
        branch: Optional[str] = None,
        remote: Optional[str] = None,
        depth: Optional[int] = None,
    ):
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
            args.extend(["--depth", depth])
        args.extend([repo_url, str(destination.absolute())])

        _exec_git(
            *args,
            cwd=self._cwd,
        )

    def push(
        self,
        *,
        remote: Optional[str] = None,
        branch: Optional[str] = None,
        follow_tags: bool = False,
    ):
        """
        Push changes to remote repository

        Args:
            remote: Push changes to the named remote
            branch: Branch to push. Will only be considered in combination with
                    a remote.
            follow_tags: Push all tags pointing to a commit included in the to
                         be pushed branch.
        """
        args = ["push"]
        if follow_tags:
            args.append("--follow-tags")
        if remote:
            args.append(remote)
            if branch:
                args.append(branch)

        _exec_git(*args, cwd=self._cwd)

    def config(self, key: str, value: str):
        """
        Set a (local) git config
        """
        _exec_git("config", key, value, cwd=self._cwd)

    def cherry_pick(self, commits: Union[str, List[str]]):
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

        _exec_git(*args, cwd=self._cwd)

    def list_tags(self) -> List[str]:
        """
        List all available tags
        """
        return _exec_git("tag", "-l", cwd=self._cwd).splitlines()

    def add(self, files: Union[str, List[str]]):
        """
        Add files to the git staging area

        Args:
            files: A single file or a list of files to add to the staging area
        """
        if isinstance(files, str):
            files = [files]

        args = ["add"]
        args.extend(files)

        _exec_git(*args, cwd=self._cwd)

    def commit(
        self,
        message: str,
        *,
        verify: Optional[bool] = None,
        gpg_signing_key: Optional[str] = None,
    ):
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

        _exec_git(*args, cwd=self._cwd)
