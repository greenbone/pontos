# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

import unittest
from datetime import datetime, timezone

from pontos.github.models.code_scanning import (
    AlertState,
    Analysis,
    CodeQLDatabase,
    CodeScanningAlert,
    DefaultSetup,
    DefaultSetupState,
    Instance,
    Language,
    Location,
    QuerySuite,
    Rule,
    SarifProcessingStatus,
    SarifUploadInformation,
    Severity,
    Tool,
)

ALERT = {
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
    "dismissed_comment": "This alert is not actually correct, because there's "
    "a sanitizer included in the library.",
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
}


class RuleTestCase(unittest.TestCase):
    def test_from_dict(self):
        rule = Rule.from_dict(
            {
                "id": "js/zipslip",
                "severity": "error",
                "tags": ["security", "external/cwe/cwe-022"],
                "description": "Arbitrary file write during zip extraction",
                "name": "js/zipslip",
            }
        )

        self.assertEqual(rule.id, "js/zipslip")
        self.assertEqual(rule.name, "js/zipslip")
        self.assertEqual(rule.severity, Severity.ERROR)
        self.assertEqual(len(rule.tags), 2)
        self.assertEqual(rule.tags, ["security", "external/cwe/cwe-022"])
        self.assertEqual(
            rule.description, "Arbitrary file write during zip extraction"
        )


class LocationTestCase(unittest.TestCase):
    def test_from_dict(self):
        location = Location.from_dict(
            {
                "path": "lib/ab12-gen.js",
                "start_line": 917,
                "end_line": 917,
                "start_column": 7,
                "end_column": 18,
            }
        )

        self.assertEqual(location.path, "lib/ab12-gen.js")
        self.assertEqual(location.start_line, 917)
        self.assertEqual(location.end_line, 917)
        self.assertEqual(location.start_column, 7)
        self.assertEqual(location.end_column, 18)


class InstanceTestCase(unittest.TestCase):
    def test_from_dict(self):
        instance = Instance.from_dict(
            {
                "ref": "refs/heads/main",
                "analysis_key": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
                "category": ".github/workflows/codeql-analysis.yml:CodeQL-Build",
                "environment": "{}",
                "state": "open",
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
                "classifications": [],
            }
        )

        self.assertEqual(instance.ref, "refs/heads/main")
        self.assertEqual(
            instance.analysis_key,
            ".github/workflows/codeql-analysis.yml:CodeQL-Build",
        )
        self.assertEqual(
            instance.category,
            ".github/workflows/codeql-analysis.yml:CodeQL-Build",
        )
        self.assertEqual(instance.environment, "{}")
        self.assertEqual(instance.state, AlertState.OPEN)
        self.assertEqual(
            instance.commit_sha, "39406e42cb832f683daa691dd652a8dc36ee8930"
        )
        self.assertEqual(
            instance.message.text, "This path depends on a user-provided value."
        )

        self.assertEqual(instance.location.path, "lib/ab12-gen.js")
        self.assertEqual(instance.location.start_line, 917)
        self.assertEqual(instance.location.end_line, 917)
        self.assertEqual(instance.location.start_column, 7)
        self.assertEqual(instance.location.end_column, 18)

        self.assertEqual(len(instance.classifications), 0)


class ToolTestCase(unittest.TestCase):
    def test_from_dict(self):
        tool = Tool.from_dict(
            {"name": "CodeQL", "guid": None, "version": "2.4.0"}
        )

        self.assertEqual(tool.name, "CodeQL")
        self.assertEqual(tool.version, "2.4.0")
        self.assertIsNone(tool.guid)


class CodeScanningAlertTestCase(unittest.TestCase):
    def test_from_dict(self):
        alert = CodeScanningAlert.from_dict(ALERT)

        self.assertEqual(alert.number, 3)
        self.assertEqual(
            alert.created_at,
            datetime(2020, 2, 13, 12, 29, 18, tzinfo=timezone.utc),
        )
        self.assertEqual(
            alert.url,
            "https://api.github.com/repos/octocat/hello-world/code-scanning/alerts/3",
        )
        self.assertEqual(
            alert.html_url,
            "https://github.com/octocat/hello-world/code-scanning/3",
        )
        self.assertEqual(alert.state, AlertState.DISMISSED)
        self.assertEqual(
            alert.dismissed_at,
            datetime(2020, 2, 14, 12, 29, 18, tzinfo=timezone.utc),
        )
        self.assertEqual(alert.dismissed_by.login, "octocat")
        self.assertEqual(
            alert.dismissed_comment,
            "This alert is not actually correct, because there's a sanitizer "
            "included in the library.",
        )
        self.assertEqual(alert.rule.id, "js/zipslip")
        self.assertEqual(alert.tool.name, "CodeQL")
        self.assertEqual(alert.most_recent_instance.ref, "refs/heads/main")
        self.assertEqual(
            alert.most_recent_instance.location.path, "lib/ab12-gen.js"
        )
        self.assertEqual(
            alert.instances_url,
            "https://api.github.com/repos/octocat/hello-world/code-scanning/alerts/3/instances",
        )
        self.assertEqual(alert.repository.id, 1296269)


