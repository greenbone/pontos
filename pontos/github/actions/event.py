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

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


class PullRequestState(Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Label:
    """
    A label of a pull request or issue
    """

    name: str


@dataclass
class Ref:
    """
    A git branch reference
    """

    name: str
    sha: str


@dataclass
class GitHubPullRequestEvent:
    """
    Event data of a GitHub Pull Request

    https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#pull_request
    """

    draft: Optional[bool]
    number: Optional[int]
    labels: Optional[Iterable[str]]
    title: Optional[str]
    merged: Optional[bool]
    state: PullRequestState
    base: Ref
    head: Ref

    def __init__(self, pull_request_data: Dict[str, Any]):
        data = pull_request_data or {}

        self.draft = data.get("draft")
        self.number = data.get("number")
        self.labels = [Label(label.get("name")) for label in data.get("labels")]  # type: ignore #pylint: disable=line-too-long
        self.title = data.get("title")
        self.merged = data.get("merged")
        self.state = PullRequestState(data.get("state"))

        base = data.get("base") or {}
        self.base = Ref(base.get("ref"), base.get("sha"))  # type: ignore

        head = data.get("head") or {}
        self.head = Ref(head.get("ref"), head.get("sha"))  # type: ignore


@dataclass
class GitHubEvent:
    """
    GitHub Actions provides event data for the running action as JSON data in
    a local file at the runner.

    The JSON data for the events is specified at
    https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads
    """

    pull_request: GitHubPullRequestEvent

    def __init__(self, event_path: Path):
        content = event_path.read_text(encoding="utf-8")
        self._event_data = json.loads(content) if content else {}
        pull_request_data = self._event_data.get("pull_request")
        self.pull_request = (
            GitHubPullRequestEvent(pull_request_data)  # type: ignore
            if pull_request_data
            else None
        )

    def __str__(self) -> str:
        return json.dumps(self._event_data, indent=2)
