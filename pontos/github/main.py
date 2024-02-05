# SPDX-FileCopyrightText: 2021-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
import sys

from pontos.terminal.null import NullTerminal
from pontos.terminal.rich import RichTerminal

from ._parser import parse_args


def main(args=None):
    parsed_args = parse_args(args)

    if parsed_args.quiet:
        term = NullTerminal()
    else:
        term = RichTerminal()

    term.bold_info(f"pontos-github => {parsed_args.func.__name__}")

    with term.indent():
        if not parsed_args.token:
            term.error("A Github User Token is required.")
            sys.exit(1)

        asyncio.run(parsed_args.func(term, parsed_args))


if __name__ == "__main__":
    main()
