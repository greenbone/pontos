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
import subprocess
import unittest
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

from pontos.git.git import ConfigScope, Git, GitError, exec_git
from pontos.release.helper import find_signing_key, get_git_repository_name
from pontos.testing import temp_git_repository


@contextlib.contextmanager
def init_test_git_repo() -> Generator[Path, None, None]:
    with temp_git_repository() as repo_path:
        exec_git("remote", "add", "foo", "https://foo.bar/bla.git")
        exec_git("remote", "add", "origin", "https://foo.bar/testrepo.git")
        yield repo_path


class GetGitRepositoryNameTestCase(unittest.TestCase):
    def test_get_project_name(self):
        with init_test_git_repo():
            project = get_git_repository_name(remote="foo")
            self.assertEqual(project, "bla")

            project = get_git_repository_name()
            self.assertEqual(project, "testrepo")


class FindSigningKeyTestCase(unittest.TestCase):
    def test_find_signing_key(self):
        terminal = MagicMock()

        with temp_git_repository():
            git = Git()
            git.config(
                "user.signingkey",
                "1234567890ABCEDEF1234567890ABCEDEF123456",
                scope=ConfigScope.LOCAL,
            )
            signing_key = find_signing_key(terminal)
            self.assertEqual(
                signing_key, "1234567890ABCEDEF1234567890ABCEDEF123456"
            )

    def test_find_no_signing_key(self):
        terminal = MagicMock()
        saved_key = None

        git = Git()
        try:
            # save possibly set git signing key from user temporarily
            try:
                saved_key = git.config(
                    "user.signingkey", scope=ConfigScope.GLOBAL
                )
            except GitError:
                saved_key = None

            try:
                git.config("user.signingkey", "", scope=ConfigScope.GLOBAL)
            except subprocess.CalledProcessError as e:
                self.assertEqual(e.returncode, 5)

            with temp_git_repository():
                signing_key = find_signing_key(terminal)
                self.assertEqual(signing_key, "")

        finally:
            # reset the previously saved signing key ...
            if saved_key is not None:
                git.config(
                    "user.signingkey", saved_key, scope=ConfigScope.GLOBAL
                )
