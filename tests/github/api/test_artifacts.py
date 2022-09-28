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

# pylint: disable=too-many-lines

import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import httpx

from pontos.github.api import GitHubRESTApi
from pontos.helper import DEFAULT_TIMEOUT
from tests.github.api import default_request

here = Path(__file__).parent


class GitHubArtifactsTestCase(unittest.TestCase):
    @patch("pontos.github.api.api.httpx.get")
    def test_get_repository_artifacts(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "artifacts": [
                {
                    "id": 11,
                    "node_id": "MDg6QXJ0aWZhY3QxMQ==",
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_repository_artifacts("foo/bar")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts",
            params={"per_page": 100, "page": 1},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_repository_artifacts_with_pagination(
        self, requests_mock: MagicMock
    ):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "artifacts": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "artifacts": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(100, 120)
                ],
            },
        ]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_repository_artifacts("foo/bar")

        args1, kwargs1 = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts",
            params={"per_page": 100, "page": 1},
        )
        args2, kwargs2 = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts",
            params={"per_page": 100, "page": 2},
        )
        requests_mock.assert_has_calls(
            [
                call.__bool__(),
                call(*args1, **kwargs1),
                call().raise_for_status(),
                call().json(),
                call.__bool__(),
                call(*args2, **kwargs2),
                call().raise_for_status(),
                call().json(),
            ]
        )

        self.assertEqual(len(artifacts), 120)
        self.assertEqual(artifacts[0]["name"], "Foo-0")
        self.assertEqual(artifacts[119]["name"], "Foo-119")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_repository_artifact(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.json.return_value = {
            "id": 123,
            "name": "Foo",
        }

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_repository_artifact("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(artifacts["id"], 123)
        self.assertEqual(artifacts["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_repository_artifact_invalid(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Testing Status Message", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.get_repository_artifact("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.helper.Path")
    @patch("pontos.github.api.api.httpx.stream")
    def test_download_repository_artifact(
        self, requests_mock: MagicMock, path_mock: MagicMock
    ):
        response = MagicMock()
        response.iter_bytes.return_value = [b"foo", b"bar", b"baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = None
        response_stream = MagicMock()
        response_stream.__enter__.return_value = response
        requests_mock.return_value = response_stream

        api = GitHubRESTApi("12345")
        download_file = path_mock()
        with api.download_repository_artifact(
            "foo/bar", "123", download_file
        ) as download_progress:
            args, kwargs = default_request(
                "GET",
                "https://api.github.com/repos/foo/bar/actions/artifacts/123/zip",  # pylint: disable=line-too-long
                timeout=DEFAULT_TIMEOUT,
            )
            requests_mock.assert_called_once_with(*args, **kwargs)
            response_headers.get.assert_called_once_with("content-length")

            self.assertIsNone(download_progress.length)

            it = iter(download_progress)
            progress = next(it)
            self.assertIsNone(progress)
            progress = next(it)
            self.assertIsNone(progress)
            progress = next(it)
            self.assertIsNone(progress)

            with self.assertRaises(StopIteration):
                next(it)

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_run_artifacts(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "artifacts": [
                {
                    "id": 11,
                    "node_id": "MDg6QXJ0aWZhY3QxMQ==",
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_run_artifacts("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs/123/artifacts",
            params={"per_page": 100, "page": 1},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_run_artifacts_with_pagination(
        self, requests_mock: MagicMock
    ):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "artifacts": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "artifacts": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(100, 120)
                ],
            },
        ]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_run_artifacts("foo/bar", "123")

        args1, kwargs1 = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs/123/artifacts",
            params={"per_page": 100, "page": 1},
        )
        args2, kwargs2 = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs/123/artifacts",
            params={"per_page": 100, "page": 2},
        )
        requests_mock.assert_has_calls(
            [
                call.__bool__(),
                call(*args1, **kwargs1),
                call().raise_for_status(),
                call().json(),
                call.__bool__(),
                call(*args2, **kwargs2),
                call().raise_for_status(),
                call().json(),
            ]
        )

        self.assertEqual(len(artifacts), 120)
        self.assertEqual(artifacts[0]["name"], "Foo-0")
        self.assertEqual(artifacts[119]["name"], "Foo-119")

    @patch("pontos.github.api.api.httpx.delete")
    def test_delete_repository_artifact(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.delete_repository_artifact("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.delete")
    def test_delete_repository_artifact_failure(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Delete Failed", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.delete_repository_artifact("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
