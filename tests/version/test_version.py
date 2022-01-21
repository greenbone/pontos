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

import unittest
import contextlib
import io

from pathlib import Path
from pontos.version.version import VersionCommand
from pontos.version.helper import VersionError

# pylint: disable=W0212


class VersionCommandTestCase(unittest.TestCase):
    def test_missing_cmd(self):
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            VersionCommand().run()
            self.assertEqual(
                buf.getvalue(),
                'usage: version [-h] [--quiet] {verify,show,update} ...\n',
            )

    def test_missing_file(self):
        with self.assertRaises(
            VersionError, msg="Could not find whatever file."
        ):
            VersionCommand(project_file_path=Path('whatever')).run(
                args=['show']
            )
