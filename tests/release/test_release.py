# -*- coding: utf-8 -*-
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
# pylint: disable=C0413,W0108

import shutil
import unittest
import datetime

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

from pontos import version, release, changelog
from pontos.release.release import (
    calculate_calendar_version,
    find_release_version_in_changelog,
)


@dataclass
class StdOutput:
    stdout: bytes


_shutil_mock = MagicMock(spec=shutil)


@patch("pontos.release.release.shutil", new=_shutil_mock)
class PrepareTestCase(unittest.TestCase):
    def test_prepare_successfully(self):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'prepare',
            '--release-version',
            '0.0.1',
            '--next-version',
            '0.0.2dev',
        ]
        runner = lambda x: StdOutput('')
        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertTrue(released)

    def test_prepare_calendar_successfully(self):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'prepare',
            '--calendar',
        ]
        runner = lambda x: StdOutput('')
        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertTrue(released)

    def test_use_git_signing_key_on_prepare(self):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'prepare',
            '--git-signing-key',
            '0815',
            '--release-version',
            '0.0.1',
            '--next-version',
            '0.0.2dev',
        ]
        called = []

        def runner(cmd):
            called.append(cmd)
            return StdOutput('')

        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertTrue(released)
        self.assertIn(
            "git commit -S0815 -m 'automatic release to 0.0.1'", called
        )
        self.assertIn(
            "git tag -u 0815 v0.0.1 -m 'automatic release to 0.0.1'", called
        )

    def test_fail_if_tag_is_already_taken(self):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_changelog = MagicMock(spec=changelog)
        args = [
            '--project',
            'testcases',
            'prepare',
            '--release-version',
            '0.0.1',
            '--next-version',
            '0.0.2dev',
        ]
        runner = lambda x: StdOutput('v0.0.1'.encode())
        with self.assertRaises(
            ValueError, msg='git tag v0.0.1 is already taken'
        ):
            release.main(
                shell_cmd_runner=runner,
                _path=fake_path_class,
                _version=fake_version,
                _changelog=fake_changelog,
                leave=False,
                args=args,
            )

    @patch('pontos.release.release.redirect_stdout')
    def test_calculate_calendar_version_old(self, stdout_mock):
        # thats the ugliest mock  I have created. Ever.
        getvalue_mock = stdout_mock.return_value.__enter__.return_value.getvalue
        getvalue_mock.return_value = '20.4.1.dev3'
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')

        release_version, next_version = calculate_calendar_version(fake_version)

        today = datetime.datetime.today()
        self.assertEqual(
            release_version, f'{str(today.year % 100)}.{str(today.month)}.0'
        )
        self.assertEqual(
            next_version, f'{str(today.year % 100)}.{str(today.month)}.1.dev1'
        )

    @patch('pontos.release.release.redirect_stdout')
    def test_calculate_calendar_version_old_month(self, stdout_mock):
        today = datetime.datetime.today()
        getvalue_mock = stdout_mock.return_value.__enter__.return_value.getvalue
        getvalue_mock.return_value = f'{str(today.year % 100)}.4.1.dev3'
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')

        release_version, next_version = calculate_calendar_version(fake_version)

        self.assertEqual(
            release_version, f'{str(today.year % 100)}.{str(today.month)}.0'
        )
        self.assertEqual(
            next_version, f'{str(today.year % 100)}.{str(today.month)}.1.dev1'
        )

    @patch('pontos.release.release.redirect_stdout')
    def test_calculate_calendar_version_old_year(self, stdout_mock):
        today = datetime.datetime.today()
        getvalue_mock = stdout_mock.return_value.__enter__.return_value.getvalue
        getvalue_mock.return_value = f'19.{str(today.month)}.1.dev3'
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')

        release_version, next_version = calculate_calendar_version(fake_version)

        self.assertEqual(
            release_version, f'{str(today.year % 100)}.{str(today.month)}.0'
        )
        self.assertEqual(
            next_version, f'{str(today.year % 100)}.{str(today.month)}.1.dev1'
        )

    @patch('pontos.release.release.redirect_stdout')
    def test_calculate_calendar_version_same_year_month(self, stdout_mock):
        today = datetime.datetime.today()
        getvalue_mock = stdout_mock.return_value.__enter__.return_value.getvalue
        getvalue_mock.return_value = (
            f'{str(today.year % 100)}.{str(today.month)}.1.dev3'
        )
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')

        release_version, next_version = calculate_calendar_version(fake_version)

        self.assertEqual(
            release_version, f'{str(today.year % 100)}.{str(today.month)}.1'
        )
        self.assertEqual(
            next_version, f'{str(today.year % 100)}.{str(today.month)}.2.dev1'
        )

    @patch('pontos.release.release.redirect_stdout')
    def test_calculate_calendar_version_same_year_month_no_dev(
        self, stdout_mock
    ):
        today = datetime.datetime.today()
        getvalue_mock = stdout_mock.return_value.__enter__.return_value.getvalue
        getvalue_mock.return_value = (
            f'{str(today.year % 100)}.{str(today.month)}.1'
        )
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')

        release_version, next_version = calculate_calendar_version(fake_version)

        self.assertEqual(
            release_version, f'{str(today.year % 100)}.{str(today.month)}.2'
        )
        self.assertEqual(
            next_version, f'{str(today.year % 100)}.{str(today.month)}.3.dev1'
        )

    @patch('pontos.release.release.redirect_stdout')
    def test_calculate_calendar_version_not_found(self, stdout_mock):
        getvalue_mock = stdout_mock.return_value.__enter__.return_value.getvalue
        getvalue_mock.return_value = None
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (False, 'MyProject.conf')

        release_version, next_version = calculate_calendar_version(fake_version)

        today = datetime.datetime.today()
        self.assertEqual(
            release_version, f'{str(today.year % 100)}.{str(today.month)}.0'
        )
        self.assertEqual(
            next_version, f'{str(today.year % 100)}.{str(today.month)}.1.dev1'
        )

    def test_find_release_version_in_changelog(self):
        today = datetime.datetime.today()
        release_text = f"""
## [{str(today.year % 100)}.{str(today.month)}.3] - {{}}

### Added

* Added support for GMP 20.08 [#254](https://github.com/greenbone/python-gvm/pull/254)

### Changed

* Refactored Gmp classes into mixins [#254](https://github.com/greenbone/python-gvm/pull/254)

### Fixed

* Require method and condition arguments for modify_alert with an event [#267](https://github.com/greenbone/python-gvm/pull/267)

[1.2.3]: https://github.com/greenbone/python-gvm/compare/v1.6.0...hidden1.2.3

        """

        release_version = find_release_version_in_changelog(release_text)
        self.assertEqual(
            release_version, f'{str(today.year % 100)}.{str(today.month)}.3'
        )

    def test_find_other_release_version_in_changelog(self):
        release_text = """
## [1.1.3] - {}

### Added

* Added support for GMP 20.08 [#254](https://github.com/greenbone/python-gvm/pull/254)

### Changed

* Refactored Gmp classes into mixins [#254](https://github.com/greenbone/python-gvm/pull/254)

### Fixed

* Require method and condition arguments for modify_alert with an event [#267](https://github.com/greenbone/python-gvm/pull/267)

[1.2.3]: https://github.com/greenbone/python-gvm/compare/v1.6.0...hidden1.2.3

        """

        release_version = find_release_version_in_changelog(release_text)
        self.assertEqual(release_version, '1.1.3')

    def test_find_release_version_in_changelog_error(self):
        release_text = "noversion"

        with self.assertRaises(SystemExit):
            find_release_version_in_changelog(release_text)

    def test_not_release_when_no_project_found(self):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (False, '')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'prepare',
            '--release-version',
            '0.0.1',
            '--next-version',
            '0.0.2dev',
        ]
        runner = lambda x: StdOutput('')
        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertFalse(released)

    def test_not_release_when_updating_version_fails(self):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (False, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'prepare',
            '--release-version',
            '0.0.1',
            '--next-version',
            '0.0.2dev',
        ]
        runner = lambda x: StdOutput('')
        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _requests=fake_requests,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertFalse(released)


