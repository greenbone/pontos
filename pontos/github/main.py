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

import sys
from pontos.github.argparser import parse_args
from pontos.terminal import Terminal, _set_terminal


def main(args=None):
    parsed_args = parse_args(args)

    term = Terminal()
    _set_terminal(term)

    term.bold_info(f'pontos-github => {parsed_args.func.__name__}')

    with term.indent():
        if not parsed_args.token:
            term.error("A Github User Token is required.")
            sys.exit(1)

        parsed_args.func(args=parsed_args)


if __name__ == "__main__":
    main()
