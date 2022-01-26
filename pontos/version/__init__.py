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

import sys
from pathlib import Path
from .__version__ import __version__

from .python import PythonVersionCommand
from .cmake import CMakeVersionCommand
from .go import GoVersionCommand


def main(leave=True, args=None):
    available_cmds = [
        ('CMakeLists.txt', CMakeVersionCommand),
        ('pyproject.toml', PythonVersionCommand),
        ('go.mod', GoVersionCommand),
    ]
    for file_name, cmd in available_cmds:
        project_definition_path = Path.cwd() / file_name
        if project_definition_path.exists():
            result = cmd().run(args)
            if leave:
                sys.exit(result)
            return result == 0, file_name
    if leave:
        sys.exit("No command found")
    return False, ""
