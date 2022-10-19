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

import json
import sys
from argparse import Namespace
from pathlib import Path

import httpx

from pontos.github.api import GitHubRESTApi
from pontos.terminal import Terminal


def tag(terminal: Terminal, args: Namespace) -> None:
    """Github release function for argument class to call"""

    args.tag_func(terminal, args)


def create_tag(terminal: Terminal, args: Namespace) -> None:
    """Github create tag function for
    argument class to call"""

    git = GitHubRESTApi(token=args.token)

    try:
        # Create tag
        sha = git.create_tag(
            repo=args.repo,
            tag=args.tag,
            message=args.message,
            git_object=args.git_object,
            name=args.name,
            email=args.email,
            git_object_type=args.git_object_type,
            date=args.date,
        )

        # Create tag reference
        git.create_tag_reference(repo=args.repo, tag=args.tag, sha=sha)

    except httpx.HTTPError as e:
        terminal.error(str(e))
        sys.exit(1)

    terminal.ok("Tag created.")


def release(terminal: Terminal, args: Namespace) -> None:
    """Github release function for argument class to call"""

    args.re_func(terminal, args)


def create_release(terminal: Terminal, args: Namespace) -> None:
    """Github create release function for
    argument class to call"""

    git = GitHubRESTApi(token=args.token)

    try:
        # Check if release exist
        if git.release_exists(repo=args.repo, tag=args.tag):
            terminal.error(f"Release {args.tag} exist.")
            sys.exit(1)

        # Create release
        git.create_release(
            repo=args.repo,
            tag=args.tag,
            body=args.body,
            name=args.name,
            target_commitish=args.target_commitish,
            draft=args.draft,
            prerelease=args.prerelease,
        )
    except httpx.HTTPError as e:
        terminal.error(str(e))
        sys.exit(1)

    terminal.ok("Release created.")


def pull_request(terminal: Terminal, args: Namespace):
    args.pr_func(terminal, args)


def create_pull_request(terminal: Terminal, args: Namespace):
    git = GitHubRESTApi(token=args.token)

    try:
        # check if branches exist
        if not git.branch_exists(repo=args.repo, branch=args.head):
            terminal.error(
                f"Head branch {args.head} is not existing "
                "or authorisation failed."
            )
            sys.exit(1)

        terminal.ok(f"Head branch {args.head} is existing.")

        if not git.branch_exists(repo=args.repo, branch=args.target):
            terminal.error(
                f"Target branch {args.target} is not existing or "
                "authorisation failed."
            )
            sys.exit(1)

        terminal.ok(f"Target branch {args.target} exists.")

        git.create_pull_request(
            repo=args.repo,
            head_branch=args.head,
            base_branch=args.target,
            title=args.title,
            body=args.body,
        )
    except httpx.HTTPError as e:
        terminal.error(str(e))
        sys.exit(1)

    terminal.ok("Pull Request created.")


def update_pull_request(terminal: Terminal, args: Namespace):
    git = GitHubRESTApi(token=args.token)

    try:
        if args.target:
            # check if branches exist
            if not git.branch_exists(repo=args.repo, branch=args.target):
                terminal.error(
                    f"Target branch {args.target} is not existing or "
                    "authorisation failed."
                )
                sys.exit(1)

            terminal.ok(f"Target branch {args.target} exists.")
        git.update_pull_request(
            repo=args.repo,
            pull_request=args.pull_request,
            base_branch=args.target,
            title=args.title,
            body=args.body,
        )
    except httpx.HTTPError as e:
        terminal.error(str(e))
        sys.exit(1)

    terminal.ok("Pull Request updated.")


def file_status(terminal: Terminal, args: Namespace):
    git = GitHubRESTApi(token=args.token)

    try:
        # check if PR is existing
        if not git.pull_request_exists(
            repo=args.repo, pull_request=args.pull_request
        ):
            terminal.error(
                f"PR {args.pull_request} is not existing "
                "or authorisation failed."
            )
            sys.exit(1)
        terminal.ok(f"PR {args.pull_request} exists.")

        file_dict = git.pull_request_files(
            repo=args.repo,
            pull_request=args.pull_request,
            status_list=args.status,
        )
        for status in args.status:
            terminal.info(f"{status.value}:")
            files = [str(f.resolve()) for f in file_dict[status]]

            for file_string in files:
                terminal.print(file_string)

            if args.output:
                args.output.write("\n".join(files) + "\n")

    except httpx.HTTPError as e:
        terminal.error(str(e))
        sys.exit(1)


def labels(terminal: Terminal, args: Namespace):
    git = GitHubRESTApi(token=args.token)

    try:
        # check if PR is existing
        if not git.pull_request_exists(repo=args.repo, pull_request=args.issue):
            terminal.error(
                f"PR {args.issue} is not existing or authorisation failed."
            )
            sys.exit(1)

        terminal.ok(f"PR {args.issue} exists.")

        issue_labels = git.get_labels(
            repo=args.repo,
            issue=args.issue,
        )

        issue_labels.extend(args.labels)

        git.set_labels(repo=args.repo, issue=args.issue, labels=issue_labels)

    except httpx.HTTPError as e:
        terminal.error(str(e))
        sys.exit(1)


def repos(terminal: Terminal, args: Namespace):
    git = GitHubRESTApi(token=args.token)

    try:
        # check if Orga is existing
        if not git.organisation_exists(orga=args.orga):
            terminal.error(
                f"PR {args.orga} is not existing or authorisation failed."
            )
            sys.exit(1)
        terminal.ok(f"Organization {args.orga} exists.")
        orga_json = git.get_repositories(
            orga=args.orga, repository_type=args.type
        )
        if args.path:
            repo_info = Path(args.path)
            with open(repo_info, encoding="utf-8", mode="w") as fp:
                json.dump(orga_json, fp, indent=2)
        else:
            terminal.print(orga_json)

    except httpx.HTTPError as e:
        terminal.error(str(e))
        sys.exit(1)
