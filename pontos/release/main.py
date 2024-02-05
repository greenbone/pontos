# pontos/release/release.py
# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import subprocess
import sys
from typing import NoReturn

from pontos.git import GitError
from pontos.terminal.null import NullTerminal
from pontos.terminal.rich import RichTerminal

from ._parser import parse_args


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
