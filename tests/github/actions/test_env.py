# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest
from pathlib import Path
from unittest.mock import patch

from pontos.github.actions.env import GitHubEnvironment


class GitHubEnvironmentTestCase(unittest.TestCase):
    @patch.dict("os.environ", {"GITHUB_WORKSPACE": "/foo/bar"}, clear=True)
    def test_workspace(self):
        env = GitHubEnvironment()
        self.assertEqual(env.workspace, Path("/foo/bar"))

    @patch.dict("os.environ", {"GITHUB_REPOSITORY": "foo/bar"}, clear=True)
    def test_repository(self):
        env = GitHubEnvironment()
        self.assertEqual(env.repository, "foo/bar")

    @patch.dict("os.environ", {"GITHUB_SHA": "123456"}, clear=True)
    def test_sha(self):
        env = GitHubEnvironment()
        self.assertEqual(env.sha, "123456")

    @patch.dict("os.environ", {"GITHUB_REF": "ref/branches/main"}, clear=True)
    def test_ref(self):
        env = GitHubEnvironment()
        self.assertEqual(env.ref, "ref/branches/main")

    @patch.dict("os.environ", {"GITHUB_REF_NAME": "main"}, clear=True)
    def test_ref_name(self):
        env = GitHubEnvironment()
        self.assertEqual(env.ref_name, "main")

    @patch.dict("os.environ", {"GITHUB_EVENT_PATH": "/foo/bar"}, clear=True)
    def test_event_path(self):
        env = GitHubEnvironment()
        self.assertEqual(env.event_path, Path("/foo/bar"))

    @patch.dict("os.environ", {"GITHUB_HEAD_REF": "foo"}, clear=True)
    def test_head_ref(self):
        env = GitHubEnvironment()
        self.assertEqual(env.head_ref, "foo")

    @patch.dict("os.environ", {"GITHUB_BASE_REF": "main"}, clear=True)
    def test_base_ref(self):
        env = GitHubEnvironment()
        self.assertEqual(env.base_ref, "main")

    @patch.dict(
        "os.environ", {"GITHUB_API_URL": "https://api.github.com"}, clear=True
    )
    def test_api_url(self):
        env = GitHubEnvironment()
        self.assertEqual(env.api_url, "https://api.github.com")

    @patch.dict("os.environ", {"GITHUB_ACTOR": "greenbonebot"}, clear=True)
    def test_actor(self):
        env = GitHubEnvironment()
        self.assertEqual(env.actor, "greenbonebot")

    @patch.dict("os.environ", {"GITHUB_RUN_ID": "12345"}, clear=True)
    def test_run_id(self):
        env = GitHubEnvironment()
        self.assertEqual(env.run_id, "12345")

    @patch.dict("os.environ", {"GITHUB_ACTION": "54321"}, clear=True)
    def test_action_id(self):
        env = GitHubEnvironment()
        self.assertEqual(env.action_id, "54321")

    @patch.dict("os.environ", {"RUNNER_DEBUG": "1"}, clear=True)
    def test_is_debug_enabled(self):
        env = GitHubEnvironment()
        self.assertTrue(env.is_debug)

    @patch.dict("os.environ", {"RUNNER_DEBUG": ""}, clear=True)
    def test_is_debug_disabled(self):
        env = GitHubEnvironment()
        self.assertFalse(env.is_debug)
