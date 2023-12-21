# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=line-too-long

import unittest
from datetime import datetime, timezone

from pontos.github.models.artifact import Artifact


class ArtifactTestCase(unittest.TestCase):
    def test_from_dict(self):
        artifact = Artifact.from_dict(
            {
                "id": 1,
                "node_id": "MDg6QXJ0aWZhY3QxMQ==",
                "name": "Rails",
                "size_in_bytes": 556,
                "url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/11",
                "archive_download_url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/11/zip",
                "expired": False,
                "created_at": "2020-01-10T14:59:22Z",
                "expires_at": "2020-03-21T14:59:22Z",
                "updated_at": "2020-02-21T14:59:22Z",
                "workflow_run": {
                    "id": 1,
                    "repository_id": 2,
                    "head_repository_id": 3,
                    "head_branch": "main",
                    "head_sha": "328faa0536e6fef19753d9d91dc96a9931694ce3",
                },
            }
        )

        self.assertEqual(artifact.id, 1)
        self.assertEqual(artifact.node_id, "MDg6QXJ0aWZhY3QxMQ==")
        self.assertEqual(artifact.name, "Rails")
        self.assertEqual(artifact.size_in_bytes, 556)
        self.assertEqual(
            artifact.url,
            "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/11",
        )
        self.assertEqual(
            artifact.archive_download_url,
            "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/11/zip",
        )
        self.assertFalse(artifact.expired)
        self.assertEqual(
            artifact.created_at,
            datetime(2020, 1, 10, 14, 59, 22, tzinfo=timezone.utc),
        )
        self.assertEqual(
            artifact.expires_at,
            datetime(2020, 3, 21, 14, 59, 22, tzinfo=timezone.utc),
        )
        self.assertEqual(
            artifact.updated_at,
            datetime(2020, 2, 21, 14, 59, 22, tzinfo=timezone.utc),
        )

        workflow_run = artifact.workflow_run
        self.assertEqual(workflow_run.id, 1)
        self.assertEqual(workflow_run.repository_id, 2)
        self.assertEqual(workflow_run.head_repository_id, 3)
        self.assertEqual(workflow_run.head_branch, "main")
        self.assertEqual(
            workflow_run.head_sha, "328faa0536e6fef19753d9d91dc96a9931694ce3"
        )