@patch("pontos.release.release.shutil", new=_shutil_mock)
class ReleaseTestCase(unittest.TestCase):

    valid_gh_release_response = (
        '{"zipball_url": "zip", "tarball_url": "tar", "upload_url":"upload"}'
    )

    def test_release_successfully(self):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_post = MagicMock(spec=requests.Response).return_value
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        fake_requests.post.return_value = fake_post
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'release',
            '--release-version',
            '0.0.1',
        ]
        runner = lambda x: StdOutput('')
        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _requests=fake_requests,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertTrue(released)

    def test_not_release_successfully_when_github_create_release_fails(self):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_post = MagicMock(spec=requests.Response).return_value
        fake_post.status_code = 401
        fake_post.text = self.valid_gh_release_response
        fake_requests.post.return_value = fake_post
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'release',
            '--release-version',
            '0.0.1',
        ]
        runner = lambda x: StdOutput('')
        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _requests=fake_requests,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertFalse(released)

    def test_release_to_specific_git_remote(self):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_post = MagicMock(spec=requests.Response).return_value
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        fake_requests.post.return_value = fake_post
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'release',
            '--release-version',
            '0.0.1',
            '--git-remote-name',
            'testremote',
        ]

        def runner(cmd: str):
            if not 'testremote' in cmd:
                raise ValueError('unexpected cmd: {}'.format(cmd))
            return StdOutput('')

        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _requests=fake_requests,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertTrue(released)


