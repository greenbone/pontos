# SPDX-FileCopyrightText: 2021-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import contextlib
import os
import subprocess
import unittest
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

from pontos.git import ConfigScope, Git, GitError
from pontos.release.helper import (
    ReleaseType,
    find_signing_key,
    get_git_repository_name,
    get_next_release_version,
    repository_split,
)
from pontos.testing import temp_git_repository
from pontos.version import VersionError
from pontos.version.schemes import SemanticVersioningScheme


@contextlib.contextmanager
def init_test_git_repo() -> Generator[Path, None, None]:
    with temp_git_repository() as repo_path:
        git = Git()
        git.add_remote("foo", "https://foo.bar/bla.git")
        git.add_remote("origin", "https://foo.bar/testrepo.git")
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

    @unittest.skipUnless(os.environ.get("CI"), "only run on CI")
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


class GetNextReleaseVersionTestCase(unittest.TestCase):
    def test_next_major_version(self):
        calculator = SemanticVersioningScheme.calculator()
        last_version = SemanticVersioningScheme.parse_version("1.0.0")
        version = get_next_release_version(
            calculator=calculator,
            last_release_version=last_version,
            release_type=ReleaseType.MAJOR,
            release_version=None,
        )

        self.assertEqual(
            version, SemanticVersioningScheme.parse_version("2.0.0")
        )

    def test_next_minor_version(self):
        calculator = SemanticVersioningScheme.calculator()
        last_version = SemanticVersioningScheme.parse_version("1.0.0")
        version = get_next_release_version(
            calculator=calculator,
            last_release_version=last_version,
            release_type=ReleaseType.MINOR,
            release_version=None,
        )

        self.assertEqual(
            version, SemanticVersioningScheme.parse_version("1.1.0")
        )

    def test_next_patch_version(self):
        calculator = SemanticVersioningScheme.calculator()
        last_version = SemanticVersioningScheme.parse_version("1.0.0")
        version = get_next_release_version(
            calculator=calculator,
            last_release_version=last_version,
            release_type=ReleaseType.PATCH,
            release_version=None,
        )

        self.assertEqual(
            version, SemanticVersioningScheme.parse_version("1.0.1")
        )

    def test_next_calendar_version(self):
        calculator = SemanticVersioningScheme.calculator()
        last_version = SemanticVersioningScheme.parse_version("1.0.0")

        with patch.object(
            calculator,
            "next_calendar_version",
            return_value=SemanticVersioningScheme.parse_version("23.7.0"),
        ):
            version = get_next_release_version(
                calculator=calculator,
                last_release_version=last_version,
                release_type=ReleaseType.CALENDAR,
                release_version=None,
            )

        self.assertEqual(
            version, SemanticVersioningScheme.parse_version("23.7.0")
        )

    def test_next_alpha_version(self):
        calculator = SemanticVersioningScheme.calculator()
        last_version = SemanticVersioningScheme.parse_version("1.0.0")
        version = get_next_release_version(
            calculator=calculator,
            last_release_version=last_version,
            release_type=ReleaseType.ALPHA,
            release_version=None,
        )

        self.assertEqual(
            version, SemanticVersioningScheme.parse_version("1.0.1-alpha1")
        )

    def test_next_beta_version(self):
        calculator = SemanticVersioningScheme.calculator()
        last_version = SemanticVersioningScheme.parse_version("1.0.0")
        version = get_next_release_version(
            calculator=calculator,
            last_release_version=last_version,
            release_type=ReleaseType.BETA,
            release_version=None,
        )

        self.assertEqual(
            version, SemanticVersioningScheme.parse_version("1.0.1-beta1")
        )

    def test_next_release_candidate_version(self):
        calculator = SemanticVersioningScheme.calculator()
        last_version = SemanticVersioningScheme.parse_version("1.0.0")
        version = get_next_release_version(
            calculator=calculator,
            last_release_version=last_version,
            release_type=ReleaseType.RELEASE_CANDIDATE,
            release_version=None,
        )

        self.assertEqual(
            version, SemanticVersioningScheme.parse_version("1.0.1-rc1")
        )

    def test_no_release_type(self):
        calculator = SemanticVersioningScheme.calculator()
        last_version = SemanticVersioningScheme.parse_version("1.0.0")
        next_version = SemanticVersioningScheme.parse_version("1.2.3")
        version = get_next_release_version(
            calculator=calculator,
            last_release_version=last_version,
            release_type=None,
            release_version=next_version,
        )

        self.assertEqual(version, next_version)

    def test_release_type_version(self):
        calculator = SemanticVersioningScheme.calculator()
        last_version = SemanticVersioningScheme.parse_version("1.0.0")
        next_version = SemanticVersioningScheme.parse_version("1.2.3")
        version = get_next_release_version(
            calculator=calculator,
            last_release_version=last_version,
            release_type=ReleaseType.VERSION,
            release_version=next_version,
        )

        self.assertEqual(version, next_version)

    def test_no_release_type_and_release_version(self):
        calculator = SemanticVersioningScheme.calculator()
        last_version = SemanticVersioningScheme.parse_version("1.0.0")

        with self.assertRaisesRegex(
            VersionError,
            "No release version provided. Either use a different release "
            "type or provide a release version.",
        ):
            get_next_release_version(
                calculator=calculator,
                last_release_version=last_version,
                release_type=None,
                release_version=None,
            )

    def test_no_release_type_and_no_last_release_version(self):
        calculator = SemanticVersioningScheme.calculator()
        release_version = SemanticVersioningScheme.parse_version("1.0.0")

        version = get_next_release_version(
            calculator=calculator,
            last_release_version=None,
            release_type=None,
            release_version=release_version,
        )

        self.assertEqual(version, release_version)

    def test_release_type_version_and_no_last_release_version(self):
        calculator = SemanticVersioningScheme.calculator()
        release_version = SemanticVersioningScheme.parse_version("1.0.0")

        version = get_next_release_version(
            calculator=calculator,
            last_release_version=None,
            release_type=ReleaseType.VERSION,
            release_version=release_version,
        )

        self.assertEqual(version, release_version)

    def test_no_last_release_version(self):
        calculator = SemanticVersioningScheme.calculator()

        with self.assertRaisesRegex(
            VersionError,
            "No last release version found for release type alpha. Either "
            "check the project setup or set a release version explicitly.",
        ):
            get_next_release_version(
                calculator=calculator,
                last_release_version=None,
                release_type=ReleaseType.ALPHA,
                release_version=None,
            )

    def test_release_version_with_invalid_release_type(self):
        calculator = SemanticVersioningScheme.calculator()
        release_version = SemanticVersioningScheme.parse_version("1.0.0")

        with self.assertRaisesRegex(
            VersionError,
            "Invalid release type alpha when setting release version "
            "explicitly. Use release type version instead.",
        ):
            get_next_release_version(
                calculator=calculator,
                last_release_version=None,
                release_type=ReleaseType.ALPHA,
                release_version=release_version,
            )


class RepositorySplitTestCase(unittest.TestCase):
    def test_invalid_repository(self):
        with self.assertRaisesRegex(
            ValueError,
            r"Invalid repository foo/bar/baz. Format must be owner/name.",
        ):
            repository_split("foo/bar/baz")

        with self.assertRaisesRegex(
            ValueError,
            r"Invalid repository foo_bar_baz. Format must be owner/name.",
        ):
            repository_split("foo_bar_baz")

    def test_repository(self):
        space, project = repository_split("foo/bar")

        self.assertEqual(space, "foo")
        self.assertEqual(project, "bar")
