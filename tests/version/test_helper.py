# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest
from unittest.mock import patch

from pontos.git import Git
from pontos.version.helper import (
    get_last_release_version,
    get_last_release_versions,
)
from pontos.version.schemes import (
    PEP440VersioningScheme,
    SemanticVersioningScheme,
)

parse_version = PEP440VersioningScheme.parse_version
Version = PEP440VersioningScheme.version_cls


class GetLastReleaseVersionsTestCase(unittest.TestCase):
    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_versions(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = ["1", "2", "3.55"]

        it = get_last_release_versions(parse_version)

        version = next(it)
        self.assertEqual(version, Version("3.55"))

        version = next(it)
        self.assertEqual(version, Version("2"))

        version = next(it)
        self.assertEqual(version, Version("1"))

        with self.assertRaises(StopIteration):
            next(it)

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_no_release_versions(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = []

        it = get_last_release_versions(parse_version)
        with self.assertRaises(StopIteration):
            next(it)

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_versions_with_git_prefix(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = ["v1", "v2", "v3.55"]

        it = get_last_release_versions(parse_version, git_tag_prefix="v")

        version = next(it)
        self.assertEqual(version, Version("3.55"))

        version = next(it)
        self.assertEqual(version, Version("2"))

        version = next(it)
        self.assertEqual(version, Version("1"))

        with self.assertRaises(StopIteration):
            next(it)

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_versions_ignore_pre_releases(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = [
            "1",
            "2",
            "3.55a1",
            "3.56.dev1",
            "4.0.0rc1",
            "4.0.1b1",
        ]
        it = get_last_release_versions(parse_version, ignore_pre_releases=True)

        version = next(it)
        self.assertEqual(version, Version("2"))

        version = next(it)
        self.assertEqual(version, Version("1"))

        with self.assertRaises(StopIteration):
            next(it)

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_versions_no_non_pre_release(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = [
            "3.55a1",
            "3.56.dev1",
            "4.0.0rc1",
            "4.0.1b1",
        ]

        it = get_last_release_versions(parse_version, ignore_pre_releases=True)

        with self.assertRaises(StopIteration):
            next(it)

    @patch("pontos.version.helper.Git", spec=Git)
    def test_invalid_version(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = [
            "1.0.0",
            "3.55a1",
            "2.0.0",
        ]

        it = get_last_release_versions(SemanticVersioningScheme.parse_version)

        version = next(it)
        self.assertEqual(
            version, SemanticVersioningScheme.parse_version("2.0.0")
        )

        version = next(it)
        self.assertEqual(
            version, SemanticVersioningScheme.parse_version("1.0.0")
        )

        with self.assertRaises(StopIteration):
            next(it)


class GetLastReleaseVersionTestCase(unittest.TestCase):
    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_version(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = ["1", "2", "3.55"]
        self.assertEqual(
            get_last_release_version(parse_version), Version("3.55")
        )

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_no_release_version(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = []
        self.assertIsNone(get_last_release_version(parse_version))

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_version_with_git_prefix(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = ["v1", "v2", "v3.55"]
        self.assertEqual(
            get_last_release_version(parse_version, git_tag_prefix="v"),
            Version("3.55"),
        )

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_version_ignore_pre_releases(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = [
            "1",
            "2",
            "3.55a1",
            "3.56.dev1",
            "4.0.0rc1",
            "4.0.1b1",
        ]
        self.assertEqual(
            get_last_release_version(parse_version, ignore_pre_releases=True),
            Version("2"),
        )

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_version_no_non_pre_release(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = [
            "3.55a1",
            "3.56.dev1",
            "4.0.0rc1",
            "4.0.1b1",
        ]
        self.assertIsNone(
            get_last_release_version(parse_version, ignore_pre_releases=True)
        )

    @patch("pontos.version.helper.Git", spec=Git)
    def test_get_last_release_version_tag_name(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = [
            "4.0.0rc1",
            "4.0.1b1",
        ]
        self.assertEqual(
            get_last_release_version(parse_version, tag_name="4.0.*"),
            Version("4.0.1b1"),
        )

    @patch("pontos.version.helper.Git", spec=Git)
    def test_invalid_version(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = ["1.0.0", "2.0.0", "3.55a1"]

        self.assertEqual(
            get_last_release_version(SemanticVersioningScheme.parse_version),
            SemanticVersioningScheme.parse_version("2.0.0"),
        )

    @patch("pontos.version.helper.Git", spec=Git)
    def test_success_with_invalid_version(self, git_mock):
        git_interface = git_mock.return_value
        git_interface.list_tags.return_value = [
            "1.0.0",
            "2.0.0",
            "3.55a1",
            "4.0.0",
        ]

        version = get_last_release_version(
            SemanticVersioningScheme.parse_version
        )
        self.assertEqual(
            version, SemanticVersioningScheme.parse_version("4.0.0")
        )