@patch("pontos.release.release.shutil", new=_shutil_mock)
class SignTestCase(unittest.TestCase):

    valid_gh_release_response = (
        '{"zipball_url": "zip", "tarball_url": "tar", "upload_url":"upload"}'
    )

    def test_fail_sign_on_invalid_get_response(self):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_get = MagicMock(spec=requests.Response).return_value
        fake_get.status_code = 404
        fake_get.text = self.valid_gh_release_response
        fake_requests.get.return_value = fake_get
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'sign',
            '--release-version',
            '0.0.1',
        ]

        def runner(_: str):
            return StdOutput('')

        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _requests=fake_requests,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertFalse(released)

    def test_fail_sign_on_upload_fail(self):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_get = MagicMock(spec=requests.Response).return_value
        fake_get.status_code = 200
        fake_get.text = self.valid_gh_release_response
        fake_post = MagicMock(spec=requests.Response).return_value
        fake_post.status_code = 500
        fake_post.text = self.valid_gh_release_response
        fake_requests.post.return_value = fake_post
        fake_requests.get.return_value = fake_get
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'sign',
            '--release-version',
            '0.0.1',
        ]

        def runner(_: str):
            return StdOutput('')

        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _requests=fake_requests,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertFalse(released)

    def test_successfully_sign(self):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_get = MagicMock(spec=requests.Response).return_value
        fake_get.status_code = 200
        fake_get.text = self.valid_gh_release_response
        fake_requests.get.return_value = fake_get
        fake_post = MagicMock(spec=requests.Response).return_value
        fake_post.status_code = 201
        fake_post.text = self.valid_gh_release_response
        fake_requests.post.return_value = fake_post
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--project',
            'testcases',
            'sign',
            '--release-version',
            '0.0.1',
        ]

        def runner(_: str):
            return StdOutput('')

        released = release.main(
            shell_cmd_runner=runner,
            _path=fake_path_class,
            _requests=fake_requests,
            _version=fake_version,
            _changelog=fake_changelog,
            leave=False,
            args=args,
        )
        self.assertTrue(released)
