# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pontos.github.models.base import GitHubModel

__all__ = (
    "Artifact",
    "ArtifactWorkflowRun",
)


@dataclass
class ArtifactWorkflowRun(GitHubModel):
    """
    The workflow run that uploaded the artifact

    Attributes:
        id: ID of the workflow run
        repository_id: ID of the corresponding repository
        head_repository_id:
        head_branch: Corresponding branch name
        head_sha: Commit ID of the head of the corresponding branch
    """

    id: int
    repository_id: int
    head_repository_id: int
    head_branch: str
    head_sha: str


@dataclass
class Artifact(GitHubModel):
    """
    A GitHub Artifact model

    Attributes:
        id: ID of the artifact
        node_id: Node ID of the artifact
        name: Name of the artifact
        size_in_bytes: The size (in bytes) of the artifact
        url: REST API URL of the artifact
        archive_download_url: URL to download the artifact
        expired: True if the artifact has expired
        created_at: Creation date of the artifact
        expires_at: Expiration date of the artifact
        update_at: Last modification date of the artifact
        workflow_run: Corresponding GitHub workflow run
    """

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
