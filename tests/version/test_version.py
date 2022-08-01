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

import contextlib
import io
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from pontos.version.helper import VersionError
from pontos.version.version import VersionCommand


class VersionCommandTestCase(unittest.TestCase):
    def test_missing_cmd(self):
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            VersionCommand().run()
            self.assertEqual(
                buf.getvalue(),
                "usage: version [-h] [--quiet] {verify,show,update} ...\n",
            )

    def test_missing_file(self):
        with self.assertRaises(
            VersionError, msg="Could not find whatever file."
        ):
            VersionCommand(project_file_path=Path("whatever")).run(
                args=["show"]
            )

    def test_print_current_version(self):
        print_mock = MagicMock()
        VersionCommand.get_current_version = MagicMock(return_value="1.2.3")
        VersionCommand._print = print_mock  # pylint: disable=protected-access

        cmd = VersionCommand()
        cmd.print_current_version()

        print_mock.assert_called_with("1.2.3")
