# SPDX-FileCopyrightText: 2021-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


class PullRequestState(Enum):
    """
    State of a pull request

    Attributes:
        OPEN: The pull request is open
        CLOSED: The pull request is closed
    """

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

    Attributes:
        name: Name of the git branch reference for example main
        sha: Git commit ID of the reference
    """

    name: str
    sha: str


@dataclass
class GitHubPullRequestEvent:
    """
    Event data of a GitHub Pull Request

    https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#pull_request

    Attributes:
        draft: True if the pull request is a draft
        number: ID of the pull request
        labels: Labels attached to the pull request
        title: Title of the pull request
        merged: True if the pull request is already merged
        state: State of the pull request (open, closed)
        base: Base reference of the pull request (target branch)
        head: Head reference of the pull request (source branch)
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
        """
        Derive the pull request information from the pull request data of a
        GitHub event.

        Args:
            pull_request_data: JSON based pull request information as dict
        """
        data = pull_request_data or {}

        self.draft = data.get("draft")
        self.number = data.get("number")
        self.labels = [Label(label.get("name")) for label in data.get("labels")]  # type: ignore #pylint: disable=line-too-long # noqa: E501
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

    Attributes:
        pull_request: Information about the pull request
    """

    pull_request: GitHubPullRequestEvent

    def __init__(self, event_path: Path):
        """
        Loads the event data from the passed path

        Args:
            event_path: Path to the event data
        """
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
