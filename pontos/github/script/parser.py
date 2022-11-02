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

import os
from argparse import ArgumentParser

from pontos.github.api.helper import DEFAULT_TIMEOUT

GITHUB_TOKEN = "GITHUB_TOKEN"


def create_parser() -> ArgumentParser:
    """
    Create a CLI parser for running Pontos GitHub Scripts

    Returns:
        A new ArgumentParser instance add the default arguments
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "--token",
        default=os.environ.get(GITHUB_TOKEN),
        help="GitHub Token. Defaults to GITHUB_TOKEN environment variable.",
    )
    parser.add_argument(
        "--timeout",
        default=DEFAULT_TIMEOUT,
        help="Timeout in seconds. Default: %(default)s.",
        type=float,
    )
    parser.add_argument("script", help="Script to run")
    return parser
