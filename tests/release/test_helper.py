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

import datetime
import subprocess
import os
import shutil
import sys
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from pontos.terminal import _set_terminal
from pontos.terminal.terminal import Terminal

from pontos.release.helper import (
    calculate_calendar_version,
    get_next_patch_version,
    get_next_dev_version,
    get_project_name,
    find_signing_key,
    update_version,
)
from pontos import version


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
        _set_terminal(Terminal())

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
        # save possibly set git signing key from user temporarly
        try:
            saved_key = self.shell_cmd_runner(
                'git config user.signingkey'
            ).stdout.strip()
        except subprocess.CalledProcessError:
            saved_key = None

        self.shell_cmd_runner(
            'git config user.signingkey '
            '1234567890ABCEDEF1234567890ABCEDEF123456'
        )

        signing_key = find_signing_key(shell_cmd_runner=self.shell_cmd_runner)
        self.assertEqual(
            signing_key, '1234567890ABCEDEF1234567890ABCEDEF123456'
        )

        # reset the previously saved signing key ...
        if saved_key is not None:
            self.shell_cmd_runner(f'git config user.signingkey {saved_key}')

    def test_find_no_signing_key(self):
        # save possibly set git signing key from user temporarly
        try:
            saved_key = self.shell_cmd_runner(
                'git config user.signingkey'
            ).stdout.strip()
        except subprocess.CalledProcessError:
            saved_key = None

        try:
            self.shell_cmd_runner('git config --unset user.signingkey')
        except subprocess.CalledProcessError as e:
            self.assertEqual(e.returncode, 5)

        signing_key = find_signing_key(shell_cmd_runner=self.shell_cmd_runner)
        self.assertEqual(signing_key, '')

        # reset the previously saved signing key ...
        if saved_key is not None:
            self.shell_cmd_runner(f'git config user.signingkey {saved_key}')

    def test_update_version_not_found(self):
        proj_path = Path.cwd()
        os.chdir(self.tmpdir)
        executed, filename = update_version(
            to='21.4.4', _version=version, develop=True
        )
        self.assertFalse(executed)
        self.assertEqual(filename, '')

        os.chdir(proj_path)

    def test_update_version_no_version_file(self):
        proj_path = Path.cwd()
        sys.path.append(self.tmpdir)
        os.chdir(self.tmpdir)

        module_path = self.tmpdir / "testrepo"
        module_path.mkdir(parents=True, exist_ok=True)
        init_file = module_path / "__init__.py"
        init_file.touch()
        version_file = module_path / "__version__.py"
        toml = self.tmpdir / "pyproject.toml"
        toml.write_text(
            '[tool.poetry]\n'
            'name = "testrepo"\n'
            'version = "21.6.2.dev1"\n\n'
            '[tool.pontos.version]\n'
            'version-module-file = "testrepo/__version__.py"\n',
            encoding='utf-8',
        )
        executed, filename = update_version(
            to='21.4.4', _version=version, develop=False
        )
        toml_text = toml.read_text(encoding='utf-8')
        self.assertEqual(filename, 'pyproject.toml')
        self.assertTrue(executed)
        self.assertEqual(
            toml_text,
            '[tool.poetry]\n'
            'name = "testrepo"\n'
            'version = "21.4.4"\n\n'
            '[tool.pontos.version]\n'
            'version-module-file = "testrepo/__version__.py"\n',
        )
        self.assertTrue(version_file.exists())
        version_text = version_file.read_text(encoding='utf-8')
        self.assertEqual(
            version_text,
            '# pylint: disable=invalid-name\n\n'
            '# THIS IS AN AUTOGENERATED FILE. DO NOT TOUCH!\n\n'
            '__version__ = "21.4.4"\n',
        )

        toml.unlink()
        shutil.rmtree(module_path)
        sys.path.remove(self.tmpdir)
        os.chdir(proj_path)


class CalculateHelperVersionTestCase(unittest.TestCase):
    def setUp(self):
        _set_terminal(Terminal())

    def test_calculate_calendar_versions(self):
        today = datetime.datetime.today()

        filenames = ['pyproject.toml', 'CMakeLists.txt']
        mocks = [
            'pontos.release.helper.PythonVersionCommand',
            'pontos.release.helper.CMakeVersionCommand',
        ]
        current_versions = [
            '21.4.1.dev3',
            f'19.{str(today.month)}.1.dev3',
            f'{str(today.year % 100)}.{str(today.month)}.1.dev3',
            f'{str(today.year % 100)}.{str(today.month)}.1',
        ]
        assert_versions = [
            f'{str(today.year % 100)}.{str(today.month)}.0',
            f'{str(today.year % 100)}.{str(today.month)}.0',
            f'{str(today.year % 100)}.{str(today.month)}.1',
            f'{str(today.year % 100)}.{str(today.month)}.2',
        ]

        tmp_path = Path.cwd() / 'tmp'

        for filename, mock in zip(filenames, mocks):
            for current_version, assert_version in zip(
                current_versions, assert_versions
            ):
                tmp_path.mkdir(parents=True, exist_ok=True)
                os.chdir(tmp_path)
                proj_file = Path.cwd() / filename
                proj_file.touch()
                with patch(mock) as cmd_mock:
                    cmd_mock.return_value.get_current_version.return_value = (
                        current_version
                    )

                    release_version = calculate_calendar_version()
                    self.assertEqual(release_version, assert_version)

                os.chdir('..')
                proj_file.unlink()

        tmp_path.rmdir()

    def test_get_next_dev_version(self):
        current_versions = [
            '20.4.1',
            '20.4.1',
            '19.1.2',
            '1.1.1',
            '20.6.1',
        ]
        assert_versions = [
            '20.4.2',
            '20.4.2',
            '19.1.3',
            '1.1.2',
            '20.6.2',
        ]

        for current_version, assert_version in zip(
            current_versions, assert_versions
        ):
            next_version = get_next_dev_version(current_version)

            self.assertEqual(assert_version, next_version)

    def test_get_next_patch_version(self):
        today = datetime.datetime.today()

        filenames = ['pyproject.toml', 'CMakeLists.txt']
        mocks = [
            'pontos.release.helper.PythonVersionCommand',
            'pontos.release.helper.CMakeVersionCommand',
        ]
        current_versions = [
            '20.4.1.dev3',
            f'{str(today.year % 100)}.4.1.dev3',
            f'19.{str(today.month)}.1.dev3',
            f'{str(today.year % 100)}.{str(today.month)}.1',
            '20.6.1',
        ]
        assert_versions = [
            '20.4.1',
            f'{str(today.year % 100)}.4.1',
            f'19.{str(today.month)}.1',
            f'{str(today.year % 100)}.{str(today.month)}.2',
            '20.6.2',
        ]

        tmp_path = Path.cwd() / 'tmp'

        for filename, mock in zip(filenames, mocks):
            for current_version, assert_version in zip(
                current_versions, assert_versions
            ):
                tmp_path.mkdir(parents=True, exist_ok=True)
                os.chdir(tmp_path)
                proj_file = Path.cwd() / filename
                proj_file.touch()
                with patch(mock) as cmd_mock:
                    cmd_mock.return_value.get_current_version.return_value = (
                        current_version
                    )

                    release_version = get_next_patch_version()

                    self.assertEqual(release_version, assert_version)

                os.chdir('..')
                proj_file.unlink()

        tmp_path.rmdir()
