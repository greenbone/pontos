# Copyright (C) 2022 Greenbone AG
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
from typing import (
    Collection,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Union,
)

from pontos.errors import PontosError
from pontos.git.status import StatusEntry, parse_git_status

DEFAULT_TAG_SORT_SUFFIX = [
    "-alpha",
    "a",
    "-beta",
    "b",
    "-rc",
    "rc",
]


class GitError(subprocess.CalledProcessError, PontosError):
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
        output = subprocess.run(
            cmd_args,
            cwd=fspath(cwd) if cwd else None,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
            errors="replace",
        )
        return output.stdout
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            return ""
        raise GitError(e.returncode, e.cmd, e.output, e.stderr) from None


class MergeStrategy(Enum):
    """
    Possible strategies for a merge

    Attributes:
        ORT:
        ORT_OURS:
        RECURSIVE:
        OCTOPUS:
        OURS:
        SUBTREE:
    """

    ORT = "ort"
    ORT_OURS = "ort-ours"
    RECURSIVE = "recursive"
    RESOLVE = "resolve"
    OCTOPUS = "octopus"
    OURS = "ours"
    SUBTREE = "subtree"


class ConfigScope(Enum):
    """
    Possible scopes for git settings

    Attributes:
        GLOBAL: Apply setting user wide (~/.gitconfig)
        LOCAL: Apply setting to the local repository only (.git/config)
        SYSTEM: Apply settings system wide (/etc/gitconfig)
        WORKTREE: Similar to LOCAL except that $GIT_DIR/config.worktree is used
            if extensions.worktreeConfig is enabled. If not it's the same as
            LOCAL.
    """

    GLOBAL = "global"
    LOCAL = "local"
    SYSTEM = "system"
    WORKTREE = "worktree"


