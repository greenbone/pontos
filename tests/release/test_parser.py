# Copyright (C) 2023 Greenbone AG
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

from pontos.release.create import create_release
from pontos.release.helper import ReleaseType
from pontos.release.parser import DEFAULT_SIGNING_KEY, parse_args
from pontos.release.show import OutputFormat, show
from pontos.release.sign import sign
from pontos.version.schemes._pep440 import PEP440Version, PEP440VersioningScheme


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


class CreateParseArgsTestCase(unittest.TestCase):
    def test_create_func(self):
        _, _, args = parse_args(["create", "--release-type", "patch"])

        self.assertEqual(args.func, create_release)

    def test_release_alias(self):
        _, _, args = parse_args(["release", "--release-type", "patch"])

        self.assertEqual(args.func, create_release)

    def test_default(self):
        _, _, args = parse_args(["create", "--release-type", "patch"])

        self.assertEqual(args.git_tag_prefix, "v")
        self.assertEqual(args.space, "greenbone")
        self.assertFalse(args.local)
        self.assertFalse(args.github_pre_release)

    def test_git_remote_name(self):
        _, _, args = parse_args(
            ["create", "--git-remote-name", "foo", "--release-type", "patch"]
        )

        self.assertEqual(args.git_remote_name, "foo")

    def test_git_signing_key(self):
        _, _, args = parse_args(
            ["create", "--git-signing-key", "123", "--release-type", "patch"]
        )

        self.assertEqual(args.git_signing_key, "123")

    def test_git_tag_prefix(self):
        _, _, args = parse_args(
            ["create", "--git-tag-prefix", "a", "--release-type", "patch"]
        )

        self.assertEqual(args.git_tag_prefix, "a")

        _, _, args = parse_args(
            ["create", "--git-tag-prefix", "", "--release-type", "patch"]
        )

        self.assertEqual(args.git_tag_prefix, "")

        _, _, args = parse_args(
            ["create", "--git-tag-prefix", "--release-type", "patch"]
        )

        self.assertEqual(args.git_tag_prefix, "")

    def test_space(self):
        _, _, args = parse_args(
            ["create", "--space", "foo", "--release-type", "patch"]
        )

        self.assertEqual(args.space, "foo")

    def test_project(self):
        _, _, args = parse_args(
            ["create", "--project", "foo", "--release-type", "patch"]
        )

        self.assertEqual(args.project, "foo")

    def test_next_version(self):
        _, _, args = parse_args(
            ["create", "--next-version", "1.2.3", "--release-type", "patch"]
        )

        self.assertEqual(args.next_version, PEP440Version("1.2.3"))

    def test_no_next_version(self):
        _, _, args = parse_args(
            ["create", "--no-next-version", "--release-type", "patch"]
        )

        self.assertFalse(args.next_version)

    def test_next_version_conflict(self):
        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(
                [
                    "create",
                    "--release-type",
                    "patch",
                    "--no-next-version",
                    "--next-verson",
                    "1.2.3",
                ]
            )

    def test_release_type(self):
        _, _, args = parse_args(["create", "--release-type", "patch"])

        self.assertEqual(args.release_type, ReleaseType.PATCH)

        _, _, args = parse_args(["create", "--release-type", "calendar"])

        self.assertEqual(args.release_type, ReleaseType.CALENDAR)

        _, _, args = parse_args(["create", "--release-type", "minor"])

        self.assertEqual(args.release_type, ReleaseType.MINOR)

        _, _, args = parse_args(["create", "--release-type", "major"])

        self.assertEqual(args.release_type, ReleaseType.MAJOR)

        _, _, args = parse_args(["create", "--release-type", "alpha"])

        self.assertEqual(args.release_type, ReleaseType.ALPHA)

        _, _, args = parse_args(["create", "--release-type", "beta"])

        self.assertEqual(args.release_type, ReleaseType.BETA)

        _, _, args = parse_args(
            ["create", "--release-type", "release-candidate"]
        )

        self.assertEqual(args.release_type, ReleaseType.RELEASE_CANDIDATE)

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["create", "--release-type", "foo"])

    def test_release_type_version_without_release_version(self):
        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["create", "--release-type", "version"])

        _, _, args = parse_args(
            [
                "create",
                "--release-type",
                "version",
                "--release-version",
                "1.2.3",
            ]
        )
        self.assertEqual(args.release_type, ReleaseType.VERSION)
        self.assertEqual(args.release_version, PEP440Version("1.2.3"))

    def test_release_version(self):
        _, _, args = parse_args(["create", "--release-version", "1.2.3"])

        self.assertEqual(args.release_version, PEP440Version("1.2.3"))
        self.assertEqual(args.release_type, ReleaseType.VERSION)

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["create", "--release-version", "1.2.3", "--patch"])

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["create", "--release-version", "1.2.3", "--calendar"])

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(
                [
                    "create",
                    "--release-version",
                    "1.2.3",
                    "--release-type",
                    "patch",
                ]
            )

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(
                [
                    "create",
                    "--release-version",
                    "1.2.3",
                    "--release-type",
                    "calendar",
                ]
            )

    def test_local(self):
        _, _, args = parse_args(
            ["create", "--local", "--release-type", "patch"]
        )

        self.assertTrue(args.local)

    def test_conventional_commits_config(self):
        _, _, args = parse_args(
            [
                "create",
                "--conventional-commits-config",
                "foo.toml",
                "--release-type",
                "patch",
            ]
        )

        self.assertEqual(args.cc_config, Path("foo.toml"))

    def test_release_series(self):
        _, _, args = parse_args(
            ["create", "--release-type", "patch", "--release-series", "22.4"]
        )

        self.assertEqual(args.release_series, "22.4")

    def test_update_project(self):
        _, _, args = parse_args(["create", "--release-type", "patch"])

        self.assertTrue(args.update_project)

        _, _, args = parse_args(
            ["create", "--release-type", "patch", "--update-project"]
        )

        self.assertTrue(args.update_project)

        _, _, args = parse_args(
            ["create", "--release-type", "patch", "--no-update-project"]
        )

        self.assertFalse(args.update_project)

    def test_github_pre_release(self):
        _, _, args = parse_args(
            ["create", "--release-type", "patch", "--github-pre-release"]
        )

        self.assertTrue(args.github_pre_release)


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

        self.assertEqual(args.release_version, PEP440Version("1.2.3"))

    def test_dry_run(self):
        _, _, args = parse_args(["sign", "--dry-run"])

        self.assertTrue(args.dry_run)

    def test_signing_key(self):
        _, _, args = parse_args(["sign", "--signing-key", "123"])

        self.assertEqual(args.signing_key, "123")

    def test_passphrase(self):
        _, _, args = parse_args(["sign", "--passphrase", "123"])

        self.assertEqual(args.passphrase, "123")

    def test_release_series(self):
        _, _, args = parse_args(["sign", "--release-series", "22.4"])

        self.assertEqual(args.release_series, "22.4")


