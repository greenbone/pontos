# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

from pontos.github.api.code_scanning import GitHubAsyncRESTCodeScanning
from pontos.github.models.base import SortOrder
from pontos.github.models.code_scanning import (
    AlertSort,
    AlertState,
    DismissedReason,
    Severity,
)
from tests import AsyncIteratorMock, aiter, anext
from tests.github.api import GitHubAsyncRESTTestCase, create_response

ALERTS = [
    {
        "number": 4,
        "created_at": "2020-02-13T12:29:18Z",
        "url": "https://api.github.com/repos/octocat/hello-world/code-scanning/alerts/4",
        "html_url": "https://github.com/octocat/hello-world/code-scanning/4",
        "state": "open",
        "dismissed_by": None,
        "dismissed_at": None,
        "dismissed_reason": None,
        "dismissed_comment": None,
        "rule": {
            "id": "js/zipslip",
            "severity": "error",
            "tags": ["security", "external/cwe/cwe-022"],
            "description": "Arbitrary file write during zip extraction",
            "name": "js/zipslip",
        },
        "tool": {"name": "CodeQL", "guid": None, "version": "2.4.0"},
        "most_recent_instance": {
            "ref": "refs/heads/main",
            "analysis_key": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
            "category": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
            "environment": "{}",
            "state": "open",
            "commit_sha": "39406e42cb832f683daa691dd652a8dc36ee8930",
            "message": {"text": "This path depends on a user-provided value."},
            "location": {
                "path": "spec-main/api-session-spec.ts",
                "start_line": 917,
                "end_line": 917,
                "start_column": 7,
                "end_column": 18,
            },
            "classifications": ["test"],
        },
        "instances_url": "https://api.github.com/repos/octocat/hello-world/code-scanning/alerts/4/instances",
        "repository": {
            "id": 1296269,
            "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
            "name": "Hello-World",
            "full_name": "octocat/Hello-World",
            "owner": {
                "login": "octocat",
                "id": 1,
                "node_id": "MDQ6VXNlcjE=",
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octocat",
                "html_url": "https://github.com/octocat",
                "followers_url": "https://api.github.com/users/octocat/followers",
                "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                "organizations_url": "https://api.github.com/users/octocat/orgs",
                "repos_url": "https://api.github.com/users/octocat/repos",
                "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octocat/received_events",
                "type": "User",
                "site_admin": False,
            },
            "private": False,
            "html_url": "https://github.com/octocat/Hello-World",
            "description": "This your first repo!",
            "fork": False,
            "url": "https://api.github.com/repos/octocat/Hello-World",
            "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
            "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
            "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
            "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
            "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
            "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
            "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
            "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
            "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
            "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
            "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
            "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
            "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
            "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
            "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
            "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
            "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
            "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
            "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
            "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
            "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
            "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
            "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
            "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
            "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
            "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
            "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
            "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
            "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
            "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
            "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
            "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
            "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
            "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
            "hooks_url": "https://api.github.com/repos/octocat/Hello-World/hooks",
        },
    },
    {
        "number": 3,
        "created_at": "2020-02-13T12:29:18Z",
        "url": "https://api.github.com/repos/octocat/hello-world/code-scanning/alerts/3",
        "html_url": "https://github.com/octocat/hello-world/code-scanning/3",
        "state": "dismissed",
        "dismissed_by": {
            "login": "octocat",
            "id": 1,
            "node_id": "MDQ6VXNlcjE=",
            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
            "gravatar_id": "",
            "url": "https://api.github.com/users/octocat",
            "html_url": "https://github.com/octocat",
            "followers_url": "https://api.github.com/users/octocat/followers",
            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
            "organizations_url": "https://api.github.com/users/octocat/orgs",
            "repos_url": "https://api.github.com/users/octocat/repos",
            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
            "received_events_url": "https://api.github.com/users/octocat/received_events",
            "type": "User",
            "site_admin": False,
        },
        "dismissed_at": "2020-02-14T12:29:18Z",
        "dismissed_reason": "false positive",
        "dismissed_comment": "This alert is not actually correct, because there's a sanitizer included in the library.",
        "rule": {
            "id": "js/zipslip",
            "severity": "error",
            "tags": ["security", "external/cwe/cwe-022"],
            "description": "Arbitrary file write during zip extraction",
            "name": "js/zipslip",
        },
        "tool": {"name": "CodeQL", "guid": None, "version": "2.4.0"},
        "most_recent_instance": {
            "ref": "refs/heads/main",
            "analysis_key": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
            "category": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
            "environment": "{}",
            "state": "open",
            "commit_sha": "39406e42cb832f683daa691dd652a8dc36ee8930",
            "message": {"text": "This path depends on a user-provided value."},
            "location": {
                "path": "lib/ab12-gen.js",
                "start_line": 917,
                "end_line": 917,
                "start_column": 7,
                "end_column": 18,
            },
            "classifications": [],
        },
        "instances_url": "https://api.github.com/repos/octocat/hello-world/code-scanning/alerts/3/instances",
        "repository": {
            "id": 1296269,
            "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
            "name": "Hello-World",
            "full_name": "octocat/Hello-World",
            "owner": {
                "login": "octocat",
                "id": 1,
                "node_id": "MDQ6VXNlcjE=",
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octocat",
                "html_url": "https://github.com/octocat",
                "followers_url": "https://api.github.com/users/octocat/followers",
                "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                "organizations_url": "https://api.github.com/users/octocat/orgs",
                "repos_url": "https://api.github.com/users/octocat/repos",
                "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octocat/received_events",
                "type": "User",
                "site_admin": False,
            },
            "private": False,
            "html_url": "https://github.com/octocat/Hello-World",
            "description": "This your first repo!",
            "fork": False,
            "url": "https://api.github.com/repos/octocat/Hello-World",
            "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
            "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
            "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
            "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
            "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
            "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
            "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
            "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
            "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
            "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
            "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
            "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
            "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
            "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
            "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
            "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
            "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
            "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
            "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
            "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
            "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
            "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
            "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
            "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
            "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
            "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
            "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
            "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
            "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
            "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
            "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
            "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
            "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
            "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
            "hooks_url": "https://api.github.com/repos/octocat/Hello-World/hooks",
        },
    },
]


class GitHubAsyncRESTCodeScanningTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTCodeScanning

    async def test_organization_alerts(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.organization_alerts("foo"))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/code-scanning/alerts",
            params={"per_page": "100", "sort": "created", "direction": "desc"},
        )

    async def test_organization_alerts_state(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.organization_alerts("foo", state=AlertState.FIXED)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "state": "fixed",
            },
        )

    async def test_organization_alerts_tool_name(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.organization_alerts("foo", tool_name="CodeQL")
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "tool_name": "CodeQL",
            },
        )

    async def test_organization_alerts_tool_guid(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.organization_alerts("foo", tool_guid=None))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "tool_guid": None,
            },
        )

    async def test_organization_alerts_severity(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.organization_alerts("foo", severity=Severity.ERROR)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "severity": "error",
            },
        )

    async def test_organization_alerts_sort(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.organization_alerts("foo", sort=AlertSort.UPDATED)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "updated",
                "direction": "desc",
            },
        )

    async def test_organization_alerts_direction(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.organization_alerts("foo", direction=SortOrder.ASC)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "asc",
            },
        )

    async def test_alerts(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar"))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/alerts",
            params={"per_page": "100", "sort": "created", "direction": "desc"},
        )

    async def test_alerts_state(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", state=AlertState.FIXED))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "state": "fixed",
            },
        )

    async def test_alerts_tool_name(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", tool_name="CodeQL"))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "tool_name": "CodeQL",
            },
        )

    async def test_alerts_tool_guid(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", tool_guid=None))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "tool_guid": None,
            },
        )

    async def test_alerts_severity(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", severity=Severity.ERROR))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "severity": "error",
            },
        )

    async def test_alerts_sort(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", sort=AlertSort.UPDATED))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "updated",
                "direction": "desc",
            },
        )

    async def test_alerts_direction(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", direction=SortOrder.ASC))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 4)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "asc",
            },
        )

    async def test_alert(self):
        response = create_response()
        response.json.return_value = {
            "number": 42,
            "created_at": "2020-06-19T11:21:34Z",
            "url": "https://api.github.com/repos/octocat/hello-world/code-scanning/alerts/42",
            "html_url": "https://github.com/octocat/hello-world/code-scanning/42",
            "state": "dismissed",
            "fixed_at": None,
            "dismissed_by": {
                "login": "octocat",
                "id": 54933897,
                "node_id": "MDQ6VXNlcjE=",
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octocat",
                "html_url": "https://github.com/octocat",
                "followers_url": "https://api.github.com/users/octocat/followers",
                "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                "organizations_url": "https://api.github.com/users/octocat/orgs",
                "repos_url": "https://api.github.com/users/octocat/repos",
                "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octocat/received_events",
                "type": "User",
                "site_admin": False,
            },
            "dismissed_at": "2020-02-14T12:29:18Z",
            "dismissed_reason": "false positive",
            "dismissed_comment": "This alert is not actually correct, because there's a sanitizer included in the library.",
            "rule": {
                "id": "js/zipslip",
                "severity": "error",
                "security_severity_level": "high",
                "description": 'Arbitrary file write during zip extraction ("Zip Slip")',
                "name": "js/zipslip",
                "full_description": "Extracting files from a malicious zip archive without validating that the destination file path is within the destination directory can cause files outside the destination directory to be overwritten.",
                "tags": ["security", "external/cwe/cwe-022"],
                "help": '# Arbitrary file write during zip extraction ("Zip Slip")\\nExtracting files from a malicious zip archive without validating that the destination file path is within the destination directory can cause files outside the destination directory to be overwritten ...',
                "help_uri": "https://codeql.github.com/",
            },
            "tool": {"name": "CodeQL", "guid": None, "version": "2.4.0"},
            "most_recent_instance": {
                "ref": "refs/heads/main",
                "analysis_key": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
                "category": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
                "environment": "{}",
                "state": "dismissed",
                "commit_sha": "39406e42cb832f683daa691dd652a8dc36ee8930",
                "message": {
                    "text": "This path depends on a user-provided value."
                },
                "location": {
                    "path": "spec-main/api-session-spec.ts",
                    "start_line": 917,
                    "end_line": 917,
                    "start_column": 7,
                    "end_column": 18,
                },
                "classifications": ["test"],
            },
            "instances_url": "https://api.github.com/repos/octocat/hello-world/code-scanning/alerts/42/instances",
        }
        self.client.get.return_value = response

        alert = await self.api.alert(
            "foo/bar",
            42,
        )

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/code-scanning/alerts/42",
        )

        self.assertEqual(alert.number, 42)

    async def test_update(self):
        response = create_response()
        response.json.return_value = {
            "number": 42,
            "created_at": "2020-08-25T21:28:36Z",
            "url": "https://api.github.com/repos/octocat/hello-world/code-scanning/alerts/42",
            "html_url": "https://github.com/octocat/hello-world/code-scanning/42",
            "state": "dismissed",
            "fixed_at": None,
            "dismissed_by": {
                "login": "octocat",
                "id": 1,
                "node_id": "MDQ6VXNlcjE=",
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octocat",
                "html_url": "https://github.com/octocat",
                "followers_url": "https://api.github.com/users/octocat/followers",
                "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                "organizations_url": "https://api.github.com/users/octocat/orgs",
                "repos_url": "https://api.github.com/users/octocat/repos",
                "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octocat/received_events",
                "type": "User",
                "site_admin": False,
            },
            "dismissed_at": "2020-09-02T22:34:56Z",
            "dismissed_reason": "false positive",
            "dismissed_comment": "This alert is not actually correct, because there's a sanitizer included in the library.",
            "rule": {
                "id": "js/zipslip",
                "severity": "error",
                "security_severity_level": "high",
                "description": 'Arbitrary file write during zip extraction ("Zip Slip")',
                "name": "js/zipslip",
                "full_description": "Extracting files from a malicious zip archive without validating that the destination file path is within the destination directory can cause files outside the destination directory to be overwritten.",
                "tags": ["security", "external/cwe/cwe-022"],
                "help": '# Arbitrary file write during zip extraction ("Zip Slip")\\nExtracting files from a malicious zip archive without validating that the destination file path is within the destination directory can cause files outside the destination directory to be overwritten ...',
                "help_uri": "https://codeql.github.com/",
            },
            "tool": {"name": "CodeQL", "guid": None, "version": "2.4.0"},
            "most_recent_instance": {
                "ref": "refs/heads/main",
                "analysis_key": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
                "category": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
                "environment": "{}",
                "state": "dismissed",
                "commit_sha": "39406e42cb832f683daa691dd652a8dc36ee8930",
                "message": {
                    "text": "This path depends on a user-provided value."
                },
                "location": {
                    "path": "spec-main/api-session-spec.ts",
                    "start_line": 917,
                    "end_line": 917,
                    "start_column": 7,
                    "end_column": 18,
                },
                "classifications": ["test"],
            },
            "instances_url": "https://api.github.com/repos/octocat/hello-world/code-scanning/alerts/42/instances",
        }
        self.client.patch.return_value = response

        alert = await self.api.update_alert(
            "foo/bar",
            42,
            AlertState.DISMISSED,
            dismissed_reason=DismissedReason.USED_IN_TESTS,
            dismissed_comment="Only used in tests",
        )

        self.client.patch.assert_awaited_once_with(
            "/repos/foo/bar/code-scanning/alerts/42",
            data={
                "state": "dismissed",
                "dismissed_reason": "used in tests",
                "dismissed_comment": "Only used in tests",
            },
        )

        self.assertEqual(alert.number, 42)
        self.assertIsNone(alert.repository)

    async def test_alerts_instances(self):
        response = create_response()
        response.json.return_value = [
            {
                "ref": "refs/heads/main",
                "analysis_key": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
                "environment": "",
                "category": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
                "state": "open",
                "fixed_at": None,
                "commit_sha": "39406e42cb832f683daa691dd652a8dc36ee8930",
                "message": {
                    "text": "This path depends on a user-provided value."
                },
                "location": {
                    "path": "lib/ab12-gen.js",
                    "start_line": 917,
                    "end_line": 917,
                    "start_column": 7,
                    "end_column": 18,
                },
                "classifications": ["library"],
            },
            {
                "ref": "refs/pull/3740/merge",
                "analysis_key": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
                "environment": "",
                "category": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
                "state": "fixed",
                "fixed_at": "2020-02-14T12:29:18Z",
                "commit_sha": "b09da05606e27f463a2b49287684b4ae777092f2",
                "message": {
                    "text": "This suffix check is missing a length comparison to correctly handle lastIndexOf returning -1."
                },
                "location": {
                    "path": "app/script.js",
                    "start_line": 2,
                    "end_line": 2,
                    "start_column": 10,
                    "end_column": 50,
                },
                "classifications": ["source"],
            },
        ]

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.instances("foo/bar", 1))
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/main")
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/pull/3740/merge")

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/alerts/1/instances",
            params={
                "per_page": "100",
            },
        )