class TagSort(Enum):
    """
    Sorting for git tags

    Attributes:
        VERSION: Sort tags by version number
    """

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

    @property
    def version(self) -> str:
        """
        Get the version string of the installed git
        """
        # git --version returns "git version 2.3.4"
        return self.exec("--version").strip().rsplit(" ", 1)[1]

    def exec(self, *args: str) -> str:
        return exec_git(*args, cwd=self._cwd)

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

        self.exec(*args)

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

        self.exec(*args)

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

        self.exec(*args)

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

        self.exec(*args)

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

        self.exec(*args)

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

        return self.exec(*args)

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

        self.exec(*args)

    def list_tags(
        self,
        *,
        sort: Optional[TagSort] = None,
        tag_name: Optional[str] = None,
        sort_suffix: Optional[List[str]] = None,
    ) -> List[str]:
        """
        List all available tags

        Args:
            sort: Apply a specific sort algorithm for the git tags. By default
                git uses a lexicographic sorting.
            tag_name: Filter list by the tagname pattern. For example: "22.4*"
            sort_suffix: A list of version suffix to consider.
        """

        if sort:
            args = []

            if sort_suffix:
                for suffix in sort_suffix:
                    args.extend(["-c", f"versionsort.suffix={suffix}"])

            args.extend(["tag", "-l"])
            args.append(f"--sort={sort.value}")
        else:
            args = ["tag", "-l"]

        if tag_name:
            args.append(tag_name)

        return self.exec(*args).splitlines()

    def add(
        self,
        files: Union[str, PathLike[str], Sequence[Union[PathLike[str], str]]],
    ) -> None:
        """
        Add files to the git staging area

        Args:
            files: A single file or a list of files to add to the staging area
        """
        if isinstance(files, (PathLike, str)):
            files = [files]

        args = ["add"]
        args.extend([fspath(file) for file in files])

        self.exec(*args)

    def commit(
        self,
        message: str,
        *,
        verify: Optional[bool] = None,
        gpg_sign: Optional[bool] = None,
        gpg_signing_key: Optional[str] = None,
    ) -> None:
        """
        Create a new commit

        Args:
            message: Message of the commit
            verify: Set to False to skip git hooks
            gpg_sign: Set to False to skip signing the commit via GPG
            gpg_signing_key: GPG Key ID to use to sign the commit
        """
        args = ["commit"]
        if verify is False:
            args.append("--no-verify")
        if gpg_signing_key:
            args.append(f"-S{gpg_signing_key}")
        if gpg_sign is False:
            args.append("--no-gpg-sign")

        args.extend(["-m", message])

        self.exec(*args)

    def tag(
        self,
        tag: str,
        *,
        gpg_key_id: Optional[str] = None,
        message: Optional[str] = None,
        force: Optional[bool] = False,
        sign: Optional[bool] = None,
    ) -> None:
        """
        Create a Tag

        Args:
            tag: Tag name to create.
            gpg_key_id: GPG Key to sign the tag.
            message: Use message to annotate the given tag.
            force: True to replace an existing tag.
            sign: Set to False to deactivate signing of the tag.
        """
        args = ["tag"]

        if gpg_key_id:
            args.extend(["-u", gpg_key_id])

        if message:
            args.extend(["-m", message])

        if force:
            args.append("--force")

        if sign is False:
            args.append("--no-sign")

        args.append(tag)

        self.exec(*args)

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

        self.exec(*args)

    def add_remote(self, remote: str, url: str) -> None:
        """
        Add a new git remote

        Args:
            remote: Name of the new remote
            url: Git URL of the remote repository
        """

        args = ["remote", "add", remote, url]

        self.exec(*args)

    def remote_url(self, remote: str = "origin") -> str:
        """
        Get the url of a remote

        Args:
            remote: Name of the remote. Default: origin.
        """
        args = ["remote", "get-url", remote]
        return self.exec(*args)

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

        self.exec(*args)

    def log(
        self,
        *log_args: str,
        oneline: Optional[bool] = None,
        format: Optional[str] = None,
    ) -> List[str]:
        """
        Get log of a git repository

        Args:
            format: Pretty format the output.
            log_args: Additional arguments for git log
            oneline: Print the abbreviated commit id and commit message in one
                line per commit
        """
        args = ["log"]

        if format:
            args.append(f"--format={format}")

        if oneline:
            args.append("--oneline")

        args.extend(log_args)

        return self.exec(*args).splitlines()

    def show(
        self,
        *show_args: str,
        format: Optional[str] = None,
        oneline: Optional[bool] = None,
        patch: Optional[bool] = None,
        objects: Union[str, Collection[str], None] = None,
    ) -> Union[str, list[str]]:
        """
        Show various types of git objects

        Args:
            format: Pretty format the output.
            oneline: Print the abbreviated commit id and commit message in one
                line per commit.
            patch: True to generate patch output. False to suppress diff output.
            show_args: Additional arguments for git show
            objects: Git objects (commits, refs, ...) to get details for.

        Returns:
            A list of details about the passed object the object if more then
            one object is passed. Otherwise a single details is returned.
        """
        args = ["show"]

        if format:
            args.append(f"--format={format}")

        if oneline:
            args.append("--oneline")

        if patch is not None:
            if patch:
                args.append("--patch")
            else:
                args.append("--no-patch")

        if objects:
            if isinstance(objects, str):
                objects = [objects]

            args.extend(objects)

        args.extend(show_args)

        output = self.exec(*args).strip()

        return output.splitlines() if objects and len(objects) > 1 else output

    def rev_list(
        self,
        *commit: str,
        max_parents: Optional[int] = None,
        abbrev_commit: Optional[bool] = False,
    ) -> List[str]:
        """
        Lists commit objects in reverse chronological order

        Args:
            commit: commit objects.
            max_parents: Only list nth oldest commits
            abbrev_commit: Set to True to show  prefix that names the commit
                object uniquely instead of the full commit ID.

        Examples:
            This will "list all the commits which are reachable from foo or
            bar, but not from baz".

            .. code-block:: python

                from pontos.git import Git

                git = Git()
                git.rev_list("foo", "bar", "^baz")

            This will return the first commit of foo.

            .. code-block:: python

                from pontos.git import Git

                git = Git()
                git.rev_list("foo", max_parents=0)

        """
        args = ["rev-list"]
        if max_parents is not None:
            args.append(f"--max-parents={max_parents}")
        if abbrev_commit:
            args.append("--abbrev-commit")

        args.extend(commit)
        return self.exec(*args).splitlines()

    def move(self, old: PathLike, new: PathLike) -> None:
        """
        Move a file from old to new
        """
        self.exec("mv", fspath(old), fspath(new))

    def remove(self, to_remove: PathLike) -> None:
        """
        Remove a file from git
        """
        self.exec("rm", fspath(to_remove))

    def status(
        self,
        files: Optional[Iterable[PathLike]] = None,
    ) -> Iterator[StatusEntry]:
        """Get information about the current git status.

        Args:
            files: specify an iterable of :py:class:`os.PathLike` and
                exclude all other paths for the status.

        Returns:
            An iterator of :py:class:`StatusEntry` instances that contain the
            status of the specific files.
        """
        args = [
            "status",
            "-z",
            "--ignore-submodules",
            "--untracked-files=no",
        ]

        if files:
            args.append("--")
            args.extend([fspath(f) for f in files])

        output = self.exec(*args)
        return parse_git_status(output)
