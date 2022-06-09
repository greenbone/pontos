# Copyright (C) 2021-2022 Greenbone Networks GmbH
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
