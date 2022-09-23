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

import os
from pathlib import Path
from typing import Optional


class GitHubEnvironment:
    """
    Class to handle values from the GitHub Environment

    https://docs.github.com/en/actions/learn-github-actions/environment-variables
    """

    @property
    def workspace(self) -> Optional[Path]:
        workspace = os.environ.get("GITHUB_WORKSPACE")
        return Path(workspace) if workspace else None

    @property
    def repository(self) -> Optional[str]:
        return os.environ.get("GITHUB_REPOSITORY")

    @property
    def sha(self) -> Optional[str]:
        return os.environ.get("GITHUB_SHA")

    @property
    def ref(self) -> Optional[str]:
        return os.environ.get("GITHUB_REF")

    @property
    def ref_name(self) -> Optional[str]:
        return os.environ.get("GITHUB_REF_NAME")

    @property
    def event_path(self) -> Optional[Path]:
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        return Path(event_path) if event_path else None

    @property
    def head_ref(self) -> Optional[str]:
        return os.environ.get("GITHUB_HEAD_REF")

    @property
    def base_ref(self) -> Optional[str]:
        return os.environ.get("GITHUB_BASE_REF")

    @property
    def api_url(self) -> Optional[str]:
        return os.environ.get("GITHUB_API_URL")

    @property
    def actor(self) -> Optional[str]:
        return os.environ.get("GITHUB_ACTOR")

    @property
    def run_id(self) -> Optional[str]:
        return os.environ.get("GITHUB_RUN_ID")

    @property
    def action_id(self) -> Optional[str]:
        return os.environ.get("GITHUB_ACTION")

    @property
    def is_debug(self) -> bool:
        return os.environ.get("RUNNER_DEBUG") == "1"
