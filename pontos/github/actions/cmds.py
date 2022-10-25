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
from argparse import Namespace
from typing import List, Tuple

from pontos.terminal import Terminal

from .core import ActionIO


def actions_output(_terminal: Terminal, args: Namespace) -> None:
    """
    Set output variables
    """
    output: List[Tuple[str, str]] = args.output
    for pair in output:
        name, value = pair
        ActionIO.output(name, value)


def actions_input(terminal: Terminal, args: Namespace) -> None:
    names: List[str] = args.input

    inputs = {}
    for name in names:
        inputs[name] = ActionIO.input(name)

    if args.format == "json":
        terminal.out(json.dumps(inputs))
    else:
        for name, value in inputs.items():
            terminal.out(f"{name}={value if value else ''}")
