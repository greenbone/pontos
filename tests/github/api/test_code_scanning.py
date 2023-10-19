# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

import json

from pontos.github.api.code_scanning import GitHubAsyncRESTCodeScanning
from pontos.github.models.base import SortOrder
from pontos.github.models.code_scanning import (
    AlertSort,
    AlertState,
    DefaultSetupState,
    DismissedReason,
    Language,
    QuerySuite,
    SarifProcessingStatus,
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

ANALYSES = [
    {
        "ref": "refs/heads/main",
        "commit_sha": "d99612c3e1f2970085cfbaeadf8f010ef69bad83",
        "analysis_key": ".github/workflows/codeql-analysis.yml:analyze",
        "environment": '{"language":"python"}',
        "error": "",
        "category": ".github/workflows/codeql-analysis.yml:analyze/language:python",
        "created_at": "2020-08-27T15:05:21Z",
        "results_count": 17,
        "rules_count": 49,
        "id": 201,
        "url": "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses/201",
        "sarif_id": "6c81cd8e-b078-4ac3-a3be-1dad7dbd0b53",
        "tool": {"name": "CodeQL", "guid": None, "version": "2.4.0"},
        "deletable": True,
        "warning": "",
    },
    {
        "ref": "refs/heads/my-branch",
        "commit_sha": "c8cff6510d4d084fb1b4aa13b64b97ca12b07321",
        "analysis_key": ".github/workflows/shiftleft.yml:build",
        "environment": "{}",
        "error": "",
        "category": ".github/workflows/shiftleft.yml:build/",
        "created_at": "2020-08-31T22:46:44Z",
        "results_count": 17,
        "rules_count": 32,
        "id": 200,
        "url": "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses/200",
        "sarif_id": "8981cd8e-b078-4ac3-a3be-1dad7dbd0b582",
        "tool": {
            "name": "Python Security Analysis",
            "guid": None,
            "version": "1.2.0",
        },
        "deletable": True,
        "warning": "",
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

    async def test_analyses(self):
        response = create_response()
        response.json.return_value = ANALYSES

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.analyses("foo/bar"))
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/main")
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/my-branch")

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/analyses",
            params={
                "per_page": "100",
                "direction": "desc",
            },
        )

    async def test_analyses_tool_name(self):
        response = create_response()
        response.json.return_value = ANALYSES

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.analyses("foo/bar", tool_name="CodeQL"))
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/main")
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/my-branch")

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/analyses",
            params={
                "per_page": "100",
                "direction": "desc",
                "tool_name": "CodeQL",
            },
        )

    async def test_analyses_tool_guid(self):
        response = create_response()
        response.json.return_value = ANALYSES

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.analyses("foo/bar", tool_guid="123"))
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/main")
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/my-branch")

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/analyses",
            params={
                "per_page": "100",
                "direction": "desc",
                "tool_guid": "123",
            },
        )

    async def test_analyses_sarif_id(self):
        response = create_response()
        response.json.return_value = ANALYSES

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.analyses("foo/bar", sarif_id="123"))
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/main")
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/my-branch")

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/analyses",
            params={
                "per_page": "100",
                "direction": "desc",
                "sarif_id": "123",
            },
        )

    async def test_analyses_ref(self):
        response = create_response()
        response.json.return_value = ANALYSES

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.analyses("foo/bar", ref="refs/heads/main"))
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/main")
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/my-branch")

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/analyses",
            params={
                "per_page": "100",
                "direction": "desc",
                "ref": "refs/heads/main",
            },
        )

    async def test_analyses_direction(self):
        response = create_response()
        response.json.return_value = ANALYSES

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.analyses("foo/bar", direction=SortOrder.ASC))
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/main")
        instance = await anext(async_it)
        self.assertEqual(instance.ref, "refs/heads/my-branch")

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/analyses",
            params={
                "per_page": "100",
                "direction": "asc",
            },
        )

    async def test_analysis(self):
        response = create_response()
        response.json.return_value = {
            "ref": "refs/heads/main",
            "commit_sha": "c18c69115654ff0166991962832dc2bd7756e655",
            "analysis_key": ".github/workflows/codeql-analysis.yml:analyze",
            "environment": '{"language":"javascript"}',
            "error": "",
            "category": ".github/workflows/codeql-analysis.yml:analyze/language:javascript",
            "created_at": "2021-01-13T11:55:49Z",
            "results_count": 3,
            "rules_count": 67,
            "id": 3602840,
            "url": "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses/201",
            "sarif_id": "47177e22-5596-11eb-80a1-c1e54ef945c6",
            "tool": {"name": "CodeQL", "guid": None, "version": "2.4.0"},
            "deletable": True,
            "warning": "",
        }
        self.client.get.return_value = response

        alert = await self.api.analysis(
            "foo/bar",
            42,
        )

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/code-scanning/analyses/42",
        )

        self.assertEqual(alert.ref, "refs/heads/main")

    async def test_delete_analysis(self):
        response = create_response()
        response.json.return_value = {
            "next_analysis_url": "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses/41",
            "confirm_delete_url": "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses/41?confirm_delete",
        }
        self.client.delete.return_value = response

        resp = await self.api.delete_analysis(
            "foo/bar",
            42,
        )

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/code-scanning/analyses/42",
        )

        self.assertEqual(
            resp["next_analysis_url"],
            "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses/41",
        )
        self.assertEqual(
            resp["confirm_delete_url"],
            "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses/41?confirm_delete",
        )

    async def test_codeql_databases(self):
        response = create_response()
        response.json.return_value = [
            {
                "id": 1,
                "name": "database.zip",
                "language": "java",
                "uploader": {
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
                "content_type": "application/zip",
                "size": 1024,
                "created_at": "2022-09-12T12:14:32Z",
                "updated_at": "2022-09-12T12:14:32Z",
                "url": "https://api.github.com/repos/octocat/Hello-World/code-scanning/codeql/databases/java",
                "commit_oid": 12345678901234567000,
            },
            {
                "id": 2,
                "name": "database.zip",
                "language": "ruby",
                "uploader": {
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
                "content_type": "application/zip",
                "size": 1024,
                "created_at": "2022-09-12T12:14:32Z",
                "updated_at": "2022-09-12T12:14:32Z",
                "url": "https://api.github.com/repos/octocat/Hello-World/code-scanning/codeql/databases/ruby",
                "commit_oid": 23456789012345680000,
            },
        ]

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.codeql_databases("foo/bar"))
        db = await anext(async_it)
        self.assertEqual(db.id, 1)
        alert = await anext(async_it)
        self.assertEqual(alert.id, 2)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/code-scanning/codeql/databases",
            params={
                "per_page": "100",
            },
        )

    async def test_codeql_database(self):
        response = create_response()
        response.json.return_value = {
            "id": 1,
            "name": "database.zip",
            "language": "java",
            "uploader": {
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
            "content_type": "application/zip",
            "size": 1024,
            "created_at": "2022-09-12T12:14:32Z",
            "updated_at": "2022-09-12T12:14:32Z",
            "url": "https://api.github.com/repos/octocat/Hello-World/code-scanning/codeql/databases/java",
            "commit_oid": 12345678901234567000,
        }
        self.client.get.return_value = response

        alert = await self.api.codeql_database(
            "foo/bar",
            "java",
        )

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/code-scanning/codeql/databases/java",
        )

        self.assertEqual(alert.id, 1)

    async def test_default_setup(self):
        response = create_response()
        response.json.return_value = {
            "state": "configured",
            "languages": ["ruby", "python"],
            "query_suite": "default",
            "updated_at": "2023-01-19T11:21:34Z",
            "schedule": "weekly",
        }
        self.client.get.return_value = response

        setup = await self.api.default_setup(
            "foo/bar",
        )

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/code-scanning/default-setup",
        )

        self.assertEqual(setup.state, DefaultSetupState.CONFIGURED)

    async def test_update_default_setup(self):
        response = create_response()
        response.json.return_value = {
            "run_id": 42,
            "run_url": "https://api.github.com/repos/octoorg/octocat/actions/runs/42",
        }
        self.client.patch.return_value = response

        resp = await self.api.update_default_setup(
            "foo/bar",
            state=DefaultSetupState.CONFIGURED,
            query_suite=QuerySuite.EXTENDED,
            languages=[Language.GO],
        )

        self.client.patch.assert_awaited_once_with(
            "/repos/foo/bar/code-scanning/code-scanning/default-setup",
            data={
                "state": "configured",
                "query_suite": "extended",
                "languages": ["go"],
            },
        )

        self.assertEqual(
            resp["run_id"],
            42,
        )
        self.assertEqual(
            resp["run_url"],
            "https://api.github.com/repos/octoorg/octocat/actions/runs/42",
        )

    async def test_upload_sarif_data(self):
        sarif = {
            "version": "2.1.0",
            "$schema": "http://json.schemastore.org/sarif-2.1.0-rtm.4",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "ESLint",
                            "informationUri": "https://eslint.org",
                            "rules": [
                                {
                                    "id": "no-unused-vars",
                                    "shortDescription": {
                                        "text": "disallow unused variables"
                                    },
                                    "helpUri": "https://eslint.org/docs/rules/no-unused-vars",
                                    "properties": {"category": "Variables"},
                                }
                            ],
                        }
                    },
                    "artifacts": [
                        {
                            "location": {
                                "uri": "file:///C:/dev/sarif/sarif-tutorials/samples/Introduction/simple-example.js"
                            }
                        }
                    ],
                    "results": [
                        {
                            "level": "error",
                            "message": {
                                "text": "'x' is assigned a value but never used."
                            },
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {
                                            "uri": "file:///C:/dev/sarif/sarif-tutorials/samples/Introduction/simple-example.js",
                                            "index": 0,
                                        },
                                        "region": {
                                            "startLine": 1,
                                            "startColumn": 5,
                                        },
                                    }
                                }
                            ],
                            "ruleId": "no-unused-vars",
                            "ruleIndex": 0,
                        }
                    ],
                }
            ],
        }

        response = create_response()
        response.json.return_value = {
            "id": "47177e22-5596-11eb-80a1-c1e54ef945c6",
            "url": "https://api.github.com/repos/octocat/hello-world/code-scanning/sarifs/47177e22-5596-11eb-80a1-c1e54ef945c6",
        }
        self.client.post.return_value = response

        resp = await self.api.upload_sarif_data(
            "foo/bar",
            commit_sha="4b6472266afd7b471e86085a6659e8c7f2b119da",
            ref="refs/heads/master",
            sarif=json.dumps(sarif).encode(),
        )

        self.assertEqual(self.client.post.await_count, 1)
        args = self.client.post.await_args
        self.assertEqual(args.args, ("/repos/foo/bar/code-scanning/sarifs",))
        data = args.kwargs["data"]
        self.assertEqual(
            data["commit_sha"],
            "4b6472266afd7b471e86085a6659e8c7f2b119da",
        )
        self.assertEqual(
            data["ref"],
            "refs/heads/master",
        )
        # it's not possible to check the sarif data in Python < 3.11 because
        # gzip creates different content on each run
        self.assertTrue("sarif" in data)

        self.assertEqual(resp["id"], "47177e22-5596-11eb-80a1-c1e54ef945c6")
        self.assertEqual(
            resp["url"],
            "https://api.github.com/repos/octocat/hello-world/code-scanning/sarifs/47177e22-5596-11eb-80a1-c1e54ef945c6",
        )

    async def test_sarif(self):
        response = create_response()
        response.json.return_value = {
            "processing_status": "complete",
            "analyses_url": "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses?sarif_id=47177e22-5596-11eb-80a1-c1e54ef945c6",
        }
        self.client.get.return_value = response

        resp = await self.api.sarif(
            "foo/bar", "47177e22-5596-11eb-80a1-c1e54ef945c6"
        )
        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/code-scanning/sarifs/47177e22-5596-11eb-80a1-c1e54ef945c6",
        )

        self.assertEqual(resp.processing_status, SarifProcessingStatus.COMPLETE)
        self.assertEqual(
            resp.analyses_url,
            "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses?sarif_id=47177e22-5596-11eb-80a1-c1e54ef945c6",
        )
        self.assertIsNone(resp.errors)
