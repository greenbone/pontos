# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Greenbone Networks GmbH
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

from pontos.terminal.terminal import ConsoleTerminal


def main() -> None:
    term = ConsoleTerminal()

    term.print()
    term.bold_info("pontos - Greenbone Python Utilities and Tools")
    term.print()
    term.print("The following commands are currently available:")
    with term.indent():
        term.bold_info(
            "pontos-release - Release handling "
            "utility for C and Python Projects"
        )
        term.print("usage:")
        with term.indent():
            term.print("pontos-release {prepare,release,sign} -h")
        term.bold_info(
            "pontos-version - Version handling utility "
            "for C, Go and Python Projects"
        )
        term.print("usage:")
        with term.indent():
            term.print("pontos-version {verify,show,update} -h")
        term.bold_info(
            "pontos-update-header - Handling Copyright header "
            "for various file types and licenses"
        )
        term.print("usage:")
        with term.indent():
            term.print("pontos-update-header -h")
        term.bold_info(
            "pontos-changelog - Parse conventional commits in the "
            "current branch, creating CHANGELOG.md file"
        )
        term.print("usage:")
        with term.indent():
            term.print("pontos-changelog -h")
        term.bold_info(
            "pontos-github - Handling GitHub operations, like "
            "Pull Requests (beta)"
        )
        term.print("usage:")
        with term.indent():
            term.print("pontos-github {pr} -h")

        term.bold_info(
            "pontos-github-script - CLI for running scripts on the GitHub API"
        )
        term.print("usage:")
        with term.indent():
            term.print("pontos-github-script {script} -h")
        term.print()

        term.bold_info("pontos-github-actions - GitHub Actions API CLI")
        term.print("usage:")
        with term.indent():
            term.print("pontos-github-actions -h")
        term.print()

        term.info(
            "pontos also comes with a Terminal interface "
            "printing prettier outputs"
        )
        with term.indent():
            term.print('Accessible with import "pontos.terminal"')
        term.info("pontos also comes with git and GitHub APIs")
        with term.indent():
            term.print(
                'Accessible with "import pontos.git" '
                'and "import pontos.github"'
            )

    term.print()
    term.warning(
        'Use the listed commands "help" for more information '
        "and arguments description."
    )


if __name__ == "__main__":
    main()