class ShowParseArgsTestCase(unittest.TestCase):
    def test_show_func(self):
        _, _, args = parse_args(["show", "--release-type", "patch"])

        self.assertEqual(args.func, show)

    def test_defaults(self):
        _, _, args = parse_args(["show", "--release-type", "patch"])

        self.assertEqual(args.git_tag_prefix, "v")
        self.assertEqual(args.versioning_scheme, PEP440VersioningScheme)

    def test_release_series(self):
        _, _, args = parse_args(
            ["show", "--release-type", "patch", "--release-series", "1.2"]
        )

        self.assertEqual(args.release_series, "1.2")

    def test_release_type(self):
        _, _, args = parse_args(["show", "--release-type", "patch"])

        self.assertEqual(args.release_type, ReleaseType.PATCH)

        _, _, args = parse_args(["show", "--release-type", "calendar"])

        self.assertEqual(args.release_type, ReleaseType.CALENDAR)

        _, _, args = parse_args(["show", "--release-type", "minor"])

        self.assertEqual(args.release_type, ReleaseType.MINOR)

        _, _, args = parse_args(["show", "--release-type", "major"])

        self.assertEqual(args.release_type, ReleaseType.MAJOR)

        _, _, args = parse_args(["show", "--release-type", "alpha"])

        self.assertEqual(args.release_type, ReleaseType.ALPHA)

        _, _, args = parse_args(["show", "--release-type", "beta"])

        self.assertEqual(args.release_type, ReleaseType.BETA)

        _, _, args = parse_args(["show", "--release-type", "release-candidate"])

        self.assertEqual(args.release_type, ReleaseType.RELEASE_CANDIDATE)

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(["show", "--release-type", "foo"])

    def test_git_tag_prefix(self):
        _, _, args = parse_args(
            ["show", "--git-tag-prefix", "a", "--release-type", "patch"]
        )

        self.assertEqual(args.git_tag_prefix, "a")

        _, _, args = parse_args(
            ["show", "--git-tag-prefix", "", "--release-type", "patch"]
        )

        self.assertEqual(args.git_tag_prefix, "")

        _, _, args = parse_args(
            ["show", "--git-tag-prefix", "--release-type", "patch"]
        )

        self.assertEqual(args.git_tag_prefix, "")

    def test_release_version(self):
        _, _, args = parse_args(["show", "--release-version", "1.2.3"])

        self.assertEqual(args.release_version, PEP440Version("1.2.3"))
        self.assertEqual(args.release_type, ReleaseType.VERSION)

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(
                [
                    "show",
                    "--release-version",
                    "1.2.3",
                    "--release-type",
                    "patch",
                ]
            )

        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parse_args(
                [
                    "show",
                    "--release-version",
                    "1.2.3",
                    "--release-type",
                    "calendar",
                ]
            )

    def test_output_format(self):
        _, _, args = parse_args(
            ["show", "--release-type", "patch", "--output-format", "env"]
        )

        self.assertEqual(args.output_format, OutputFormat.ENV)

        _, _, args = parse_args(
            ["show", "--release-type", "patch", "--output-format", "json"]
        )

        self.assertEqual(args.output_format, OutputFormat.JSON)

        _, _, args = parse_args(
            [
                "show",
                "--release-type",
                "patch",
                "--output-format",
                "github-action",
            ]
        )

        with patch.dict(
            "os.environ", {"GITHUB_OUTPUT": "/tmp/output"}, clear=True
        ):
            self.assertEqual(args.output_format, OutputFormat.GITHUB_ACTION)
