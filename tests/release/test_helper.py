# -*- coding: utf-8 -*-
# Copyright (C) 2021 Greenbone Networks GmbH
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

import subprocess
import unittest
import tempfile
import os
from pathlib import Path
import shutil


from pontos.release.helper import get_project_name, find_signing_key


class TestHelperFunctions(unittest.TestCase):
    def setUp(self):
        self.shell_cmd_runner = lambda x: subprocess.run(
            x,
            shell=True,
            check=True,
            errors="utf-8",  # use utf-8 encoding for error output
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.tmpdir = Path(tempfile.gettempdir()) / 'testrepo'
        self.tmpdir.mkdir(parents=True, exist_ok=True)
        self.shell_cmd_runner(f'git -C {self.tmpdir} init')
        self.shell_cmd_runner(
            f'git -C {self.tmpdir} remote add foo https://foo.bar/bla.git'
        )
        self.shell_cmd_runner(
            f'git -C {self.tmpdir} remote add '
            'origin https://foo.bar/testrepo.git'
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir)

    def test_get_project_name(self):
        proj_path = Path.cwd()
        os.chdir(self.tmpdir)
        project = get_project_name(
            shell_cmd_runner=self.shell_cmd_runner, remote='foo'
        )
        self.assertEqual(project, 'bla')

        project = get_project_name(shell_cmd_runner=self.shell_cmd_runner)
        self.assertEqual(project, 'testrepo')
        os.chdir(proj_path)

    def test_find_signing_key(self):
        # save possibly set git signing key temporarly
        saved_key = self.shell_cmd_runner(
            'git config user.signingkey'
        ).stdout.strip()

        self.shell_cmd_runner(
            'git config user.signingkey '
            '1234567890ABCEDEF1234567890ABCEDEF123456'
        )

        signing_key = find_signing_key(shell_cmd_runner=self.shell_cmd_runner)
        self.assertEqual(
            signing_key, '1234567890ABCEDEF1234567890ABCEDEF123456'
        )

        self.shell_cmd_runner('git config user.signingkey ""')
        signing_key = find_signing_key(shell_cmd_runner=self.shell_cmd_runner)
        self.assertEqual(signing_key, '')

        self.shell_cmd_runner(f'git config user.signingkey {saved_key}')
