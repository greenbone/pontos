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
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from io import StringIO

from pontos.testing import temp_directory
from pontos.version.main import VersionExitCode, main


class MainTestCase(unittest.TestCase):
    def test_no_command(self):
        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            main([])

    def test_no_project(self):
        with temp_directory(change_into=True), self.assertRaises(
            SystemExit
        ) as cm, redirect_stderr(StringIO()):
            main(["show"])

        self.assertEqual(cm.exception.code, VersionExitCode.NO_PROJECT)

    def test_update_success(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["update", "2.0.0"])

        self.assertEqual(
            out.getvalue(), "Updated version from 1.2.3 to 2.0.0.\n"
        )

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)

    def test_update_failure(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stderr(
            StringIO()
        ), self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                "{}",
                encoding="utf8",
            )
            main(["update", "2.0.0"])

        self.assertEqual(cm.exception.code, VersionExitCode.UPDATE_ERROR)

    def test_update_already_up_to_date(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["update", "1.2.3"])

        self.assertEqual(out.getvalue(), "Version is already up-to-date.\n")

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)

    def test_show(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["show"])

        self.assertEqual(out.getvalue(), "1.2.3\n")

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)

    def test_show_error(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stderr(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "abc"}',
                encoding="utf8",
            )
            main(["show"])

        self.assertEqual(out.getvalue(), "Invalid version: 'abc'\n")

        self.assertEqual(
            cm.exception.code, VersionExitCode.CURRENT_VERSION_ERROR
        )

    def test_verify_failure(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stderr(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["verify", "1.2.4"])

        self.assertEqual(
            out.getvalue(),
            "Provided version 1.2.4 does not match the current version "
            f"1.2.3 in {version_file.resolve()}.\n",
        )

        self.assertEqual(cm.exception.code, VersionExitCode.VERIFY_ERROR)

    def test_verify_success(self):
        with temp_directory(change_into=True) as temp_dir, self.assertRaises(
            SystemExit
        ) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["verify", "1.2.3"])

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)

    def test_verify_current(self):
        with temp_directory(change_into=True) as temp_dir, self.assertRaises(
            SystemExit
        ) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["verify", "current"])

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)

    def test_next_invalid_current(self):
        with redirect_stderr(StringIO()), temp_directory(
            change_into=True
        ) as temp_dir, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.tt"}',
                encoding="utf8",
            )
            main(["next", "dev", "--versioning-scheme", "pep440"])

        self.assertEqual(
            cm.exception.code, VersionExitCode.CURRENT_VERSION_ERROR
        )

    def test_next_dev(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["next", "dev", "--versioning-scheme", "pep440"])

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)
        self.assertEqual(out.getvalue(), "1.2.4.dev1\n")

    def test_next_patch(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["next", "patch", "--versioning-scheme", "pep440"])

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)
        self.assertEqual(out.getvalue(), "1.2.4\n")

    def test_next_minor(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["next", "minor", "--versioning-scheme", "pep440"])

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)
        self.assertEqual(out.getvalue(), "1.3.0\n")

    def test_next_major(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["next", "major", "--versioning-scheme", "pep440"])

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)
        self.assertEqual(out.getvalue(), "2.0.0\n")

    def test_next_alpha(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["next", "alpha", "--versioning-scheme", "semver"])

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)
        self.assertEqual(out.getvalue(), "1.2.4-alpha1\n")

    def test_next_beta(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["next", "beta", "--versioning-scheme", "semver"])

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)
        self.assertEqual(out.getvalue(), "1.2.4-beta1\n")

    def test_next_rc(self):
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["next", "rc", "--versioning-scheme", "semver"])

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)
        self.assertEqual(out.getvalue(), "1.2.4-rc1\n")

    def test_next_calendar(self):
        today = datetime.today()
        with temp_directory(change_into=True) as temp_dir, redirect_stdout(
            StringIO()
        ) as out, self.assertRaises(SystemExit) as cm:
            version_file = temp_dir / "package.json"
            version_file.write_text(
                '{"name": "foo", "version": "1.2.3"}',
                encoding="utf8",
            )
            main(["next", "calendar", "--versioning-scheme", "pep440"])

        self.assertEqual(cm.exception.code, VersionExitCode.SUCCESS)
        self.assertEqual(
            out.getvalue(), f"{today.year % 100}.{today.month}.0\n"
        )