class AnalysisTestCase(unittest.TestCase):
    def test_from_dict(self):
        analysis = Analysis.from_dict(
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
            }
        )

        self.assertEqual(analysis.ref, "refs/heads/main")
        self.assertEqual(
            analysis.commit_sha, "d99612c3e1f2970085cfbaeadf8f010ef69bad83"
        )
        self.assertEqual(
            analysis.analysis_key,
            ".github/workflows/codeql-analysis.yml:analyze",
        )
        self.assertEqual(analysis.environment, '{"language":"python"}')
        self.assertEqual(analysis.error, "")
        self.assertEqual(analysis.warning, "")
        self.assertEqual(
            analysis.category,
            ".github/workflows/codeql-analysis.yml:analyze/language:python",
        )
        self.assertEqual(
            analysis.created_at,
            datetime(2020, 8, 27, 15, 5, 21, tzinfo=timezone.utc),
        )
        self.assertEqual(analysis.results_count, 17)
        self.assertEqual(analysis.rules_count, 49)
        self.assertEqual(analysis.id, 201)
        self.assertEqual(
            analysis.url,
            "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses/201",
        )
        self.assertEqual(
            analysis.sarif_id, "6c81cd8e-b078-4ac3-a3be-1dad7dbd0b53"
        )
        self.assertEqual(analysis.tool.name, "CodeQL")
        self.assertEqual(analysis.tool.version, "2.4.0")
        self.assertIsNone(analysis.tool.guid)
        self.assertTrue(analysis.deletable)


class CodeQLDatabaseTestCase(unittest.TestCase):
    def test_from_dict(self):
        db = CodeQLDatabase.from_dict(
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
                "commit_oid": "12345678901234567000",
            }
        )

        self.assertEqual(db.id, 1)
        self.assertEqual(db.name, "database.zip")
        self.assertEqual(db.language, "java")
        self.assertEqual(db.uploader.id, 1)
        self.assertEqual(db.content_type, "application/zip")
        self.assertEqual(db.size, 1024)
        self.assertEqual(
            db.created_at,
            datetime(2022, 9, 12, 12, 14, 32, tzinfo=timezone.utc),
        )
        self.assertEqual(
            db.updated_at,
            datetime(2022, 9, 12, 12, 14, 32, tzinfo=timezone.utc),
        )
        self.assertEqual(
            db.url,
            "https://api.github.com/repos/octocat/Hello-World/code-scanning/codeql/databases/java",
        )
        self.assertEqual(db.commit_oid, "12345678901234567000")


class DefaultSetupTestCase(unittest.TestCase):
    def test_from_dict(self):
        setup = DefaultSetup.from_dict(
            {
                "state": "configured",
                "languages": ["ruby", "python"],
                "query_suite": "default",
                "updated_at": "2023-01-19T11:21:34Z",
                "schedule": "weekly",
            }
        )

        self.assertEqual(setup.state, DefaultSetupState.CONFIGURED)
        self.assertEqual(setup.languages, [Language.RUBY, Language.PYTHON])
        self.assertEqual(setup.query_suite, QuerySuite.DEFAULT)
        self.assertEqual(
            setup.updated_at,
            datetime(2023, 1, 19, 11, 21, 34, tzinfo=timezone.utc),
        )
        self.assertEqual(setup.schedule, "weekly")


class SarifUploadInformationTestCase(unittest.TestCase):
    def test_from_dict(self):
        sarif = SarifUploadInformation.from_dict(
            {
                "processing_status": "complete",
                "analyses_url": "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses?sarif_id=47177e22-5596-11eb-80a1-c1e54ef945c6",
            }
        )
        self.assertEqual(
            sarif.processing_status, SarifProcessingStatus.COMPLETE
        )
        self.assertEqual(
            sarif.analyses_url,
            "https://api.github.com/repos/octocat/hello-world/code-scanning/analyses?sarif_id=47177e22-5596-11eb-80a1-c1e54ef945c6",
        )
        self.assertIsNone(sarif.errors)
