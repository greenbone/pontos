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

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pontos.github.models.base import GitHubModel

__all__ = ("Artifact",)


@dataclass
class ArtifactWorkflowRun(GitHubModel):
    id: int
    repository_id: int
    head_repository_id: int
    head_branch: str
    head_sha: str


@dataclass
class Artifact(GitHubModel):
    id: int
    node_id: str
    name: str
    size_in_bytes: int
    url: str
    archive_download_url: str
    expired: bool
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    workflow_run: Optional[ArtifactWorkflowRun] = None
