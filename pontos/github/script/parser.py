# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import os
from argparse import ArgumentParser

import shtab

from pontos.github.api.helper import DEFAULT_TIMEOUT

GITHUB_TOKEN = "GITHUB_TOKEN"


def create_parser() -> ArgumentParser:
    """
    Create a CLI parser for running Pontos GitHub Scripts

    Returns:
        A new ArgumentParser instance add the default arguments
    """
    parser = ArgumentParser(add_help=False)
    shtab.add_argument_to(parser)
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
