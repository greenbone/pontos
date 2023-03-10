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
"""
Load and run Pontos GitHub Scripts

A Pontos GitHub Script is a Python module that has a github_script coroutine
function and optionally a add_script_arguments function. These functions should
have the following signatures:

.. code-block:: python

    async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:

    def add_script_arguments(parser: ArgumentParser) -> None:

Example:

.. code-block:: python
    :caption: Example Python module containing a Pontos GitHub Script

    def add_script_arguments(parser: ArgumentParser) -> None:
        parser.add_argument("repository")

    async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
        repo = await api.repositories.get(args.repository)
        print(repo.html_url, repo.description)
        return 0
"""

import json
import sys
from argparse import ArgumentParser

import httpx

from pontos.errors import PontosError

from .errors import GitHubScriptError
from .load import (
    load_script,
    run_add_arguments_function,
    run_github_script_function,
)
from .parser import create_parser

__all__ = (
    "GitHubScriptError",
    "load_script",
    "run_add_arguments_function",
    "run_github_script_function",
)


def main():
    """
    CLI function to run a Pontos GitHub Script
    """
    parser = create_parser()
    known_args, _ = parser.parse_known_args()
    try:
        with load_script(known_args.script) as module:
            # using a child parser allows for adding --help including the script
            # arguments
            child_parser = ArgumentParser(parents=[parser])
            run_add_arguments_function(module, child_parser)
            args = child_parser.parse_args()
            token = args.token
            timeout = args.timeout

            retval = run_github_script_function(module, token, timeout, args)

        sys.exit(retval)
    except KeyboardInterrupt:
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        try:
            error = e.response.json()
            message = error.get("message")
            print("Error:", message, file=sys.stderr)
        except json.JSONDecodeError:
            # not a json response
            print(e, file=sys.stderr)
        except httpx.ResponseNotRead:
            # a streaming response failed
            print(e, file=sys.stderr)

        sys.exit(1)
    except PontosError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
