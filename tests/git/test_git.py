# Copyright (C) 2022 Greenbone Networks GmbH
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
from unittest.mock import patch

from pontos.git import Git
from pontos.git.git import ConfigScope, MergeStrategy, TagSort


class GitTestCase(unittest.TestCase):
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
            "tag", "-l", "--sort=version:refname", cwd=None
        )

        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0], "v1.0")
        self.assertEqual(tags[1], "v2.0")
        self.assertEqual(tags[2], "v2.1")

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
"""

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
