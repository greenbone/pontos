# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import sys
from typing import NoReturn, Optional, Sequence

from pontos.changelog.conventional_commits import ChangelogBuilder
from pontos.errors import PontosError
from pontos.terminal.null import NullTerminal
from pontos.terminal.rich import RichTerminal
from pontos.version.helper import get_last_release_version

from ._parser import parse_args


def main(args: Optional[Sequence[str]] = None) -> NoReturn:
    parsed_args = parse_args(args)

    term = NullTerminal() if parsed_args.quiet else RichTerminal()

    if parsed_args.current_version:
        last_version = parsed_args.current_version
    else:
        last_version = get_last_release_version(
            parsed_args.versioning_scheme.parse_version,
            git_tag_prefix=parsed_args.git_tag_prefix,
        )

    try:
        changelog_builder = ChangelogBuilder(
            config=parsed_args.config,
            repository=parsed_args.repository,
        )
        if parsed_args.output:
            changelog_builder.create_changelog_file(
                parsed_args.output,
                last_version=last_version,
                next_version=parsed_args.next_version,
            )
        else:
            changelog = changelog_builder.create_changelog(
                last_version=last_version,
                next_version=parsed_args.next_version,
            )
            term.out(changelog)
    except KeyboardInterrupt:
        sys.exit(1)
    except PontosError as e:
        term.error(str(e))
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
