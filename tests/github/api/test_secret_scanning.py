# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

from pontos.github.api.secret_scanning import GitHubAsyncRESTSecretScanning
from pontos.github.models.base import SortOrder
from pontos.github.models.secret_scanning import (
    AlertSort,
    AlertState,
    LocationType,
    Resolution,
)
from tests import AsyncIteratorMock, aiter, anext
from tests.github.api import GitHubAsyncRESTTestCase, create_response

ALERTS = [
    {
        "number": 2,
        "created_at": "2020-11-06T18:48:51Z",
        "url": "https://api.github.com/repos/owner/private-repo/secret-scanning/alerts/2",
        "html_url": "https://github.com/owner/private-repo/security/secret-scanning/2",
        "locations_url": "https://api.github.com/repos/owner/private-repo/secret-scanning/alerts/2/locations",
        "state": "resolved",
        "resolution": "false_positive",
        "resolved_at": "2020-11-07T02:47:13Z",
        "resolved_by": {
            "login": "monalisa",
            "id": 2,
            "node_id": "MDQ6VXNlcjI=",
            "avatar_url": "https://alambic.github.com/avatars/u/2?",
            "gravatar_id": "",
            "url": "https://api.github.com/users/monalisa",
            "html_url": "https://github.com/monalisa",
            "followers_url": "https://api.github.com/users/monalisa/followers",
            "following_url": "https://api.github.com/users/monalisa/following{/other_user}",
            "gists_url": "https://api.github.com/users/monalisa/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/monalisa/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/monalisa/subscriptions",
            "organizations_url": "https://api.github.com/users/monalisa/orgs",
            "repos_url": "https://api.github.com/users/monalisa/repos",
            "events_url": "https://api.github.com/users/monalisa/events{/privacy}",
            "received_events_url": "https://api.github.com/users/monalisa/received_events",
            "type": "User",
            "site_admin": True,
        },
        "secret_type": "adafruit_io_key",
        "secret_type_display_name": "Adafruit IO Key",
        "secret": "aio_XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
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
        "push_protection_bypassed_by": {
            "login": "monalisa",
            "id": 2,
            "node_id": "MDQ6VXNlcjI=",
            "avatar_url": "https://alambic.github.com/avatars/u/2?",
            "gravatar_id": "",
            "url": "https://api.github.com/users/monalisa",
            "html_url": "https://github.com/monalisa",
            "followers_url": "https://api.github.com/users/monalisa/followers",
            "following_url": "https://api.github.com/users/monalisa/following{/other_user}",
            "gists_url": "https://api.github.com/users/monalisa/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/monalisa/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/monalisa/subscriptions",
            "organizations_url": "https://api.github.com/users/monalisa/orgs",
            "repos_url": "https://api.github.com/users/monalisa/repos",
            "events_url": "https://api.github.com/users/monalisa/events{/privacy}",
            "received_events_url": "https://api.github.com/users/monalisa/received_events",
            "type": "User",
            "site_admin": True,
        },
        "push_protection_bypassed": True,
        "push_protection_bypassed_at": "2020-11-06T21:48:51Z",
        "resolution_comment": "Example comment",
    },
    {
        "number": 1,
        "created_at": "2020-11-06T18:18:30Z",
        "url": "https://api.github.com/repos/owner/repo/secret-scanning/alerts/1",
        "html_url": "https://github.com/owner/repo/security/secret-scanning/1",
        "locations_url": "https://api.github.com/repos/owner/private-repo/secret-scanning/alerts/1/locations",
        "state": "open",
        "resolution": None,
        "resolved_at": None,
        "resolved_by": None,
        "secret_type": "mailchimp_api_key",
        "secret_type_display_name": "Mailchimp API Key",
        "secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-us2",
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
        "push_protection_bypassed_by": None,
        "push_protection_bypassed": False,
        "push_protection_bypassed_at": None,
        "resolution_comment": None,
    },
]


class GitHubAsyncRESTSecretScanningTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTSecretScanning

    async def test_enterprise_alerts(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.enterprise_alerts("foo"))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/enterprises/foo/secret-scanning/alerts",
            params={"per_page": "100", "sort": "created", "direction": "desc"},
        )

    async def test_enterprise_alerts_state(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.enterprise_alerts("foo", state=AlertState.RESOLVED)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/enterprises/foo/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "state": "resolved",
            },
        )

    async def test_enterprise_alerts_secret_types(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.enterprise_alerts(
                "foo",
                secret_types=[
                    "google_api_key",
                    "hashicorp_vault_service_token",
                ],
            )
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/enterprises/foo/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "secret_type": "google_api_key,hashicorp_vault_service_token",
            },
        )

    async def test_enterprise_alerts_resolutions(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.enterprise_alerts(
                "foo",
                resolutions=["false_positive", "wont_fix", "revoked"],
            )
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/enterprises/foo/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "resolution": "false_positive,wont_fix,revoked",
            },
        )

    async def test_enterprise_alerts_sort(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.enterprise_alerts("foo", sort=AlertSort.UPDATED)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/enterprises/foo/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "updated",
                "direction": "desc",
            },
        )

    async def test_enterprise_alerts_direction(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.enterprise_alerts("foo", direction=SortOrder.ASC)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/enterprises/foo/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "asc",
            },
        )

    async def test_organization_alerts(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.organization_alerts("foo"))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/secret-scanning/alerts",
            params={"per_page": "100", "sort": "created", "direction": "desc"},
        )

    async def test_organization_alerts_state(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.organization_alerts("foo", state=AlertState.RESOLVED)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "state": "resolved",
            },
        )

    async def test_organization_alerts_secret_types(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.organization_alerts(
                "foo",
                secret_types=[
                    "google_api_key",
                    "hashicorp_vault_service_token",
                ],
            )
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "secret_type": "google_api_key,hashicorp_vault_service_token",
            },
        )

    async def test_organization_alerts_resolutions(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.organization_alerts(
                "foo",
                resolutions=["false_positive", "wont_fix", "revoked"],
            )
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "resolution": "false_positive,wont_fix,revoked",
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
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/secret-scanning/alerts",
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
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/secret-scanning/alerts",
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
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/secret-scanning/alerts",
            params={"per_page": "100", "sort": "created", "direction": "desc"},
        )

    async def test_alerts_state(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", state=AlertState.RESOLVED))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "state": "resolved",
            },
        )

    async def test_alerts_secret_types(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.alerts(
                "foo/bar",
                secret_types=[
                    "google_api_key",
                    "hashicorp_vault_service_token",
                ],
            )
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "secret_type": "google_api_key,hashicorp_vault_service_token",
            },
        )

    async def test_alerts_resolutions(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.alerts(
                "foo/bar",
                resolutions=["false_positive", "wont_fix", "revoked"],
            )
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/secret-scanning/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "resolution": "false_positive,wont_fix,revoked",
            },
        )

    async def test_alerts_sort(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", sort=AlertSort.UPDATED))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/secret-scanning/alerts",
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
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/secret-scanning/alerts",
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
            "created_at": "2020-11-06T18:18:30Z",
            "url": "https://api.github.com/repos/owner/private-repo/secret-scanning/alerts/42",
            "html_url": "https://github.com/owner/private-repo/security/secret-scanning/42",
            "locations_url": "https://api.github.com/repos/owner/private-repo/secret-scanning/alerts/42/locations",
            "state": "open",
            "resolution": None,
            "resolved_at": None,
            "resolved_by": None,
            "secret_type": "mailchimp_api_key",
            "secret_type_display_name": "Mailchimp API Key",
            "secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-us2",
            "push_protection_bypassed_by": None,
            "push_protection_bypassed": False,
            "push_protection_bypassed_at": None,
            "resolution_comment": None,
        }
        self.client.get.return_value = response

        alert = await self.api.alert(
            "foo/bar",
            42,
        )

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/secret-scanning/alerts/42",
        )

        self.assertEqual(alert.number, 42)

    async def test_update(self):
        response = create_response()
        response.json.return_value = {
            "number": 42,
            "created_at": "2020-11-06T18:18:30Z",
            "url": "https://api.github.com/repos/owner/private-repo/secret-scanning/alerts/42",
            "html_url": "https://github.com/owner/private-repo/security/secret-scanning/42",
            "locations_url": "https://api.github.com/repos/owner/private-repo/secret-scanning/alerts/42/locations",
            "state": "resolved",
            "resolution": "used_in_tests",
            "resolved_at": "2020-11-16T22:42:07Z",
            "resolved_by": {
                "login": "monalisa",
                "id": 2,
                "node_id": "MDQ6VXNlcjI=",
                "avatar_url": "https://alambic.github.com/avatars/u/2?",
                "gravatar_id": "",
                "url": "https://api.github.com/users/monalisa",
                "html_url": "https://github.com/monalisa",
                "followers_url": "https://api.github.com/users/monalisa/followers",
                "following_url": "https://api.github.com/users/monalisa/following{/other_user}",
                "gists_url": "https://api.github.com/users/monalisa/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/monalisa/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/monalisa/subscriptions",
                "organizations_url": "https://api.github.com/users/monalisa/orgs",
                "repos_url": "https://api.github.com/users/monalisa/repos",
                "events_url": "https://api.github.com/users/monalisa/events{/privacy}",
                "received_events_url": "https://api.github.com/users/monalisa/received_events",
                "type": "User",
                "site_admin": True,
            },
            "secret_type": "mailchimp_api_key",
            "secret_type_display_name": "Mailchimp API Key",
            "secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-us2",
            "push_protection_bypassed": False,
            "push_protection_bypassed_by": None,
            "push_protection_bypassed_at": None,
            "resolution_comment": "Example comment",
        }
        self.client.patch.return_value = response

        alert = await self.api.update_alert(
            "foo/bar",
            1,
            AlertState.RESOLVED,
            resolution=Resolution.USED_IN_TESTS,
            resolution_comment="Only used in tests",
        )

        self.client.patch.assert_awaited_once_with(
            "/repos/foo/bar/secret-scanning/alerts/1",
            data={
                "state": "resolved",
                "resolution": "used_in_tests",
                "resolution_comment": "Only used in tests",
            },
        )

        self.assertEqual(alert.number, 42)
        self.assertIsNone(alert.repository)

    async def test_alerts_locations(self):
        response = create_response()
        response.json.return_value = [
            {
                "type": "commit",
                "details": {
                    "path": "/example/secrets.txt",
                    "start_line": 1,
                    "end_line": 1,
                    "start_column": 1,
                    "end_column": 64,
                    "blob_sha": "af5626b4a114abcb82d63db7c8082c3c4756e51b",
                    "blob_url": "https://api.github.com/repos/octocat/hello-world/git/blobs/af5626b4a114abcb82d63db7c8082c3c4756e51b",
                    "commit_sha": "f14d7debf9775f957cf4f1e8176da0786431f72b",
                    "commit_url": "https://api.github.com/repos/octocat/hello-world/git/commits/f14d7debf9775f957cf4f1e8176da0786431f72b",
                },
            },
            {
                "type": "issue_title",
                "details": {
                    "issue_title_url": "https://api.github.com/repos/octocat/Hello-World/issues/1347"
                },
            },
            {
                "type": "issue_body",
                "details": {
                    "issue_body_url": "https://api.github.com/repos/octocat/Hello-World/issues/1347"
                },
            },
            {
                "type": "issue_comment",
                "details": {
                    "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments/1081119451"
                },
            },
        ]

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.locations("foo/bar", 123))
        location = await anext(async_it)
        self.assertEqual(location.type, LocationType.COMMIT)
        location = await anext(async_it)
        self.assertEqual(location.type, LocationType.ISSUE_TITLE)
        location = await anext(async_it)
        self.assertEqual(location.type, LocationType.ISSUE_BODY)
        location = await anext(async_it)
        self.assertEqual(location.type, LocationType.ISSUE_COMMENT)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/secret-scanning/alerts/123/locations",
            params={
                "per_page": "100",
            },
        )
