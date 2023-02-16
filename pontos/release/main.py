# -*- coding: utf-8 -*-
# pontos/release/release.py
# Copyright (C) 2020-2022 Greenbone Networks GmbH
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
#

import subprocess
import sys
from typing import NoReturn

from pontos.release.parser import parse_args
from pontos.terminal.null import NullTerminal
from pontos.terminal.rich import RichTerminal


def main(
    args=None,
) -> NoReturn:
    username, token, parsed_args = parse_args(args)
    if parsed_args.quiet:
        term = NullTerminal()
    else:
        term = RichTerminal()

    term.bold_info(f"pontos-release => {parsed_args.func.__name__}")

    with term.indent():
        try:
            retval = parsed_args.func(
                term,
                parsed_args,
                username=username,
                token=token,
            )
            sys.exit(int(retval))
        except KeyboardInterrupt:
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            if not "--passphrase" in e.cmd:
                term.error(f'Could not run command "{e.cmd}".')
            else:
                term.error("Headless signing failed.")

            term.print(f"Error was: {e.stderr}")
            sys.exit(1)


if __name__ == "__main__":
    main()
