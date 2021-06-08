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

import datetime
import os
import unittest
from unittest.mock import patch
from pathlib import Path


from pontos.version import (
    calculate_calendar_version,
)


class CalculateNextVersionTestCase(unittest.TestCase):
    def test_calculate_calendar_versions(self):
        today = datetime.datetime.today()

        filenames = ['pyproject.toml', 'CMakeLists.txt']
        mocks = [
            'pontos.version.helper.PontosVersionCommand',
            'pontos.version.helper.CMakeVersionCommand',
        ]
        current_versions = [
            '20.4.1.dev3',
            f'{str(today.year % 100)}.4.1.dev3',
            f'19.{str(today.month)}.1.dev3',
            f'{str(today.year % 100)}.{str(today.month)}.1.dev3',
            f'{str(today.year % 100)}.{str(today.month)}.1',
        ]
        assert_versions = [
            f'{str(today.year % 100)}.{str(today.month)}.0',
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
