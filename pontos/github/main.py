# Copyright (C) 2021 Greenbone Networks GmbH
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

from pontos.github.argparser import parse_args
from pontos.github.api import GitHubRESTApi


def main(args=None):
    parsed_args = parse_args(args)
    print(parsed_args)

    git = GitHubRESTApi(token=parsed_args.token)

    git.create_pull_request(
        repo=parsed_args.repo,
        head_branch=parsed_args.head,
        base_branch=parsed_args.target,
        title=parsed_args.title,
        body=parsed_args.body,
    )


if __name__ == "__main__":
    main()
