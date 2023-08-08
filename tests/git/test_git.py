# Copyright (C) 2022 Greenbone AG
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
from pathlib import Path
from unittest.mock import MagicMock, patch

from pontos.git import Git
from pontos.git.git import (
    DEFAULT_TAG_SORT_SUFFIX,
    ConfigScope,
    GitError,
    MergeStrategy,
    TagSort,
)
from pontos.git.status import Status
from pontos.testing import temp_directory, temp_git_repository


class GitTestCase(unittest.TestCase):
    @patch("pontos.git.git.exec_git")
    def test_exec(self, exec_git_mock):
        git = Git()
        git.exec("foo", "bar", "baz")

        exec_git_mock.assert_called_once_with("foo", "bar", "baz", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_clone(self, exec_git_mock):
        git = Git()
        git.clone("http://foo/foo.git", Path("/bar"))

        exec_git_mock.assert_called_once_with(
            "clone", "http://foo/foo.git", "/bar", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_clone_with_remote(self, exec_git_mock):
        git = Git()
        git.clone("http://foo/foo.git", Path("/bar"), remote="foo")

        exec_git_mock.assert_called_once_with(
            "clone", "-o", "foo", "http://foo/foo.git", "/bar", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_clone_with_branch(self, exec_git_mock):
        git = Git()
        git.clone("http://foo/foo.git", Path("/bar"), branch="foo")

        exec_git_mock.assert_called_once_with(
            "clone", "-b", "foo", "http://foo/foo.git", "/bar", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_clone_with_depth(self, exec_git_mock):
        git = Git()
        git.clone("http://foo/foo.git", Path("/bar"), depth=1)

        exec_git_mock.assert_called_once_with(
            "clone", "--depth", "1", "http://foo/foo.git", "/bar", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_init(self, exec_git_mock):
        git = Git()
        git.init()

        exec_git_mock.assert_called_once_with("init", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_init_bare(self, exec_git_mock):
        git = Git()
        git.init(bare=True)

        exec_git_mock.assert_called_once_with("init", "--bare", cwd=None)

    def test_cwd(self):
        git = Git()

        self.assertIsNone(git.cwd)

        new_cwd = Path("foo")
        git.cwd = new_cwd

        self.assertEqual(git.cwd, new_cwd.absolute())

    @patch("pontos.git.git.exec_git")
    def test_create_branch(self, exec_git_mock):
        git = Git()
        git.create_branch("foo")

        exec_git_mock.assert_called_once_with("checkout", "-b", "foo", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_create_branch_with_starting_point(self, exec_git_mock):
        git = Git()
        git.create_branch("foo", start_point="bar")

        exec_git_mock.assert_called_once_with(
            "checkout", "-b", "foo", "bar", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_rebase(self, exec_git_mock):
        git = Git()
        git.rebase("foo")

        exec_git_mock.assert_called_once_with("rebase", "foo", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_rebase_with_head(self, exec_git_mock):
        git = Git()
        git.rebase("foo", head="bar")

        exec_git_mock.assert_called_once_with("rebase", "foo", "bar", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_rebase_with_head_and_onto(self, exec_git_mock):
        git = Git()
        git.rebase("foo", head="bar", onto="staging")

        exec_git_mock.assert_called_once_with(
            "rebase", "--onto", "staging", "foo", "bar", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_rebase_with_octopus_strategy(self, exec_git_mock):
        git = Git()
        git.rebase("foo", strategy=MergeStrategy.OCTOPUS)

        exec_git_mock.assert_called_once_with(
            "rebase", "--strategy", "octopus", "foo", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_rebase_with_ort_ours_strategy(self, exec_git_mock):
        git = Git()
        git.rebase("foo", strategy=MergeStrategy.ORT_OURS)

        exec_git_mock.assert_called_once_with(
            "rebase", "--strategy", "ort", "-X", "ours", "foo", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_push(self, exec_git_mock):
        git = Git()
        git.push()

        exec_git_mock.assert_called_once_with("push", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_push_with_remote(self, exec_git_mock):
        git = Git()
        git.push(remote="foo")

        exec_git_mock.assert_called_once_with("push", "foo", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_push_with_remote_and_branch(self, exec_git_mock):
        git = Git()
        git.push(remote="foo", branch="bar")

        exec_git_mock.assert_called_once_with("push", "foo", "bar", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_push_with_follow_tags(self, exec_git_mock):
        git = Git()
        git.push(follow_tags=True)

        exec_git_mock.assert_called_once_with("push", "--follow-tags", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_push_with_follow_tags_false(self, exec_git_mock):
        git = Git()
        git.push(follow_tags=False)

        exec_git_mock.assert_called_once_with("push", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_push_with_force(self, exec_git_mock):
        git = Git()
        git.push(force=True)

        exec_git_mock.assert_called_once_with("push", "--force", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_push_with_force_false(self, exec_git_mock):
        git = Git()
        git.push(force=False)

        exec_git_mock.assert_called_once_with("push", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_config_get(self, exec_git_mock):
        git = Git()
        git.config("foo")

        exec_git_mock.assert_called_once_with("config", "foo", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_config_set(self, exec_git_mock):
        git = Git()
        git.config("foo", "bar")

        exec_git_mock.assert_called_once_with("config", "foo", "bar", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_config_get_local_scope(self, exec_git_mock):
        git = Git()
        git.config("foo", scope=ConfigScope.LOCAL)

        exec_git_mock.assert_called_once_with(
            "config", "--local", "foo", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_config_get_system_scope(self, exec_git_mock):
        git = Git()
        git.config("foo", scope=ConfigScope.SYSTEM)

        exec_git_mock.assert_called_once_with(
            "config", "--system", "foo", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_config_get_global_scope(self, exec_git_mock):
        git = Git()
        git.config("foo", scope=ConfigScope.GLOBAL)

        exec_git_mock.assert_called_once_with(
            "config", "--global", "foo", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_config_get_worktree_scope(self, exec_git_mock):
        git = Git()
        git.config("foo", scope=ConfigScope.WORKTREE)

        exec_git_mock.assert_called_once_with(
            "config", "--worktree", "foo", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_cherry_pick(self, exec_git_mock):
        git = Git()
        git.cherry_pick(["foo", "bar"])

        exec_git_mock.assert_called_once_with(
            "cherry-pick", "foo", "bar", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_cherry_pick_single_commit(self, exec_git_mock):
        git = Git()
        git.cherry_pick("foo")

        exec_git_mock.assert_called_once_with("cherry-pick", "foo", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_list_tags(self, exec_git_mock):
        exec_git_mock.return_value = "v1.0\nv2.0\nv2.1\n"
        git = Git()
        tags = git.list_tags()

        exec_git_mock.assert_called_once_with("tag", "-l", cwd=None)

        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0], "v1.0")
        self.assertEqual(tags[1], "v2.0")
        self.assertEqual(tags[2], "v2.1")

    @patch("pontos.git.git.exec_git")
    def test_list_tags_with_version_sort(self, exec_git_mock):
        exec_git_mock.return_value = "v1.0\nv2.0\nv2.1\n"
        git = Git()
        tags = git.list_tags(sort=TagSort.VERSION)

        exec_git_mock.assert_called_once_with(
            "tag",
            "-l",
            "--sort=version:refname",
            cwd=None,
        )

        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0], "v1.0")
        self.assertEqual(tags[1], "v2.0")
        self.assertEqual(tags[2], "v2.1")

    @patch("pontos.git.git.exec_git")
    def test_list_tags_with_version_suffix_sort(self, exec_git_mock):
        exec_git_mock.return_value = "v1.0\nv2.0\nv2.1\n"
        git = Git()
        tags = git.list_tags(
            sort=TagSort.VERSION, sort_suffix=DEFAULT_TAG_SORT_SUFFIX
        )

        exec_git_mock.assert_called_once_with(
            "-c",
            "versionsort.suffix=-alpha",
            "-c",
            "versionsort.suffix=a",
            "-c",
            "versionsort.suffix=-beta",
            "-c",
            "versionsort.suffix=b",
            "-c",
            "versionsort.suffix=-rc",
            "-c",
            "versionsort.suffix=rc",
            "tag",
            "-l",
            "--sort=version:refname",
            cwd=None,
        )

        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0], "v1.0")
        self.assertEqual(tags[1], "v2.0")
        self.assertEqual(tags[2], "v2.1")

    @patch("pontos.git.git.exec_git")
    def test_list_tags_with_tag_name(self, exec_git_mock):
        exec_git_mock.return_value = "v2.0\nv2.1\n"
        git = Git()
        tags = git.list_tags(tag_name="v2.*")

        exec_git_mock.assert_called_once_with("tag", "-l", "v2.*", cwd=None)

        self.assertEqual(len(tags), 2)
        self.assertEqual(tags[0], "v2.0")
        self.assertEqual(tags[1], "v2.1")

    @patch("pontos.git.git.exec_git")
    def test_add_single_file(self, exec_git_mock):
        git = Git()
        git.add("foo")

        exec_git_mock.assert_called_once_with("add", "foo", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_add(self, exec_git_mock):
        git = Git()
        git.add(["foo", "bar"])

        exec_git_mock.assert_called_once_with("add", "foo", "bar", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_commit(self, exec_git_mock):
        git = Git()
        git.commit("Add foo")

        exec_git_mock.assert_called_once_with(
            "commit", "-m", "Add foo", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_commit_with_signing_key(self, exec_git_mock):
        git = Git()
        git.commit(
            "Add foo",
            gpg_signing_key="8AE4BE429B60A59B311C2E739823FAA60ED1E580",
        )

        exec_git_mock.assert_called_once_with(
            "commit",
            "-S8AE4BE429B60A59B311C2E739823FAA60ED1E580",
            "-m",
            "Add foo",
            cwd=None,
        )

    @patch("pontos.git.git.exec_git")
    def test_commit_without_verify(self, exec_git_mock):
        git = Git()
        git.commit("Add foo", verify=False)

        exec_git_mock.assert_called_once_with(
            "commit", "--no-verify", "-m", "Add foo", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_commit_without_gpg_sign(self, exec_git_mock):
        git = Git()
        git.commit("Add foo", gpg_sign=False)

        exec_git_mock.assert_called_once_with(
            "commit", "--no-gpg-sign", "-m", "Add foo", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_tag(self, exec_git_mock):
        git = Git()
        git.tag(tag="test")

        exec_git_mock.assert_called_once_with("tag", "test", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_tag_with_gpg_key(self, exec_git_mock):
        git = Git()
        git.tag("test", gpg_key_id="0x123")

        exec_git_mock.assert_called_once_with(
            "tag", "-u", "0x123", "test", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_tag_with_message(self, exec_git_mock):
        git = Git()
        git.tag("test", message="Tag for 123 release")

        exec_git_mock.assert_called_once_with(
            "tag", "-m", "Tag for 123 release", "test", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_tag_with_force(self, exec_git_mock):
        git = Git()
        git.tag("test", force=True)

        exec_git_mock.assert_called_once_with(
            "tag", "--force", "test", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_tag_without_sign(self, exec_git_mock):
        git = Git()
        git.tag("test", sign=False)

        exec_git_mock.assert_called_once_with(
            "tag", "--no-sign", "test", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_fetch(self, exec_git_mock):
        git = Git()
        git.fetch()

        exec_git_mock.assert_called_once_with("fetch", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_fetch_with_remote(self, exec_git_mock):
        git = Git()
        git.fetch("foo")

        exec_git_mock.assert_called_once_with("fetch", "foo", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_fetch_with_remote_and_refspec(self, exec_git_mock):
        git = Git()
        git.fetch("foo", "my-branch")

        exec_git_mock.assert_called_once_with(
            "fetch", "foo", "my-branch", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_fetch_with_verbose(self, exec_git_mock):
        git = Git()
        git.fetch(verbose=True)

        exec_git_mock.assert_called_once_with("fetch", "-v", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_add_remote(self, exec_git_mock):
        git = Git()
        git.add_remote("foo", "https://foo.bar/foo.git")

        exec_git_mock.assert_called_once_with(
            "remote", "add", "foo", "https://foo.bar/foo.git", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_checkout(self, exec_git_mock):
        git = Git()
        git.checkout("foo")

        exec_git_mock.assert_called_once_with("checkout", "foo", cwd=None)

    @patch("pontos.git.git.exec_git")
    def test_checkout_with_start_point(self, exec_git_mock):
        git = Git()
        git.checkout("foo", start_point="bar")

        exec_git_mock.assert_called_once_with(
            "checkout", "-b", "foo", "bar", cwd=None
        )

    @patch("pontos.git.git.exec_git")
    def test_remote_url(self, exec_git_mock):
        url = "git@github.com:foo/foo.git"
        exec_git_mock.return_value = url

        git = Git()
        remote = git.remote_url("foo")

        exec_git_mock.assert_called_once_with(
            "remote", "get-url", "foo", cwd=None
        )

        self.assertEqual(remote, url)

    @patch("pontos.git.git.exec_git")
    def test_remote_url_with_default(self, exec_git_mock):
        url = "git@github.com:foo/foo.git"
        exec_git_mock.return_value = url

        git = Git()
        remote = git.remote_url()

        exec_git_mock.assert_called_once_with(
            "remote", "get-url", "origin", cwd=None
        )

        self.assertEqual(remote, url)

    @patch("pontos.git.git.exec_git")
    def test_log(self, exec_git_mock):
        # pylint: disable=line-too-long
        exec_git_mock.return_value = """commit 68c6c3785bbb049df63dc51f8b5b709eb19f8517
Author: Björn Ricks <bjoern.ricks@greenbone.net>
Date:   Wed Apr 8 15:16:05 2020 +0200

    Add a draft for a README.md document

commit 464f24d43d7293091b168c6b37ee37978a650958
Author: Björn Ricks <bjoern.ricks@greenbone.net>
Date:   Wed Apr 8 14:28:53 2020 +0200

    Initial commit
"""  # noqa: E501

        git = Git()
        logs = git.log()

        exec_git_mock.assert_called_once_with("log", cwd=None)

        self.assertEqual(
            logs[0], "commit 68c6c3785bbb049df63dc51f8b5b709eb19f8517"
        )
        self.assertEqual(
            logs[6], "commit 464f24d43d7293091b168c6b37ee37978a650958"
        )

    @patch("pontos.git.git.exec_git")
    def test_log_with_oneline(self, exec_git_mock):
        exec_git_mock.return_value = """50f9963 Add CircleCI config for pontos
9a8feaa Rename to pontos only
047cfae Update README for installation and development
e6ea80d Update README
68c6c37 Add a draft for a README.md document
464f24d Initial commit"""

        git = Git()
        logs = git.log(oneline=True)

        exec_git_mock.assert_called_once_with("log", "--oneline", cwd=None)

        self.assertEqual(logs[0], "50f9963 Add CircleCI config for pontos")
        self.assertEqual(logs[5], "464f24d Initial commit")

    @patch("pontos.git.git.exec_git")
    def test_log_with_format(self, exec_git_mock):
        exec_git_mock.return_value = """Add CircleCI config for pontos
Rename to pontos only
Update README for installation and development
Update README
Add a draft for a README.md document
Initial commit"""

        git = Git()
        logs = git.log(format="format:%s")

        exec_git_mock.assert_called_once_with(
            "log", "--format=format:%s", cwd=None
        )

        self.assertEqual(logs[0], "Add CircleCI config for pontos")
        self.assertEqual(logs[5], "Initial commit")

    @patch("pontos.git.git.exec_git")
    def test_rev_list(self, exec_git_mock):
        git = Git()
        git.rev_list("foo", "bar", "baz", max_parents=123, abbrev_commit=True)

        exec_git_mock.assert_called_once_with(
            "rev-list",
            "--max-parents=123",
            "--abbrev-commit",
            "foo",
            "bar",
            "baz",
            cwd=None,
        )

    @patch("pontos.git.git.exec_git")
    def test_move(self, exec_git_mock):
        git = Git()
        git.move("foo", "bar")

        exec_git_mock.assert_called_once_with(
            "mv",
            "foo",
            "bar",
            cwd=None,
        )

    @patch("pontos.git.git.exec_git")
    def test_remove(self, exec_git_mock):
        git = Git()
        git.remove("foo")

        exec_git_mock.assert_called_once_with(
            "rm",
            "foo",
            cwd=None,
        )

    @patch("pontos.git.git.exec_git")
    def test_status(self, exec_git_mock):
        git = Git()
        git.status()

        exec_git_mock.assert_called_once_with(
            "status",
            "-z",
            "--ignore-submodules",
            "--untracked-files=no",
            cwd=None,
        )

    @patch("pontos.git.git.exec_git")
    def test_status_with_files(self, exec_git_mock):
        git = Git()
        git.status(["foo", "bar", "baz"])

        exec_git_mock.assert_called_once_with(
            "status",
            "-z",
            "--ignore-submodules",
            "--untracked-files=no",
            "--",
            "foo",
            "bar",
            "baz",
            cwd=None,
        )

    @patch("pontos.git.git.exec_git")
    def test_version(self, exec_git_mock: MagicMock):
        exec_git_mock.return_value = "git version 1.2.3"
        git = Git()
        self.assertEqual(git.version, "1.2.3")

    def test_version_runs(self):
        """Getting the git version should not raise an error"""
        git = Git()
        git.version

    @patch("pontos.git.git.exec_git")
    def test_show_with_online_and_objects(self, exec_git_mock: MagicMock):
        exec_git_mock.return_value = """9a8feaa Rename to pontos only
047cfae Update README for installation and development
"""

        git = Git()
        show = git.show(oneline=True, objects=["9a8feaa", "047cfae"])

        exec_git_mock.assert_called_once_with(
            "show", "--oneline", "9a8feaa", "047cfae", cwd=None
        )

        self.assertEqual(show[0], "9a8feaa Rename to pontos only")
        self.assertEqual(
            show[1], "047cfae Update README for installation and development"
        )

    @patch("pontos.git.git.exec_git")
    def test_show_with_format(self, exec_git_mock: MagicMock):
        exec_git_mock.return_value = """Rename to pontos only
"""

        git = Git()
        show = git.show(format="format:%s")

        exec_git_mock.assert_called_once_with(
            "show", "--format=format:%s", cwd=None
        )

        self.assertEqual(show, "Rename to pontos only")

    @patch("pontos.git.git.exec_git")
    def test_show_with_single_object(self, exec_git_mock: MagicMock):
        content = """commit a6956fb1398cae9426e7ced0396248a90dc1ff64
Author: Björn Ricks <bjoern.ricks@greenbone.net>
Date:   Wed Jul 19 15:07:03 2023 +0200

    Add: Allow to get the git version string

diff --git a/pontos/git/git.py b/pontos/git/git.py
index a83eed8..09aed3d 100644
--- a/pontos/git/git.py
+++ b/pontos/git/git.py
@@ -168,6 +168,14 @@ class Git:
...
"""
        exec_git_mock.return_value = content

        git = Git()
        show = git.show(objects="9a8feaa")

        exec_git_mock.assert_called_once_with("show", "9a8feaa", cwd=None)

        self.assertEqual(show, content.strip())

    @patch("pontos.git.git.exec_git")
    def test_show_with_patch(self, exec_git_mock: MagicMock):
        content = """commit a6956fb1398cae9426e7ced0396248a90dc1ff64
Author: Björn Ricks <bjoern.ricks@greenbone.net>
Date:   Wed Jul 19 15:07:03 2023 +0200

    Add: Allow to get the git version string

diff --git a/pontos/git/git.py b/pontos/git/git.py
index a83eed8..09aed3d 100644
--- a/pontos/git/git.py
+++ b/pontos/git/git.py
@@ -168,6 +168,14 @@ class Git:
...
"""
        exec_git_mock.return_value = content

        git = Git()
        show = git.show(patch=True)

        exec_git_mock.assert_called_once_with("show", "--patch", cwd=None)

        self.assertEqual(show, content.strip())

    @patch("pontos.git.git.exec_git")
    def test_show_with_no_patch(self, exec_git_mock: MagicMock):
        content = """commit a6956fb1398cae9426e7ced0396248a90dc1ff64
Author: Björn Ricks <bjoern.ricks@greenbone.net>
Date:   Wed Jul 19 15:07:03 2023 +0200

    Add: Allow to get the git version string
"""
        exec_git_mock.return_value = content

        git = Git()
        show = git.show(patch=False)

        exec_git_mock.assert_called_once_with("show", "--no-patch", cwd=None)

        self.assertEqual(show, content.strip())


class GitExtendedTestCase(unittest.TestCase):
    def test_semantic_list_tags(self):
        with temp_git_repository() as tmp_git:
            tags = [
                "v0.6.5-alpha3",
                "v0.6.5-beta1",
                "v0.6.5-alpha2",
                "v0.6.5-rc1",
                "v0.6.5-alpha1",
                "v0.6.5",
                "v0.6.4",
                "v0.6.3-alpha1",
                "v1.0.0",
            ]
            git = Git(tmp_git)
            git.config("commit.gpgSign", "false", scope=ConfigScope.LOCAL)
            git.config("tag.gpgSign", "false", scope=ConfigScope.LOCAL)
            git.config("tag.sort", "refname", scope=ConfigScope.LOCAL)

            tmp_file = tmp_git / "foo.txt"
            tmp_file.touch()

            git.add(tmp_file)

            git.commit("some commit")

            for tag in tags:
                git.tag(tag)

            tags = git.list_tags()
            self.assertEqual(
                tags,
                [
                    "v0.6.3-alpha1",
                    "v0.6.4",
                    "v0.6.5",
                    "v0.6.5-alpha1",
                    "v0.6.5-alpha2",
                    "v0.6.5-alpha3",
                    "v0.6.5-beta1",
                    "v0.6.5-rc1",
                    "v1.0.0",
                ],
            )

            tags = git.list_tags(sort=TagSort.VERSION)
            self.assertEqual(
                tags,
                [
                    "v0.6.3-alpha1",
                    "v0.6.4",
                    "v0.6.5",
                    "v0.6.5-alpha1",
                    "v0.6.5-alpha2",
                    "v0.6.5-alpha3",
                    "v0.6.5-beta1",
                    "v0.6.5-rc1",
                    "v1.0.0",
                ],
            )

            tags = git.list_tags(sort=TagSort.VERSION, tag_name="v0.6*")
            self.assertEqual(
                tags,
                [
                    "v0.6.3-alpha1",
                    "v0.6.4",
                    "v0.6.5",
                    "v0.6.5-alpha1",
                    "v0.6.5-alpha2",
                    "v0.6.5-alpha3",
                    "v0.6.5-beta1",
                    "v0.6.5-rc1",
                ],
            )

            tags = git.list_tags(sort=TagSort.VERSION, tag_name="v0.6.5*")
            self.assertEqual(
                tags,
                [
                    "v0.6.5",
                    "v0.6.5-alpha1",
                    "v0.6.5-alpha2",
                    "v0.6.5-alpha3",
                    "v0.6.5-beta1",
                    "v0.6.5-rc1",
                ],
            )

            tags = git.list_tags(tag_name="v0.6.5*")
            self.assertEqual(
                tags,
                [
                    "v0.6.5",
                    "v0.6.5-alpha1",
                    "v0.6.5-alpha2",
                    "v0.6.5-alpha3",
                    "v0.6.5-beta1",
                    "v0.6.5-rc1",
                ],
            )

            tags = git.list_tags(
                sort=TagSort.VERSION, sort_suffix=DEFAULT_TAG_SORT_SUFFIX
            )
            self.assertEqual(
                tags,
                [
                    "v0.6.3-alpha1",
                    "v0.6.4",
                    "v0.6.5-alpha1",
                    "v0.6.5-alpha2",
                    "v0.6.5-alpha3",
                    "v0.6.5-beta1",
                    "v0.6.5-rc1",
                    "v0.6.5",
                    "v1.0.0",
                ],
            )

    def test_pep440_list_tags(self):
        with temp_git_repository() as tmp_git:
            tags = [
                "v0.6.5a3",
                "v0.6.5b1",
                "v0.6.5a2",
                "v0.6.5rc1",
                "v0.6.5a1",
                "v0.6.5",
                "v0.6.4",
                "v0.6.3a1",
                "v1.0.0",
            ]
            git = Git(tmp_git)
            git.config("commit.gpgSign", "false", scope=ConfigScope.LOCAL)
            git.config("tag.gpgSign", "false", scope=ConfigScope.LOCAL)
            git.config("tag.sort", "refname", scope=ConfigScope.LOCAL)

            tmp_file = tmp_git / "foo.txt"
            tmp_file.touch()

            git.add(tmp_file)

            git.commit("some commit")

            for tag in tags:
                git.tag(tag)

            tags = git.list_tags()
            self.assertEqual(
                tags,
                [
                    "v0.6.3a1",
                    "v0.6.4",
                    "v0.6.5",
                    "v0.6.5a1",
                    "v0.6.5a2",
                    "v0.6.5a3",
                    "v0.6.5b1",
                    "v0.6.5rc1",
                    "v1.0.0",
                ],
            )

            tags = git.list_tags(sort=TagSort.VERSION)
            self.assertEqual(
                tags,
                [
                    "v0.6.3a1",
                    "v0.6.4",
                    "v0.6.5",
                    "v0.6.5a1",
                    "v0.6.5a2",
                    "v0.6.5a3",
                    "v0.6.5b1",
                    "v0.6.5rc1",
                    "v1.0.0",
                ],
            )

            tags = git.list_tags(
                sort=TagSort.VERSION, sort_suffix=DEFAULT_TAG_SORT_SUFFIX
            )
            self.assertEqual(
                tags,
                [
                    "v0.6.3a1",
                    "v0.6.4",
                    "v0.6.5a1",
                    "v0.6.5a2",
                    "v0.6.5a3",
                    "v0.6.5b1",
                    "v0.6.5rc1",
                    "v0.6.5",
                    "v1.0.0",
                ],
            )

    def test_git_status(self):
        with temp_git_repository() as tmp_git:
            tracked_file = tmp_git / "foo.json"
            tracked_file.write_text("sed diam nonumy eirmod", encoding="utf8")
            changed_file = tmp_git / "bar.json"
            changed_file.touch()
            staged_changed_file = tmp_git / "ipsum.json"
            staged_changed_file.write_text("tempor invidunt ut labore")
            removed_file = tmp_git / "lorem.json"
            removed_file.write_text(
                "consetetur sadipscing elitr", encoding="utf8"
            )
            renamed_file = tmp_git / "foo.md"
            renamed_file.write_text(
                "et dolore magna aliquyam erat", encoding="utf8"
            )

            git = Git(tmp_git)
            git.config("commit.gpgSign", "false", scope=ConfigScope.LOCAL)
            git.add(
                [
                    tracked_file,
                    changed_file,
                    staged_changed_file,
                    removed_file,
                    renamed_file,
                ]
            )
            git.commit("Some commit")

            changed_file.write_text("Lorem Ipsum", encoding="utf8")
            staged_changed_file.write_text("Lorem Ipsum", encoding="utf8")

            added_file = tmp_git / "foo.txt"
            added_file.touch()

            added_modified_file = tmp_git / "ipsum.txt"
            added_modified_file.touch()

            git.add([added_file, staged_changed_file, added_modified_file])

            staged_changed_file.write_text("Dolor sit", encoding="utf8")

            added_modified_file.write_text("Lorem Ipsum", encoding="utf8")

            git.move(renamed_file, "foo.rst")
            git.remove(removed_file)

            untracked_file = tmp_git / "bar.txt"
            untracked_file.touch()

            it = git.status()

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

    def test_git_error(self):
        with temp_directory(change_into=True), self.assertRaises(
            GitError
        ) as cm:
            Git().log()

        self.assertEqual(cm.exception.returncode, 128)
        self.assertEqual(
            cm.exception.stderr,
            "fatal: not a git repository (or any of the parent directories): "
            ".git\n",
        )
        self.assertEqual(cm.exception.stdout, "")
        self.assertEqual(cm.exception.cmd, ["git", "log"])
