# Copyright (C) 2020 Greenbone Networks GmbH
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

# pylint: disable=invalid-name

import sys

from pathlib import Path
from .version import PontosVersionCommand
from .cmake_version import CMakeVersionCommand


def main():
    available_cmds = [
        ('CMakeLists.txt', CMakeVersionCommand),
        ('pyproject.toml', PontosVersionCommand),
    ]
    for fileName, cmd in available_cmds:
        project_definition_path = Path.cwd() / fileName
        if project_definition_path.exists():
            sys.exit(cmd().run())
    sys.exit("No command found")


if __name__ == '__main__':
    main()
