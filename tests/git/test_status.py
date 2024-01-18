# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import os
import unittest
from pathlib import Path

from pontos.git._status import Status, StatusEntry, parse_git_status


class StatusEntryTestCase(unittest.TestCase):
    def test_parse_modified_modified(self):
        status = StatusEntry("MM foo.txt")

        self.assertEqual(status.index, Status.MODIFIED)
        self.assertEqual(status.working_tree, Status.MODIFIED)
        self.assertEqual(status.path, Path("foo.txt"))

    def test_parse_modified_unmodified(self):
        status = StatusEntry("M  foo.txt")

        self.assertEqual(status.index, Status.MODIFIED)
        self.assertEqual(status.working_tree, Status.UNMODIFIED)
        self.assertEqual(status.path, Path("foo.txt"))

    def test_parse_deleted(self):
        status = StatusEntry("D  foo.txt")

        self.assertEqual(status.index, Status.DELETED)
        self.assertEqual(status.working_tree, Status.UNMODIFIED)
        self.assertEqual(status.path, Path("foo.txt"))

    def test_parse_added(self):
        status = StatusEntry("A  foo.txt")

        self.assertEqual(status.index, Status.ADDED)
        self.assertEqual(status.working_tree, Status.UNMODIFIED)
        self.assertEqual(status.path, Path("foo.txt"))

    def test_parse_untracked(self):
        status = StatusEntry("?? foo.txt")

        self.assertEqual(status.index, Status.UNTRACKED)
        self.assertEqual(status.working_tree, Status.UNTRACKED)
        self.assertEqual(status.path, Path("foo.txt"))

    def test_parse_ignored_untracked(self):
        status = StatusEntry("!? foo.txt")

        self.assertEqual(status.index, Status.IGNORED)
        self.assertEqual(status.working_tree, Status.UNTRACKED)
        self.assertEqual(status.path, Path("foo.txt"))

    def test_pathlike(self):
        status = StatusEntry("MM foo.txt")
        self.assertEqual(os.fspath(status), "foo.txt")


class ParseGitStatusTestCase(unittest.TestCase):
    def test_parse_git_status(self):
        output = (
            b" M bar.json\x00R  foo.rst\x00foo.md\x00A  foo.txt\x00"
            b"MM ipsum.json\x00AM ipsum.txt\x00D  lorem.json\x00"
        )

        it = parse_git_status(output.decode("utf-8"))

        status = next(it)
        self.assertEqual(status.index, Status.UNMODIFIED)
        self.assertEqual(status.working_tree, Status.MODIFIED)
        self.assertEqual(status.path, Path("bar.json"))

        status = next(it)
        self.assertEqual(status.index, Status.RENAMED)
        self.assertEqual(status.working_tree, Status.UNMODIFIED)
        self.assertEqual(status.path, Path("foo.rst"))
        self.assertEqual(status.old_path, Path("foo.md"))

        status = next(it)
        self.assertEqual(status.index, Status.ADDED)
        self.assertEqual(status.working_tree, Status.UNMODIFIED)
        self.assertEqual(status.path, Path("foo.txt"))

        status = next(it)
        self.assertEqual(status.index, Status.MODIFIED)
        self.assertEqual(status.working_tree, Status.MODIFIED)
        self.assertEqual(status.path, Path("ipsum.json"))

        status = next(it)
        self.assertEqual(status.index, Status.ADDED)
        self.assertEqual(status.working_tree, Status.MODIFIED)
        self.assertEqual(status.path, Path("ipsum.txt"))

        status = next(it)
        self.assertEqual(status.index, Status.DELETED)
        self.assertEqual(status.working_tree, Status.UNMODIFIED)
        self.assertEqual(status.path, Path("lorem.json"))

        with self.assertRaises(StopIteration):
            next(it)
