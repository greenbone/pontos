# pylint: disable=C0413,W0108

import shutil
import unittest

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

from pontos import version, release, changelog


@dataclass
class StdOutput:
    stdout: bytes


_shutil_mock = MagicMock(spec=shutil)


@patch("pontos.release.release.shutil", new=_shutil_mock)
class ReleaseTestCase(unittest.TestCase):

    valid_gh_release_response = (
        '{"zipball_url": "zip", "tarball_url": "tar", "upload_url":"upload"}'
    )

    def test_prepare_successfully(self):
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
            '--release-version',
            '0.0.1',
            '--next-release-version',
            '0.0.2dev',
            '--project',
            'testcases',
            'prepare',
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

    def test_fail_if_tag_is_already_taken(self):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_version = MagicMock(spec=version)
        fake_changelog = MagicMock(spec=changelog)
        args = [
            '--release-version',
            '0.0.1',
            '--next-release-version',
            '0.0.2dev',
            '--project',
            'testcases',
            'prepare',
        ]
        runner = lambda x: StdOutput('v0.0.1'.encode())
        with self.assertRaises(ValueError):
            release.main(
                shell_cmd_runner=runner,
                _path=fake_path_class,
                _requests=fake_requests,
                _version=fake_version,
                _changelog=fake_changelog,
                leave=False,
                args=args,
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
            '--release-version',
            '0.0.1',
            '--next-release-version',
            '0.0.2dev',
            '--project',
            'testcases',
            'release',
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
            '--release-version',
            '0.0.1',
            '--next-release-version',
            '0.0.2dev',
            '--project',
            'testcases',
            'release',
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

    def test_not_release_when_no_project_found(self):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (False, '')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--release-version',
            '0.0.1',
            '--next-release-version',
            '0.0.2dev',
            '--project',
            'testcases',
            'prepare',
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

    def test_not_release_when_updating_version_fails(self):
        fake_path_class = MagicMock(spec=Path)
        fake_requests = MagicMock(spec=requests)
        fake_version = MagicMock(spec=version)
        fake_version.main.return_value = (False, 'MyProject.conf')
        fake_changelog = MagicMock(spec=changelog)
        fake_changelog.update.return_value = ('updated', 'changelog')
        args = [
            '--release-version',
            '0.0.1',
            '--next-release-version',
            '0.0.2dev',
            '--project',
            'testcases',
            'prepare',
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
            '--release-version',
            '0.0.1',
            '--next-release-version',
            '0.0.2dev',
            '--project',
            'testcases',
            '--git-remote-name',
            'testremote',
            'release',
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
