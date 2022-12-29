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

from typing import AsyncIterator, Dict, Iterable, Optional, Union

import httpx

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.helper import JSON_OBJECT
from pontos.github.models.base import Event
from pontos.github.models.workflow import (
    Workflow,
    WorkflowRun,
    WorkflowRunStatus,
)
from pontos.helper import enum_or_value


class GitHubAsyncRESTWorkflows(GitHubAsyncREST):
    def get_all(self, repo: str) -> AsyncIterator[Workflow]:
        """
        List all workflows of a repository

        https://docs.github.com/en/rest/actions/workflows#list-repository-workflows

        Args:
            repo: GitHub repository (owner/name) to use

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflows as an iterable of dicts
        """
        api = f"/repos/{repo}/actions/workflows"
        return self._get_paged_items(api, "workflows", Workflow)

    async def get(self, repo: str, workflow: Union[str, int]) -> Workflow:
        """
        Get the information for the given workflow

        https://docs.github.com/en/rest/actions/workflows#get-a-workflow

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: ID of the workflow or workflow file name. For example
                `main.yml`.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflows as a dict
        """
        api = f"/repos/{repo}/actions/workflows/{workflow}"
        response = await self._client.get(api)
        response.raise_for_status()
        return Workflow.from_dict(response.json())

    async def create_workflow_dispatch(
        self,
        repo: str,
        workflow: Union[str, int],
        *,
        ref: str,
        inputs: Dict[str, str] = None,
    ) -> None:
        """
        Create a workflow dispatch event to manually trigger a GitHub Actions
        workflow run.

        https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: ID of the workflow or workflow file name. For example
                `main.yml`.
            ref: The git reference for the workflow. The reference can be a
                branch or tag name.
            inputs: Input keys and values configured in the workflow file. Any
                default properties configured in the workflow file will be used
                when inputs are omitted.
        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Example:
            .. code-block:: python

            with GitHubAsyncRESTApi("...") as api:
                api.workflows.create_workflow_dispatch(
                    "foo/bar", "ci.yml", ref="main"
                )
        """
        api = f"/repos/{repo}/actions/workflows/{workflow}/dispatches"
        data = {"ref": ref}

        if inputs:
            data["inputs"] = inputs

        response = await self._client.post(api, data=data)
        response.raise_for_status()

    def get_workflow_runs(
        self,
        repo: str,
        workflow: Optional[Union[str, int]] = None,
        *,
        actor: Optional[str] = None,
        branch: Optional[str] = None,
        event: Optional[Union[Event, str]] = None,
        status: Optional[Union[WorkflowRunStatus, str]] = None,
        created: Optional[str] = None,
        exclude_pull_requests: Optional[bool] = None,
    ) -> AsyncIterator[WorkflowRun]:
        # pylint: disable=line-too-long
        """
        List all workflow runs of a repository or of a specific workflow.

        https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-repository
        https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-workflow

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: Optional ID of the workflow or workflow file name. For
                example `main.yml`.
            actor: Only return workflow runs of this user ID.
            branch: Only return workflow runs for a specific branch.
            event: Only return workflow runs triggered by the event specified.
                For example, `push`, `pull_request` or `issue`.
                For more information, see https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows.
            status: Only return workflow runs with the check run status or
                conclusion that specified. For example, a conclusion can be
                `success` or a status can be `in_progress`. Can be one of:
                `completed`, `action_required`, `cancelled`, `failure`,
                `neutral`, `skipped`, `stale`, `success`, `timed_out`,
                `in_progress`, `queued`, `requested`, `waiting`.
            created: Only returns workflow runs created within the given
                date-time range. For more information on the syntax, see
                https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax#query-for-dates
            exclude_pull_requests: If true pull requests are omitted from the
                response.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflow runs as an iterable of dicts
        """

        api = (
            f"/repos/{repo}/actions/workflows/{workflow}/runs"
            if workflow
            else f"/repos/{repo}/actions/runs"
        )
        params = {}
        if actor:
            params["actor"] = actor
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = enum_or_value(event)
        if status:
            params["status"] = enum_or_value(status)
        if created:
            params["created"] = created
        if exclude_pull_requests is not None:
            params["exclude_pull_requests"] = exclude_pull_requests

        return self._get_paged_items(
            api, "workflow_runs", WorkflowRun, params=params
        )

    async def get_workflow_run(
        self, repo: str, run: Union[str, int]
    ) -> WorkflowRun:
        """
        Get information about a single workflow run

        https://docs.github.com/en/rest/actions/workflow-runs#get-a-workflow-run

        Args:
            repo: GitHub repository (owner/name) to use
            run: The ID of the workflow run

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflow runs as a dict
        """
        api = f"/repos/{repo}/actions/runs/{run}"
        response = await self._client.get(api)
        response.raise_for_status()
        return WorkflowRun.from_dict(response.json())


