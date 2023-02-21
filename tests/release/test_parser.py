# Copyright (C) 2023 Greenbone Networks GmbH
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
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from pontos.release.helper import ReleaseType
from pontos.release.parser import (
    DEFAULT_CHANGELOG_CONFIG_FILE,
    DEFAULT_SIGNING_KEY,
    parse_args,
)
from pontos.release.prepare import prepare
from pontos.release.release import release
from pontos.release.sign import sign


class ParseArgsTestCase(unittest.TestCase):
    def test_quiet(self):
        _, _, args = parse_args(["-q", "sign"])
        self.assertTrue(args.quiet)

        _, _, args = parse_args(["sign"])
        self.assertFalse(args.quiet)

    @patch.dict("os.environ", {"GITHUB_USER": "foo"})
    def test_user(self):
        user, _, _ = parse_args(["sign"])
        self.assertEqual(user, "foo")

    @patch.dict("os.environ", {"GITHUB_TOKEN": "foo"})
    def test_token(self):
        _, token, _ = parse_args(["sign"])
        self.assertEqual(token, "foo")


class PrepareParseArgsTestCase(unittest.TestCase):
    def test_prepare_func(self):
        _, _, args = parse_args(["prepare", "--patch"])

        self.assertEqual(args.func, prepare)

    def test_version_group(self):
        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["prepare", "--patch", "--calendar"])

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["prepare", "--patch", "--release-type", "patch"])

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["prepare", "--calendar", "--release-type", "patch"])

    def test_default(self):
        _, _, args = parse_args(["prepare", "--patch"])

        self.assertEqual(args.git_tag_prefix, "v")
        self.assertEqual(args.space, "greenbone")
        self.assertEqual(args.cc_config, Path(DEFAULT_CHANGELOG_CONFIG_FILE))

    def test_missing_release_type(self):
        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["prepare"])

    def test_git_signing_key(self):
        _, _, args = parse_args(
            ["prepare", "--patch", "--git-signing-key", "123"]
        )

        self.assertEqual(args.git_signing_key, "123")

    def test_git_tag_prefix(self):
        _, _, args = parse_args(["prepare", "--patch", "--git-tag-prefix", "a"])

        self.assertEqual(args.git_tag_prefix, "a")

    def test_space(self):
        _, _, args = parse_args(["prepare", "--patch", "--space", "foo"])

        self.assertEqual(args.space, "foo")

    def test_project(self):
        _, _, args = parse_args(["prepare", "--patch", "--project", "foo"])

        self.assertEqual(args.project, "foo")

    def test_conventional_commits_config(self):
        _, _, args = parse_args(
            ["prepare", "--patch", "--conventional-commits-config", "foo.toml"]
        )

        self.assertEqual(args.cc_config, Path("foo.toml"))

    def test_calendar(self):
        _, _, args = parse_args(["prepare", "--calendar"])

        self.assertFalse("calendar" in args)
        self.assertEqual(args.release_type, ReleaseType.CALENDAR)

    def test_patch(self):
        _, _, args = parse_args(["prepare", "--patch"])

        self.assertFalse("patch" in args)
        self.assertEqual(args.release_type, ReleaseType.PATCH)

    def test_release_type(self):
        _, _, args = parse_args(["prepare", "--release-type", "patch"])

        self.assertEqual(args.release_type, ReleaseType.PATCH)

        _, _, args = parse_args(["prepare", "--release-type", "calendar"])

        self.assertEqual(args.release_type, ReleaseType.CALENDAR)

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["prepare", "--release-type", "foo"])

    def test_release_type_version_without_release_version(self):
        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["prepare", "--release-type", "version"])

        _, _, args = parse_args(
            [
                "prepare",
                "--release-type",
                "version",
                "--release-version",
                "1.2.3",
            ]
        )
        self.assertEqual(args.release_type, ReleaseType.VERSION)
        self.assertEqual(args.release_version, "1.2.3")

    def test_release_version(self):
        _, _, args = parse_args(["prepare", "--release-version", "1.2.3"])

        self.assertEqual(args.release_version, "1.2.3")
        self.assertEqual(args.release_type, ReleaseType.VERSION)

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["prepare", "--release-version", "1.2.3", "--patch"])

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["prepare", "--release-version", "1.2.3", "--calendar"])

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(
                [
                    "prepare",
                    "--release-version",
                    "1.2.3",
                    "--release-type",
                    "patch",
                ]
            )

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(
                [
                    "prepare",
                    "--release-version",
                    "1.2.3",
                    "--release-type",
                    "calendar",
                ]
            )


class ReleaseParseArgsTestCase(unittest.TestCase):
    def test_release_func(self):
        _, _, args = parse_args(["release"])

        self.assertEqual(args.func, release)

    def test_default(self):
        _, _, args = parse_args(["release"])

        self.assertEqual(args.git_tag_prefix, "v")
        self.assertEqual(args.space, "greenbone")

    def test_git_remote_name(self):
        _, _, args = parse_args(["release", "--git-remote-name", "foo"])

        self.assertEqual(args.git_remote_name, "foo")

    def test_git_signing_key(self):
        _, _, args = parse_args(["release", "--git-signing-key", "123"])

        self.assertEqual(args.git_signing_key, "123")

    def test_git_tag_prefix(self):
        _, _, args = parse_args(["release", "--git-tag-prefix", "a"])

        self.assertEqual(args.git_tag_prefix, "a")

    def test_space(self):
        _, _, args = parse_args(["release", "--space", "foo"])

        self.assertEqual(args.space, "foo")

    def test_project(self):
        _, _, args = parse_args(["release", "--project", "foo"])

        self.assertEqual(args.project, "foo")

    def test_release_version(self):
        _, _, args = parse_args(["release", "--release-version", "1.2.3"])

        self.assertEqual(args.release_version, "1.2.3")

    def test_next_version(self):
        _, _, args = parse_args(["release", "--next-version", "1.2.3"])

        self.assertEqual(args.next_version, "1.2.3")


class SignParseArgsTestCase(unittest.TestCase):
    def test_sign_func(self):
        _, _, args = parse_args(["sign"])

        self.assertEqual(args.func, sign)

    def test_default(self):
        _, _, args = parse_args(["sign"])

        self.assertEqual(args.git_tag_prefix, "v")
        self.assertEqual(args.space, "greenbone")
        self.assertEqual(args.signing_key, DEFAULT_SIGNING_KEY)

    def test_space(self):
        _, _, args = parse_args(["sign", "--space", "foo"])

        self.assertEqual(args.space, "foo")

    def test_project(self):
        _, _, args = parse_args(["sign", "--project", "foo"])

        self.assertEqual(args.project, "foo")

    def test_release_version(self):
        _, _, args = parse_args(["sign", "--release-version", "1.2.3"])

        self.assertEqual(args.release_version, "1.2.3")

    def test_dry_run(self):
        _, _, args = parse_args(["sign", "--dry-run"])

        self.assertTrue(args.dry_run)

    def test_signing_key(self):
        _, _, args = parse_args(["sign", "--signing-key", "123"])

        self.assertEqual(args.signing_key, "123")

    def test_passphrase(self):
        _, _, args = parse_args(["sign", "--passphrase", "123"])

        self.assertEqual(args.passphrase, "123")