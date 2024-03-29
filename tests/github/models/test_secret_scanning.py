# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

import unittest
from datetime import datetime, timezone

from pontos.github.models.secret_scanning import (
    AlertState,
    Resolution,
    SecretScanningAlert,
)

ALERT = {
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
}


class SecretScanningAlertTestCase(unittest.TestCase):
    def test_from_dict(self):
        alert = SecretScanningAlert.from_dict(ALERT)

        self.assertEqual(alert.number, 2)
        self.assertEqual(
            alert.url,
            "https://api.github.com/repos/owner/private-repo/secret-scanning/alerts/2",
        )
        self.assertEqual(
            alert.html_url,
            "https://github.com/owner/private-repo/security/secret-scanning/2",
        )
        self.assertEqual(
            alert.locations_url,
            "https://api.github.com/repos/owner/private-repo/secret-scanning/alerts/2/locations",
        )
        self.assertEqual(alert.state, AlertState.RESOLVED)
        self.assertEqual(alert.secret_type, "adafruit_io_key")
        self.assertEqual(alert.secret_type_display_name, "Adafruit IO Key")
        self.assertEqual(alert.secret, "aio_XXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        self.assertEqual(alert.repository.id, 1296269)
        self.assertEqual(
            alert.created_at,
            datetime(2020, 11, 6, 18, 48, 51, tzinfo=timezone.utc),
        )
        self.assertIsNone(alert.updated_at)

        self.assertEqual(alert.resolution, Resolution.FALSE_POSITIVE)
        self.assertEqual(alert.resolution_comment, "Example comment")
        self.assertEqual(
            alert.resolved_at,
            datetime(2020, 11, 7, 2, 47, 13, tzinfo=timezone.utc),
        )
        self.assertEqual(alert.resolved_by.login, "monalisa")

        self.assertTrue(alert.push_protection_bypassed)
        self.assertEqual(alert.push_protection_bypassed_by.login, "monalisa")
        self.assertEqual(
            alert.push_protection_bypassed_at,
            datetime(2020, 11, 6, 21, 48, 51, tzinfo=timezone.utc),
        )