class GitHubRESTWorkflowsMixin:
    def get_workflows(self, repo: str) -> Iterable[JSON_OBJECT]:
        """
        List all workflows of a repository

        Args:
            repo: GitHub repository (owner/name) to use

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflows as an iterable of dicts
        """
        api = f"/repos/{repo}/actions/workflows"
        return self._get_paged_items(api, "workflows")

    def get_workflow(self, repo: str, workflow: str) -> JSON_OBJECT:
        """
        Get the information for the given workflow

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: ID of the workflow or workflow file name. For example
                `main.yml`.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflows as a dict
        """
        api = f"/repos/{repo}/actions/workflows/{workflow}"
        response = self._request(api, request=httpx.get)
        response.raise_for_status()
        return response.json()

    def create_workflow_dispatch(
        self,
        repo: str,
        workflow: str,
        *,
        ref: str,
        inputs: Dict[str, str] = None,
    ):
        """
        Create a workflow dispatch event to manually trigger a GitHub Actions
        workflow run.

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: ID of the workflow or workflow file name. For example
                `main.yml`.
            ref: The git reference for the workflow. The reference can be a
                branch or tag name.
            inputs: Input keys and values configured in the workflow file. Any
                default properties configured in the workflow file will be used
                when inputs are omitted.
        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Example:
            .. code-block:: python

            api = GitHubRESTApi("...")
            api.create_workflow_dispatch("foo/bar", "ci.yml", ref="main")
        """
        api = f"/repos/{repo}/actions/workflows/{workflow}/dispatches"
        data = {"ref": ref}

        if inputs:
            data["inputs"] = inputs

        response = self._request(api, data=data, request=httpx.post)
        response.raise_for_status()

    def get_workflow_runs(
        self,
        repo: str,
        workflow: Optional[str] = None,
        *,
        actor: Optional[str] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[str] = None,
        created: Optional[str] = None,
        exclude_pull_requests: Optional[bool] = None,
    ) -> Iterable[JSON_OBJECT]:
        # pylint: disable=line-too-long
        """
        List all workflow runs of a repository or of a specific workflow.

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: ID of the workflow or workflow file name. For example
                `main.yml`.
            actor: Only return workflow runs of this user ID.
            branch: Only return workflow runs for a specific branch.
            event: Only returns workflows runs triggered by the event specified.
                For example, `push`, `pull_request` or `issue`.
                For more information, see https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows.
            status: Only return workflow runs with the check run status or
                conclusion that specified. For example, a conclusion can be
                `success` or a status can be `in_progress`. Can be one of:
                `completed`, `action_required`, `cancelled`, `failure`,
                `neutral`, `skipped`, `stale`, `success`, `timed_out`,
                `in_progress`, `queued`, `requested`, `waiting`.
            created: Only returns workflow runs created within the given
                date-time range. For more information on the syntax, see
                https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax#query-for-dates
            exclude_pull_requests: If true pull requests are omitted from the
                response.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflow runs as an iterable of dicts
        """

        api = (
            f"/repos/{repo}/actions/workflows/{workflow}/runs"
            if workflow
            else f"/repos/{repo}/actions/runs"
        )
        params = {}
        if actor:
            params["actor"] = actor
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status
        if created:
            params["created"] = created
        if exclude_pull_requests is not None:
            params["exclude_pull_requests"] = exclude_pull_requests

        return self._get_paged_items(api, "workflow_runs", params=params)

    def get_workflow_run(self, repo: str, run: str) -> JSON_OBJECT:
        """
        Get information about a single workflow run

        Args:
            repo: GitHub repository (owner/name) to use
            run: The ID of the workflow run

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflow runs as a dict
        """
        api = f"/repos/{repo}/actions/runs/{run}"
        response = self._request(api, request=httpx.get)
        response.raise_for_status()
        return response.json()
