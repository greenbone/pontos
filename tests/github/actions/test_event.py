# SPDX-FileCopyrightText: 2021-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest
from pathlib import Path

from pontos.github.actions.event import GitHubEvent, PullRequestState

here = Path(__file__).parent


class GitHubPullRequestEventTestCase(unittest.TestCase):
    def setUp(self) -> None:
        event_path = Path(here / "test-pull-request-event.json")
        event = GitHubEvent(event_path)
        self.pull_request = event.pull_request

    def test_draft(self):
        self.assertFalse(self.pull_request.draft)

    def test_labels(self):
        self.assertEqual(len(self.pull_request.labels), 1)
        self.assertEqual(self.pull_request.labels[0].name, "enhancement")

    def test_number(self):
        self.assertEqual(self.pull_request.number, 1)

    def test_title(self):
        self.assertEqual(self.pull_request.title, "Add foo for bar")

    def test_state(self):
        self.assertEqual(self.pull_request.state, PullRequestState.OPEN)

    def test_base(self):
        base = self.pull_request.base
        self.assertEqual(base.name, "main")
        self.assertEqual(base.sha, "50c0fbe90d0c19dba08165b707e8b720d604ed5d")

    def test_head(self):
        head = self.pull_request.head
        self.assertEqual(head.name, "label-test")
        self.assertEqual(head.sha, "beeecfeee02f5a9e69c1f69dba6757df6e5c20f7")

    def test_merged(self):
        self.assertEqual(self.pull_request.merged, False)
