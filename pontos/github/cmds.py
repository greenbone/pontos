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

import sys
from argparse import Namespace
from pathlib import Path

import httpx

from pontos.github.api import GitHubAsyncRESTApi
from pontos.terminal import Terminal


async def tag(terminal: Terminal, args: Namespace) -> None:
    """Github release function for argument class to call"""
    await args.tag_func(terminal, args)


async def create_tag(terminal: Terminal, args: Namespace) -> None:
    """Github create tag function for
    argument class to call"""
    async with GitHubAsyncRESTApi(token=args.token) as api:
        try:
            # Create tag
            new_tag = await api.tags.create(
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
            await api.tags.create_tag_reference(
                repo=args.repo, tag=args.tag, sha=new_tag.sha
            )

        except httpx.HTTPError as e:
            terminal.error(str(e))
            sys.exit(1)

        terminal.ok("Tag created.")


async def release(terminal: Terminal, args: Namespace) -> None:
    """Github release function for argument class to call"""
    await args.re_func(terminal, args)


async def create_release(terminal: Terminal, args: Namespace) -> None:
    """Github create release function for
    argument class to call"""

    async with GitHubAsyncRESTApi(token=args.token) as api:
        try:
            # Check if release exist
            exists = await api.releases.exists(repo=args.repo, tag=args.tag)
            if exists:
                terminal.error(f"Release {args.tag} exist.")
                sys.exit(1)

            # Create release
            await api.releases.create(
                repo=args.repo,
                tag=args.tag,
                body=args.body,
                name=args.name,
                target_commitish=args.target_commitish,
                draft=args.draft,
                prerelease=args.prerelease,
            )

            terminal.ok("Release created.")
        except httpx.HTTPError as e:
            terminal.error(str(e))
            sys.exit(1)


async def pull_request(terminal: Terminal, args: Namespace):
    await args.pr_func(terminal, args)


async def create_pull_request(terminal: Terminal, args: Namespace):
    async with GitHubAsyncRESTApi(token=args.token) as api:
        try:
            # check if branches exist
            exists = await api.branches.exists(repo=args.repo, branch=args.head)
            if not exists:
                terminal.error(
                    f"Head branch {args.head} is not existing "
                    "or authorisation failed."
                )
                sys.exit(1)

            terminal.ok(f"Head branch {args.head} is existing.")

            exists = await api.branches.exists(
                repo=args.repo, branch=args.target
            )
            if not exists:
                terminal.error(
                    f"Target branch {args.target} is not existing or "
                    "authorisation failed."
                )
                sys.exit(1)

            terminal.ok(f"Target branch {args.target} exists.")

            await api.pulls.create(
                repo=args.repo,
                head_branch=args.head,
                base_branch=args.target,
                title=args.title,
                body=args.body,
            )

            terminal.ok("Pull Request created.")
        except httpx.HTTPError as e:
            terminal.error(str(e))
            sys.exit(1)


async def update_pull_request(terminal: Terminal, args: Namespace):
    async with GitHubAsyncRESTApi(token=args.token) as api:
        try:
            if args.target:
                # check if branches exist
                exists = await api.branches.exists(
                    repo=args.repo, branch=args.target
                )
                if not exists:
                    terminal.error(
                        f"Target branch {args.target} is not existing or "
                        "authorisation failed."
                    )
                    sys.exit(1)

                terminal.ok(f"Target branch {args.target} exists.")

            await api.pulls.update(
                repo=args.repo,
                pull_request=args.pull_request,
                base_branch=args.target,
                title=args.title,
                body=args.body,
            )

            terminal.ok("Pull Request updated.")
        except httpx.HTTPError as e:
            terminal.error(str(e))
            sys.exit(1)


async def file_status(terminal: Terminal, args: Namespace):
    async with GitHubAsyncRESTApi(token=args.token) as api:
        try:
            # check if PR is existing
            exists = await api.pulls.exists(
                repo=args.repo, pull_request=args.pull_request
            )
            if not exists:
                terminal.error(
                    f"PR {args.pull_request} is not existing "
                    "or authorisation failed."
                )
                sys.exit(1)

            terminal.ok(f"PR {args.pull_request} exists.")

            file_dict = await api.pulls.files(
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


async def labels(terminal: Terminal, args: Namespace):
    async with GitHubAsyncRESTApi(token=args.token) as api:
        try:
            # check if PR is existing
            exists = await api.pulls.exists(
                repo=args.repo, pull_request=args.issue
            )
            if not exists:
                terminal.error(
                    f"PR {args.issue} is not existing or authorisation failed."
                )
                sys.exit(1)

            terminal.ok(f"PR {args.issue} exists.")

            issue_labels = []
            async for label in api.labels.get_all(
                repo=args.repo,
                issue=args.issue,
            ):
                issue_labels.append(label)

            issue_labels.extend(args.labels)

            await api.labels.set_all(
                repo=args.repo, issue=args.issue, labels=issue_labels
            )
        except httpx.HTTPError as e:
            terminal.error(str(e))
            sys.exit(1)


async def repos(terminal: Terminal, args: Namespace):
    async with GitHubAsyncRESTApi(token=args.token) as api:
        try:
            # check if Orga is existing
            exists = await api.organizations.exists(args.orga)
            if not exists:
                terminal.error(
                    f"PR {args.orga} is not existing or authorisation failed."
                )
                sys.exit(1)

            terminal.ok(f"Organization {args.orga} exists.")

            if args.path:
                repo_info = Path(args.path)
                with repo_info.open(encoding="utf-8", mode="w") as fp:
                    async for repo in api.organizations.get_repositories(
                        organization=args.orga, repository_type=args.type
                    ):
                        fp.write(repr(repo))

            else:
                async for repo in api.organizations.get_repositories(
                    organization=args.orga, repository_type=args.type
                ):
                    terminal.print(repo)

        except httpx.HTTPError as e:
            terminal.error(str(e))
            sys.exit(1)
