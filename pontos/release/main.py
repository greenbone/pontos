# -*- coding: utf-8 -*-
# pontos/release/release.py
# Copyright (C) 2020-2022 Greenbone AG
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

import logging
import subprocess
import sys
from typing import NoReturn

from pontos.git import GitError
from pontos.release.parser import parse_args
from pontos.terminal.null import NullTerminal
from pontos.terminal.rich import RichTerminal


def main(
    args=None,
) -> NoReturn:
    username, token, parsed_args = parse_args(args)
    logging.basicConfig(format="%(levelname)s - %(name)s - %(message)s")

    if parsed_args.quiet:
        term = NullTerminal()
        error_terminal = NullTerminal()
        logging.disable()
    else:
        term = RichTerminal()  # type: ignore[assignment]
        error_terminal = RichTerminal(file=sys.stderr)  # type: ignore[assignment] # noqa: E501

    try:
        retval = parsed_args.func(
            parsed_args,
            terminal=term,
            error_terminal=error_terminal,
            username=username,
            token=token,
        )
        sys.exit(int(retval))
    except KeyboardInterrupt:
        sys.exit(1)
    except GitError as e:
        error_terminal.error(f'Could not run git command "{e.cmd}".')
        error = e.stderr if e.stderr else e.stdout
        error_terminal.print(f"Output was: {error}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        if "--passphrase" not in e.cmd:
            error_terminal.error(f'Could not run command "{e.cmd}".')
        else:
            error_terminal.error("Headless signing failed.")

        error_terminal.print(f"Error was: {e.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    main()
