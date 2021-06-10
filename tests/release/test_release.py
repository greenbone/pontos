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

import os
import shutil
import unittest

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

from pontos.release.helper import version
from pontos import release, changelog


@dataclass
class StdOutput:
    stdout: bytes


_shutil_mock = MagicMock(spec=shutil)


@patch("pontos.release.helper.shutil", new=_shutil_mock)
class PrepareTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['GITHUB_TOKEN'] = 'foo'
        os.environ['GITHUB_USER'] = 'bar'

    def test_prepare_successfully(self):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (True, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            'prepare',
            '--release-version',
            '0.0.1',
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
            'prepare',
            '--git-signing-key',
            '0815',
            '--release-version',
            '0.0.1',
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
            "git commit -S 0815 -m 'automatic release to 0.0.1'", called
        )
        self.assertIn(
            "git tag -u 0815 v0.0.1 -m 'automatic release to 0.0.1'", called
        )

    def test_fail_if_tag_is_already_taken(self):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_changelog = MagicMock(spec=changelog)

        args = [
            'prepare',
            '--release-version',
            '0.0.1',
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

    def test_not_release_when_no_project_found(self):
        fake_path_class = MagicMock(spec=Path)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (False, '')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')

        args = [
            'prepare',
            '--release-version',
            '0.0.1',
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
            'prepare',
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


@patch("pontos.release.helper.shutil", new=_shutil_mock)
class ReleaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['GITHUB_TOKEN'] = 'foo'
        os.environ['GITHUB_USER'] = 'bar'
        self.valid_gh_release_response = (
            '{"zipball_url": "zip", "tarball_url":'
            ' "tar", "upload_url":"upload"}'
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
            'release',
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
            'release',
            '--project',
            'foo',
            '--release-version',
            '0.0.1',
            '--next-version',
            '0.0.2.dev1',
            '--git-remote-name',
            'upstream',
        ]

        called = []

        def runner(cmd: str):
            called.append(cmd)
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

        self.assertIn('git push --follow-tags upstream', called)
        self.assertIn('git add MyProject.conf', called)
        self.assertIn(
            "git commit -m '* Update to version"
            " 0.0.2.dev1\n* Add empty changelog after 0.0.1'",
            called,
        )
        print(called)


@patch("pontos.release.helper.shutil", new=_shutil_mock)
class SignTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['GITHUB_TOKEN'] = 'foo'
        os.environ['GITHUB_USER'] = 'bar'
        self.valid_gh_release_response = (
            '{"zipball_url": "zip", "tarball_url":'
            ' "tar", "upload_url":"upload"}'
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
            'sign',
            '--project',
            'foo',
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
            'sign',
            '--project',
            'foo',
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
            'sign',
            '--project',
            'bar',
            '--release-version',
            '0.0.1',
        ]

        called = []

        def runner(cmd: str):
            called.append(cmd)
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
