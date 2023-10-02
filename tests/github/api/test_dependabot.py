# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

from pontos.github.api.dependabot import GitHubAsyncRESTDependabot
from pontos.github.models.base import SortOrder
from pontos.github.models.dependabot import (
    AlertSort,
    AlertState,
    DependencyScope,
    DismissedReason,
    Severity,
)
from tests import AsyncIteratorMock, aiter, anext
from tests.github.api import GitHubAsyncRESTTestCase, create_response

ALERTS = [
    {
        "number": 2,
        "state": "dismissed",
        "dependency": {
            "package": {"ecosystem": "pip", "name": "django"},
            "manifest_path": "path/to/requirements.txt",
            "scope": "runtime",
        },
        "security_advisory": {
            "ghsa_id": "GHSA-rf4j-j272-fj86",
            "cve_id": "CVE-2018-6188",
            "summary": "Django allows remote attackers to obtain potentially sensitive information by leveraging data exposure from the confirm_login_allowed() method, as demonstrated by discovering whether a user account is inactive",
            "description": "django.contrib.auth.forms.AuthenticationForm in Django 2.0 before 2.0.2, and 1.11.8 and 1.11.9, allows remote attackers to obtain potentially sensitive information by leveraging data exposure from the confirm_login_allowed() method, as demonstrated by discovering whether a user account is inactive.",
            "vulnerabilities": [
                {
                    "package": {"ecosystem": "pip", "name": "django"},
                    "severity": "high",
                    "vulnerable_version_range": ">= 2.0.0, < 2.0.2",
                    "first_patched_version": {"identifier": "2.0.2"},
                },
                {
                    "package": {"ecosystem": "pip", "name": "django"},
                    "severity": "high",
                    "vulnerable_version_range": ">= 1.11.8, < 1.11.10",
                    "first_patched_version": {"identifier": "1.11.10"},
                },
            ],
            "severity": "high",
            "cvss": {
                "vector_string": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                "score": 7.5,
            },
            "cwes": [
                {
                    "cwe_id": "CWE-200",
                    "name": "Exposure of Sensitive Information to an Unauthorized Actor",
                }
            ],
            "identifiers": [
                {"type": "GHSA", "value": "GHSA-rf4j-j272-fj86"},
                {"type": "CVE", "value": "CVE-2018-6188"},
            ],
            "references": [
                {"url": "https://nvd.nist.gov/vuln/detail/CVE-2018-6188"},
                {"url": "https://github.com/advisories/GHSA-rf4j-j272-fj86"},
                {"url": "https://usn.ubuntu.com/3559-1/"},
                {
                    "url": "https://www.djangoproject.com/weblog/2018/feb/01/security-releases/"
                },
                {"url": "http://www.securitytracker.com/id/1040422"},
            ],
            "published_at": "2018-10-03T21:13:54Z",
            "updated_at": "2022-04-26T18:35:37Z",
            "withdrawn_at": None,
        },
        "security_vulnerability": {
            "package": {"ecosystem": "pip", "name": "django"},
            "severity": "high",
            "vulnerable_version_range": ">= 2.0.0, < 2.0.2",
            "first_patched_version": {"identifier": "2.0.2"},
        },
        "url": "https://api.github.com/repos/octo-org/octo-repo/dependabot/alerts/2",
        "html_url": "https://github.com/octo-org/octo-repo/security/dependabot/2",
        "created_at": "2022-06-15T07:43:03Z",
        "updated_at": "2022-08-23T14:29:47Z",
        "dismissed_at": "2022-08-23T14:29:47Z",
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
        "dismissed_reason": "tolerable_risk",
        "dismissed_comment": "This alert is accurate but we use a sanitizer.",
        "fixed_at": None,
        "repository": {
            "id": 217723378,
            "node_id": "MDEwOlJlcG9zaXRvcnkyMTc3MjMzNzg=",
            "name": "octo-repo",
            "full_name": "octo-org/octo-repo",
            "owner": {
                "login": "octo-org",
                "id": 6811672,
                "node_id": "MDEyOk9yZ2FuaXphdGlvbjY4MTE2NzI=",
                "avatar_url": "https://avatars3.githubusercontent.com/u/6811672?v=4",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octo-org",
                "html_url": "https://github.com/octo-org",
                "followers_url": "https://api.github.com/users/octo-org/followers",
                "following_url": "https://api.github.com/users/octo-org/following{/other_user}",
                "gists_url": "https://api.github.com/users/octo-org/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octo-org/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octo-org/subscriptions",
                "organizations_url": "https://api.github.com/users/octo-org/orgs",
                "repos_url": "https://api.github.com/users/octo-org/repos",
                "events_url": "https://api.github.com/users/octo-org/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octo-org/received_events",
                "type": "Organization",
                "site_admin": False,
            },
            "private": True,
            "html_url": "https://github.com/octo-org/octo-repo",
            "description": None,
            "fork": False,
            "url": "https://api.github.com/repos/octo-org/octo-repo",
            "archive_url": "https://api.github.com/repos/octo-org/octo-repo/{archive_format}{/ref}",
            "assignees_url": "https://api.github.com/repos/octo-org/octo-repo/assignees{/user}",
            "blobs_url": "https://api.github.com/repos/octo-org/octo-repo/git/blobs{/sha}",
            "branches_url": "https://api.github.com/repos/octo-org/octo-repo/branches{/branch}",
            "collaborators_url": "https://api.github.com/repos/octo-org/octo-repo/collaborators{/collaborator}",
            "comments_url": "https://api.github.com/repos/octo-org/octo-repo/comments{/number}",
            "commits_url": "https://api.github.com/repos/octo-org/octo-repo/commits{/sha}",
            "compare_url": "https://api.github.com/repos/octo-org/octo-repo/compare/{base}...{head}",
            "contents_url": "https://api.github.com/repos/octo-org/octo-repo/contents/{+path}",
            "contributors_url": "https://api.github.com/repos/octo-org/octo-repo/contributors",
            "deployments_url": "https://api.github.com/repos/octo-org/octo-repo/deployments",
            "downloads_url": "https://api.github.com/repos/octo-org/octo-repo/downloads",
            "events_url": "https://api.github.com/repos/octo-org/octo-repo/events",
            "forks_url": "https://api.github.com/repos/octo-org/octo-repo/forks",
            "git_commits_url": "https://api.github.com/repos/octo-org/octo-repo/git/commits{/sha}",
            "git_refs_url": "https://api.github.com/repos/octo-org/octo-repo/git/refs{/sha}",
            "git_tags_url": "https://api.github.com/repos/octo-org/octo-repo/git/tags{/sha}",
            "hooks_url": "https://api.github.com/repos/octo-org/octo-repo/hooks",
            "issue_comment_url": "https://api.github.com/repos/octo-org/octo-repo/issues/comments{/number}",
            "issue_events_url": "https://api.github.com/repos/octo-org/octo-repo/issues/events{/number}",
            "issues_url": "https://api.github.com/repos/octo-org/octo-repo/issues{/number}",
            "keys_url": "https://api.github.com/repos/octo-org/octo-repo/keys{/key_id}",
            "labels_url": "https://api.github.com/repos/octo-org/octo-repo/labels{/name}",
            "languages_url": "https://api.github.com/repos/octo-org/octo-repo/languages",
            "merges_url": "https://api.github.com/repos/octo-org/octo-repo/merges",
            "milestones_url": "https://api.github.com/repos/octo-org/octo-repo/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/octo-org/octo-repo/notifications{?since,all,participating}",
            "pulls_url": "https://api.github.com/repos/octo-org/octo-repo/pulls{/number}",
            "releases_url": "https://api.github.com/repos/octo-org/octo-repo/releases{/id}",
            "stargazers_url": "https://api.github.com/repos/octo-org/octo-repo/stargazers",
            "statuses_url": "https://api.github.com/repos/octo-org/octo-repo/statuses/{sha}",
            "subscribers_url": "https://api.github.com/repos/octo-org/octo-repo/subscribers",
            "subscription_url": "https://api.github.com/repos/octo-org/octo-repo/subscription",
            "tags_url": "https://api.github.com/repos/octo-org/octo-repo/tags",
            "teams_url": "https://api.github.com/repos/octo-org/octo-repo/teams",
            "trees_url": "https://api.github.com/repos/octo-org/octo-repo/git/trees{/sha}",
        },
    },
    {
        "number": 1,
        "state": "open",
        "dependency": {
            "package": {"ecosystem": "pip", "name": "ansible"},
            "manifest_path": "path/to/requirements.txt",
            "scope": "runtime",
        },
        "security_advisory": {
            "ghsa_id": "GHSA-8f4m-hccc-8qph",
            "cve_id": "CVE-2021-20191",
            "summary": "Insertion of Sensitive Information into Log File in ansible",
            "description": "A flaw was found in ansible. Credentials, such as secrets, are being disclosed in console log by default and not protected by no_log feature when using those modules. An attacker can take advantage of this information to steal those credentials. The highest threat from this vulnerability is to data confidentiality.",
            "vulnerabilities": [
                {
                    "package": {"ecosystem": "pip", "name": "ansible"},
                    "severity": "medium",
                    "vulnerable_version_range": ">= 2.9.0, < 2.9.18",
                    "first_patched_version": {"identifier": "2.9.18"},
                },
                {
                    "package": {"ecosystem": "pip", "name": "ansible"},
                    "severity": "medium",
                    "vulnerable_version_range": "< 2.8.19",
                    "first_patched_version": {"identifier": "2.8.19"},
                },
                {
                    "package": {"ecosystem": "pip", "name": "ansible"},
                    "severity": "medium",
                    "vulnerable_version_range": ">= 2.10.0, < 2.10.7",
                    "first_patched_version": {"identifier": "2.10.7"},
                },
            ],
            "severity": "medium",
            "cvss": {
                "vector_string": "CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N",
                "score": 5.5,
            },
            "cwes": [
                {
                    "cwe_id": "CWE-532",
                    "name": "Insertion of Sensitive Information into Log File",
                }
            ],
            "identifiers": [
                {"type": "GHSA", "value": "GHSA-8f4m-hccc-8qph"},
                {"type": "CVE", "value": "CVE-2021-20191"},
            ],
            "references": [
                {"url": "https://nvd.nist.gov/vuln/detail/CVE-2021-20191"},
                {
                    "url": "https://access.redhat.com/security/cve/cve-2021-20191"
                },
                {"url": "https://bugzilla.redhat.com/show_bug.cgi?id=1916813"},
            ],
            "published_at": "2021-06-01T17:38:00Z",
            "updated_at": "2021-08-12T23:06:00Z",
            "withdrawn_at": None,
        },
        "security_vulnerability": {
            "package": {"ecosystem": "pip", "name": "ansible"},
            "severity": "medium",
            "vulnerable_version_range": "< 2.8.19",
            "first_patched_version": {"identifier": "2.8.19"},
        },
        "url": "https://api.github.com/repos/octo-org/hello-world/dependabot/alerts/1",
        "html_url": "https://github.com/octo-org/hello-world/security/dependabot/1",
        "created_at": "2022-06-14T15:21:52Z",
        "updated_at": "2022-06-14T15:21:52Z",
        "dismissed_at": None,
        "dismissed_by": None,
        "dismissed_reason": None,
        "dismissed_comment": None,
        "fixed_at": None,
        "repository": {
            "id": 664700648,
            "node_id": "MDEwOlJlcG9zaXRvcnk2NjQ3MDA2NDg=",
            "name": "hello-world",
            "full_name": "octo-org/hello-world",
            "owner": {
                "login": "octo-org",
                "id": 6811672,
                "node_id": "MDEyOk9yZ2FuaXphdGlvbjY4MTE2NzI=",
                "avatar_url": "https://avatars3.githubusercontent.com/u/6811672?v=4",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octo-org",
                "html_url": "https://github.com/octo-org",
                "followers_url": "https://api.github.com/users/octo-org/followers",
                "following_url": "https://api.github.com/users/octo-org/following{/other_user}",
                "gists_url": "https://api.github.com/users/octo-org/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octo-org/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octo-org/subscriptions",
                "organizations_url": "https://api.github.com/users/octo-org/orgs",
                "repos_url": "https://api.github.com/users/octo-org/repos",
                "events_url": "https://api.github.com/users/octo-org/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octo-org/received_events",
                "type": "Organization",
                "site_admin": False,
            },
            "private": True,
            "html_url": "https://github.com/octo-org/hello-world",
            "description": None,
            "fork": False,
            "url": "https://api.github.com/repos/octo-org/hello-world",
            "archive_url": "https://api.github.com/repos/octo-org/hello-world/{archive_format}{/ref}",
            "assignees_url": "https://api.github.com/repos/octo-org/hello-world/assignees{/user}",
            "blobs_url": "https://api.github.com/repos/octo-org/hello-world/git/blobs{/sha}",
            "branches_url": "https://api.github.com/repos/octo-org/hello-world/branches{/branch}",
            "collaborators_url": "https://api.github.com/repos/octo-org/hello-world/collaborators{/collaborator}",
            "comments_url": "https://api.github.com/repos/octo-org/hello-world/comments{/number}",
            "commits_url": "https://api.github.com/repos/octo-org/hello-world/commits{/sha}",
            "compare_url": "https://api.github.com/repos/octo-org/hello-world/compare/{base}...{head}",
            "contents_url": "https://api.github.com/repos/octo-org/hello-world/contents/{+path}",
            "contributors_url": "https://api.github.com/repos/octo-org/hello-world/contributors",
            "deployments_url": "https://api.github.com/repos/octo-org/hello-world/deployments",
            "downloads_url": "https://api.github.com/repos/octo-org/hello-world/downloads",
            "events_url": "https://api.github.com/repos/octo-org/hello-world/events",
            "forks_url": "https://api.github.com/repos/octo-org/hello-world/forks",
            "git_commits_url": "https://api.github.com/repos/octo-org/hello-world/git/commits{/sha}",
            "git_refs_url": "https://api.github.com/repos/octo-org/hello-world/git/refs{/sha}",
            "git_tags_url": "https://api.github.com/repos/octo-org/hello-world/git/tags{/sha}",
            "hooks_url": "https://api.github.com/repos/octo-org/hello-world/hooks",
            "issue_comment_url": "https://api.github.com/repos/octo-org/hello-world/issues/comments{/number}",
            "issue_events_url": "https://api.github.com/repos/octo-org/hello-world/issues/events{/number}",
            "issues_url": "https://api.github.com/repos/octo-org/hello-world/issues{/number}",
            "keys_url": "https://api.github.com/repos/octo-org/hello-world/keys{/key_id}",
            "labels_url": "https://api.github.com/repos/octo-org/hello-world/labels{/name}",
            "languages_url": "https://api.github.com/repos/octo-org/hello-world/languages",
            "merges_url": "https://api.github.com/repos/octo-org/hello-world/merges",
            "milestones_url": "https://api.github.com/repos/octo-org/hello-world/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/octo-org/hello-world/notifications{?since,all,participating}",
            "pulls_url": "https://api.github.com/repos/octo-org/hello-world/pulls{/number}",
            "releases_url": "https://api.github.com/repos/octo-org/hello-world/releases{/id}",
            "stargazers_url": "https://api.github.com/repos/octo-org/hello-world/stargazers",
            "statuses_url": "https://api.github.com/repos/octo-org/hello-world/statuses/{sha}",
            "subscribers_url": "https://api.github.com/repos/octo-org/hello-world/subscribers",
            "subscription_url": "https://api.github.com/repos/octo-org/hello-world/subscription",
            "tags_url": "https://api.github.com/repos/octo-org/hello-world/tags",
            "teams_url": "https://api.github.com/repos/octo-org/hello-world/teams",
            "trees_url": "https://api.github.com/repos/octo-org/hello-world/git/trees{/sha}",
        },
    },
]


class GitHubAsyncRESTDependabotTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTDependabot

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
            "/enterprises/foo/dependabot/alerts",
            params={"per_page": "100", "sort": "created", "direction": "desc"},
        )

    async def test_enterprise_alerts_state(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.enterprise_alerts("foo", state=AlertState.FIXED)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/enterprises/foo/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "state": "fixed",
            },
        )

    async def test_enterprise_alerts_severity(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.enterprise_alerts("foo", severity=Severity.CRITICAL)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/enterprises/foo/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "severity": "critical",
            },
        )

    async def test_enterprise_alerts_ecosystem(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.enterprise_alerts("foo", ecosystem="pip"))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/enterprises/foo/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "ecosystem": "pip",
            },
        )

    async def test_enterprise_alerts_scope(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.enterprise_alerts("foo", scope=DependencyScope.RUNTIME)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/enterprises/foo/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "scope": "runtime",
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
            "/enterprises/foo/dependabot/alerts",
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
            "/enterprises/foo/dependabot/alerts",
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
            "/orgs/foo/dependabot/alerts",
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
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "state": "fixed",
            },
        )

    async def test_organization_alerts_severity(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.organization_alerts("foo", severity=Severity.CRITICAL)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "severity": "critical",
            },
        )

    async def test_organization_alerts_ecosystem(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.organization_alerts("foo", ecosystem="pip"))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "ecosystem": "pip",
            },
        )

    async def test_organization_alerts_scope(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.organization_alerts("foo", scope=DependencyScope.RUNTIME)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/orgs/foo/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "scope": "runtime",
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
            "/orgs/foo/dependabot/alerts",
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
            "/orgs/foo/dependabot/alerts",
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
            "/repos/foo/bar/dependabot/alerts",
            params={"per_page": "100", "sort": "created", "direction": "desc"},
        )

    async def test_alerts_state(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", state=AlertState.FIXED))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "state": "fixed",
            },
        )

    async def test_alerts_severity(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", severity=Severity.CRITICAL))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "severity": "critical",
            },
        )

    async def test_alerts_ecosystem(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.alerts("foo/bar", ecosystem="pip"))
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "ecosystem": "pip",
            },
        )

    async def test_alerts_scope(self):
        response = create_response()
        response.json.return_value = ALERTS

        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(
            self.api.alerts("foo/bar", scope=DependencyScope.RUNTIME)
        )
        alert = await anext(async_it)
        self.assertEqual(alert.number, 2)
        alert = await anext(async_it)
        self.assertEqual(alert.number, 1)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "desc",
                "scope": "runtime",
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
            "/repos/foo/bar/dependabot/alerts",
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
            "/repos/foo/bar/dependabot/alerts",
            params={
                "per_page": "100",
                "sort": "created",
                "direction": "asc",
            },
        )

    async def test_alert(self):
        response = create_response()
        response.json.return_value = {
            "number": 1,
            "state": "open",
            "dependency": {
                "package": {"ecosystem": "pip", "name": "ansible"},
                "manifest_path": "path/to/requirements.txt",
                "scope": "runtime",
            },
            "security_advisory": {
                "ghsa_id": "GHSA-8f4m-hccc-8qph",
                "cve_id": "CVE-2021-20191",
                "summary": "Insertion of Sensitive Information into Log File in ansible",
                "description": "A flaw was found in ansible. Credentials, such as secrets, are being disclosed in console log by default and not protected by no_log feature when using those modules. An attacker can take advantage of this information to steal those credentials. The highest threat from this vulnerability is to data confidentiality.",
                "vulnerabilities": [
                    {
                        "package": {"ecosystem": "pip", "name": "ansible"},
                        "severity": "medium",
                        "vulnerable_version_range": ">= 2.9.0, < 2.9.18",
                        "first_patched_version": {"identifier": "2.9.18"},
                    },
                    {
                        "package": {"ecosystem": "pip", "name": "ansible"},
                        "severity": "medium",
                        "vulnerable_version_range": "< 2.8.19",
                        "first_patched_version": {"identifier": "2.8.19"},
                    },
                    {
                        "package": {"ecosystem": "pip", "name": "ansible"},
                        "severity": "medium",
                        "vulnerable_version_range": ">= 2.10.0, < 2.10.7",
                        "first_patched_version": {"identifier": "2.10.7"},
                    },
                ],
                "severity": "medium",
                "cvss": {
                    "vector_string": "CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N",
                    "score": 5.5,
                },
                "cwes": [
                    {
                        "cwe_id": "CWE-532",
                        "name": "Insertion of Sensitive Information into Log File",
                    }
                ],
                "identifiers": [
                    {"type": "GHSA", "value": "GHSA-8f4m-hccc-8qph"},
                    {"type": "CVE", "value": "CVE-2021-20191"},
                ],
                "references": [
                    {"url": "https://nvd.nist.gov/vuln/detail/CVE-2021-20191"},
                    {
                        "url": "https://access.redhat.com/security/cve/cve-2021-20191"
                    },
                    {
                        "url": "https://bugzilla.redhat.com/show_bug.cgi?id=1916813"
                    },
                ],
                "published_at": "2021-06-01T17:38:00Z",
                "updated_at": "2021-08-12T23:06:00Z",
                "withdrawn_at": None,
            },
            "security_vulnerability": {
                "package": {"ecosystem": "pip", "name": "ansible"},
                "severity": "medium",
                "vulnerable_version_range": "< 2.8.19",
                "first_patched_version": {"identifier": "2.8.19"},
            },
            "url": "https://api.github.com/repos/octocat/hello-world/dependabot/alerts/1",
            "html_url": "https://github.com/octocat/hello-world/security/dependabot/1",
            "created_at": "2022-06-14T15:21:52Z",
            "updated_at": "2022-06-14T15:21:52Z",
            "dismissed_at": None,
            "dismissed_by": None,
            "dismissed_reason": None,
            "dismissed_comment": None,
            "fixed_at": None,
        }
        self.client.get.return_value = response

        alert = await self.api.alert(
            "foo/bar",
            1,
        )

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/dependabot/alerts/1",
        )

        self.assertEqual(alert.number, 1)

    async def test_update(self):
        response = create_response()
        response.json.return_value = {
            "number": 1,
            "state": "open",
            "dependency": {
                "package": {"ecosystem": "pip", "name": "ansible"},
                "manifest_path": "path/to/requirements.txt",
                "scope": "runtime",
            },
            "security_advisory": {
                "ghsa_id": "GHSA-8f4m-hccc-8qph",
                "cve_id": "CVE-2021-20191",
                "summary": "Insertion of Sensitive Information into Log File in ansible",
                "description": "A flaw was found in ansible. Credentials, such as secrets, are being disclosed in console log by default and not protected by no_log feature when using those modules. An attacker can take advantage of this information to steal those credentials. The highest threat from this vulnerability is to data confidentiality.",
                "vulnerabilities": [
                    {
                        "package": {"ecosystem": "pip", "name": "ansible"},
                        "severity": "medium",
                        "vulnerable_version_range": ">= 2.9.0, < 2.9.18",
                        "first_patched_version": {"identifier": "2.9.18"},
                    },
                    {
                        "package": {"ecosystem": "pip", "name": "ansible"},
                        "severity": "medium",
                        "vulnerable_version_range": "< 2.8.19",
                        "first_patched_version": {"identifier": "2.8.19"},
                    },
                    {
                        "package": {"ecosystem": "pip", "name": "ansible"},
                        "severity": "medium",
                        "vulnerable_version_range": ">= 2.10.0, < 2.10.7",
                        "first_patched_version": {"identifier": "2.10.7"},
                    },
                ],
                "severity": "medium",
                "cvss": {
                    "vector_string": "CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N",
                    "score": 5.5,
                },
                "cwes": [
                    {
                        "cwe_id": "CWE-532",
                        "name": "Insertion of Sensitive Information into Log File",
                    }
                ],
                "identifiers": [
                    {"type": "GHSA", "value": "GHSA-8f4m-hccc-8qph"},
                    {"type": "CVE", "value": "CVE-2021-20191"},
                ],
                "references": [
                    {"url": "https://nvd.nist.gov/vuln/detail/CVE-2021-20191"},
                    {
                        "url": "https://access.redhat.com/security/cve/cve-2021-20191"
                    },
                    {
                        "url": "https://bugzilla.redhat.com/show_bug.cgi?id=1916813"
                    },
                ],
                "published_at": "2021-06-01T17:38:00Z",
                "updated_at": "2021-08-12T23:06:00Z",
                "withdrawn_at": None,
            },
            "security_vulnerability": {
                "package": {"ecosystem": "pip", "name": "ansible"},
                "severity": "medium",
                "vulnerable_version_range": "< 2.8.19",
                "first_patched_version": {"identifier": "2.8.19"},
            },
            "url": "https://api.github.com/repos/octocat/hello-world/dependabot/alerts/1",
            "html_url": "https://github.com/octocat/hello-world/security/dependabot/1",
            "created_at": "2022-06-14T15:21:52Z",
            "updated_at": "2022-06-14T15:21:52Z",
            "dismissed_at": None,
            "dismissed_by": None,
            "dismissed_reason": None,
            "dismissed_comment": None,
            "fixed_at": None,
        }
        self.client.patch.return_value = response

        alert = await self.api.update_alert(
            "foo/bar",
            1,
            AlertState.DISMISSED,
            dismissed_reason=DismissedReason.NOT_USED,
            dismissed_comment="Dependency is not used.",
        )

        self.client.patch.assert_awaited_once_with(
            "/repos/foo/bar/dependabot/alerts/1",
            data={
                "state": "dismissed",
                "dismissed_reason": "not_used",
                "dismissed_comment": "Dependency is not used.",
            },
        )

        self.assertEqual(alert.number, 1)
