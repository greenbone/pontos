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
from pontos.github.api.workflows import GitHubAsyncRESTWorkflows
from tests import AsyncIteratorMock
from tests.github.api import (
    GitHubAsyncRESTTestCase,
    create_response,
    default_request,
)

here = Path(__file__).parent


class GitHubAsyncRESTWorkflowsTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTWorkflows

    async def test_get(self):
        response = create_response()
        self.client.get.return_value = response

        await self.api.get("foo/bar", "ci.yml")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/actions/workflows/ci.yml"
        )

    async def test_get_failure(self):
        response = create_response()
        self.client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.get("foo/bar", "ci.yml")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/actions/workflows/ci.yml"
        )

    async def test_get_all(self):
        response1 = create_response()
        response1.json.return_value = {"workflows": [{"id": 1}]}
        response2 = create_response()
        response2.json.return_value = {"workflows": [{"id": 2}, {"id": 3}]}

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        workflows = await self.api.get_all("foo/bar")

        self.assertEqual(len(workflows), 3)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/actions/workflows",
            params={"per_page": "100"},
        )

    async def test_get_workflow_runs(self):
        response1 = create_response()
        response1.json.return_value = {"workflow_runs": [{"id": 1}]}
        response2 = create_response()
        response2.json.return_value = {"workflow_runs": [{"id": 2}, {"id": 3}]}

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        runs = await self.api.get_workflow_runs(
            "foo/bar", actor="foo", branch="stable", exclude_pull_requests=True
        )

        self.assertEqual(len(runs), 3)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/actions/runs",
            params={
                "actor": "foo",
                "branch": "stable",
                "exclude_pull_requests": True,
                "per_page": "100",
            },
        )

    async def test_get_workflow_runs_for_workflow(self):
        response1 = create_response()
        response1.json.return_value = {"workflow_runs": [{"id": 1}]}
        response2 = create_response()
        response2.json.return_value = {"workflow_runs": [{"id": 2}, {"id": 3}]}

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        runs = await self.api.get_workflow_runs(
            "foo/bar",
            "ci.yml",
            actor="foo",
            branch="stable",
            exclude_pull_requests=True,
        )

        self.assertEqual(len(runs), 3)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/actions/workflows/ci.yml/runs",
            params={
                "actor": "foo",
                "branch": "stable",
                "exclude_pull_requests": True,
                "per_page": "100",
            },
        )

    async def test_get_workflow_run(self):
        response = create_response()
        self.client.get.return_value = response

        await self.api.get_workflow_run("foo/bar", "123")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/actions/runs/123"
        )

    async def test_get_workflow_run_failure(self):
        response = create_response()
        self.client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.get_workflow_run("foo/bar", "123")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/actions/runs/123"
        )

    async def test_create_workflow_dispatch(self):
        response = create_response()
        self.client.post.return_value = response

        input_dict = {"foo": "bar"}

        await self.api.create_workflow_dispatch(
            "foo/bar", "ci.yml", ref="stable", inputs=input_dict
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/actions/workflows/ci.yml/dispatches",
            data={"ref": "stable", "inputs": input_dict},
        )

    async def test_create_workflow_dispatch_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        input_dict = {"foo": "bar"}

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.create_workflow_dispatch(
                "foo/bar", "ci.yml", ref="stable", inputs=input_dict
            )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/actions/workflows/ci.yml/dispatches",
            data={"ref": "stable", "inputs": input_dict},
        )


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
