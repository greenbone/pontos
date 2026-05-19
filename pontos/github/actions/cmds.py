# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import json
from argparse import Namespace

from pontos.terminal import Terminal

from .core import ActionIO


def actions_output(_terminal: Terminal, args: Namespace) -> None:
    """
    Set output variables
    """
    output: list[tuple[str, str]] = args.output
    for pair in output:
        name, value = pair
        ActionIO.output(name, value)


def actions_input(terminal: Terminal, args: Namespace) -> None:
    names: list[str] = args.input

    inputs = {}
    for name in names:
        inputs[name] = ActionIO.input(name)

    if args.format == "json":
        terminal.out(json.dumps(inputs))
    else:
        for name, value in inputs.items():
            terminal.out(f"{name}={value if value else ''}")
