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
from tests.github.api import default_request

here = Path(__file__).parent


class GitHubWorkflowsTestCase(unittest.TestCase):
    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflows(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflows": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflows("foo/bar")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows",
            params={"per_page": 100, "page": 1},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflows_with_pagination(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "workflows": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "workflows": [
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
        artifacts = api.get_workflows("foo/bar")

        args1, kwargs1 = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows",
            params={"per_page": 100, "page": 1},
        )
        args2, kwargs2 = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows",
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
    def test_get_workflow(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.json.return_value = {
            "id": 123,
            "name": "Foo",
        }

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(artifacts["id"], 123)
        self.assertEqual(artifacts["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_invalid(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Testing Status Message", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.get_workflow("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    def test_create_workflow_dispatch(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_workflow_dispatch("foo/bar", "123", ref="main")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows/123"
            "/dispatches",
            json={"ref": "main"},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    def test_create_workflow_dispatch_failure(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Dispatch Failed", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.create_workflow_dispatch("foo/bar", "123", ref="main")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows/123"
            "/dispatches",
            json={"ref": "main"},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_runs(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflow_runs": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_runs("foo/bar")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs",
            params={"per_page": 100, "page": 1},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_runs_with_pagination(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "workflow_runs": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "workflow_runs": [
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
        artifacts = api.get_workflow_runs("foo/bar")

        args1, kwargs1 = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs",
            params={"per_page": 100, "page": 1},
        )
        args2, kwargs2 = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs",
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
    def test_get_workflow_runs_with_params(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflow_runs": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_runs(
            "foo/bar",
            actor="Foo",
            branch="main",
            event="workflow_dispatch",
            status="completed",
            created=">=2022-09-01",
            exclude_pull_requests=True,
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs",
            params={
                "per_page": 100,
                "page": 1,
                "actor": "Foo",
                "branch": "main",
                "event": "workflow_dispatch",
                "status": "completed",
                "created": ">=2022-09-01",
                "exclude_pull_requests": True,
            },
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_runs_for_workflow(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflow_runs": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_runs("foo/bar", "foo")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows/foo/runs",
            params={"per_page": 100, "page": 1},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_run(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.json.return_value = {
            "id": 123,
            "name": "Foo",
        }

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_run("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(artifacts["id"], 123)
        self.assertEqual(artifacts["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_run_invalid(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Workflow Run Not Found", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.get_workflow_run("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
