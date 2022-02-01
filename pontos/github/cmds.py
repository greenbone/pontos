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

from argparse import Namespace
import sys

import requests

from pontos.github.api import GitHubRESTApi
from pontos.terminal import error, info, ok, out


def pull_request(args: Namespace):
    git = GitHubRESTApi(token=args.token)

    try:
        # check if branches exist
        if not git.branch_exists(repo=args.repo, branch=args.head):
            error(
                f"Head branch {args.head} is not existing "
                "or authorisation failed."
            )
            sys.exit(1)
        ok(f"Head branch {args.head} is existing.")

        if not git.branch_exists(repo=args.repo, branch=args.target):
            error(
                f"Target branch {args.target} is not existing or "
                "authorisation failed."
            )
            sys.exit(1)
        ok(f"Target branch {args.target} is existing.")

        git.create_pull_request(
            repo=args.repo,
            head_branch=args.head,
            base_branch=args.target,
            title=args.title,
            body=args.body,
        )
    except requests.exceptions.RequestException as e:
        error(str(e))
        sys.exit(1)

    ok("Pull Request created.")


def file_status(args: Namespace):
    git = GitHubRESTApi(token=args.token)

    try:
        # check if PR is existing
        if not git.pull_request_exists(
            repo=args.repo, pull_request=args.pull_request
        ):
            error(
                f"PR {args.pull_request} is not existing "
                "or authorisation failed."
            )
            sys.exit(1)
        ok(f"PR {args.pull_request} is existing.")

        file_dict = git.pull_request_files(
            repo=args.repo,
            pull_request=args.pull_request,
            status_list=args.status,
        )
        for status in args.status:
            info(f'{status.value}:')
            files = [str(f.resolve()) for f in file_dict[status]]
            for file_string in files:
                out(file_string)
            if args.output:
                args.output.write("\n".join(files) + "\n")

    except requests.exceptions.RequestException as e:
        error(str(e))
        sys.exit(1)
