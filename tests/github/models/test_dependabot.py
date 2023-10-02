# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

import unittest
from datetime import datetime, timezone

from pontos.github.models.dependabot import (
    AlertState,
    DependabotAlert,
    DependencyScope,
    DismissedReason,
    IdentifierType,
    SecurityAdvisory,
    Severity,
    Vulnerability,
    VulnerablePackage,
)


class VulnerablePackageTestCase(unittest.TestCase):
    def test_from_dict(self):
        package = VulnerablePackage.from_dict(
            {
                "ecosystem": "pip",
                "name": "django",
            }
        )

        self.assertEqual(package.ecosystem, "pip")
        self.assertEqual(package.name, "django")


class VulnerabilityTestCase(unittest.TestCase):
    def test_from_dict(self):
        vulnerability = Vulnerability.from_dict(
            {
                "package": {
                    "ecosystem": "pip",
                    "name": "django",
                },
                "severity": "high",
                "vulnerable_version_range": ">= 2.0.0, < 2.0.2",
                "first_patched_version": {"identifier": "2.0.2"},
            }
        )

        self.assertEqual(vulnerability.package.ecosystem, "pip")
        self.assertEqual(vulnerability.package.name, "django")
        self.assertEqual(vulnerability.severity, Severity.HIGH)
        self.assertEqual(
            vulnerability.vulnerable_version_range, ">= 2.0.0, < 2.0.2"
        )
        self.assertEqual(
            vulnerability.first_patched_version.identifier, "2.0.2"
        )

        vulnerability = Vulnerability.from_dict(
            {
                "package": {
                    "ecosystem": "pip",
                    "name": "django",
                },
                "severity": "high",
                "vulnerable_version_range": ">= 2.0.0, < 2.0.2",
            }
        )

        self.assertEqual(vulnerability.package.ecosystem, "pip")
        self.assertEqual(vulnerability.package.name, "django")
        self.assertEqual(vulnerability.severity, Severity.HIGH)
        self.assertIsNone(vulnerability.first_patched_version)


SECURITY_ADVISORY = {
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
}


class SecurityAdvisoryTestCase(unittest.TestCase):
    def test_from_dict(self):
        advisory = SecurityAdvisory.from_dict(SECURITY_ADVISORY)

        self.assertEqual(advisory.cve_id, "CVE-2018-6188")
        self.assertEqual(advisory.ghsa_id, "GHSA-rf4j-j272-fj86")
        self.assertEqual(
            advisory.cvss.vector_string,
            "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        )
        self.assertEqual(advisory.cvss.score, 7.5)
        self.assertRegex(advisory.summary, "^Django allows remote attacker.*")
        self.assertRegex(
            advisory.description,
            "^django\.contrib\.auth\.forms\.AuthenticationForm in Django 2\.0.*",
        )

        self.assertEqual(len(advisory.vulnerabilities), 2)
        vuln = advisory.vulnerabilities[0]
        self.assertEqual(vuln.package.ecosystem, "pip")
        self.assertEqual(vuln.package.name, "django")
        self.assertEqual(vuln.severity, Severity.HIGH)
        self.assertEqual(vuln.vulnerable_version_range, ">= 2.0.0, < 2.0.2")
        self.assertEqual(vuln.first_patched_version.identifier, "2.0.2")

        vuln = advisory.vulnerabilities[1]
        self.assertEqual(vuln.package.ecosystem, "pip")
        self.assertEqual(vuln.package.name, "django")
        self.assertEqual(vuln.severity, Severity.HIGH)
        self.assertEqual(vuln.vulnerable_version_range, ">= 1.11.8, < 1.11.10")
        self.assertEqual(vuln.first_patched_version.identifier, "1.11.10")

        self.assertEqual(len(advisory.cwes), 1)
        cwe = advisory.cwes[0]
        self.assertEqual(cwe.cwe_id, "CWE-200")
        self.assertEqual(
            cwe.name,
            "Exposure of Sensitive Information to an Unauthorized Actor",
        )

        self.assertEqual(len(advisory.identifiers), 2)
        identifier = advisory.identifiers[0]
        self.assertEqual(identifier.type, IdentifierType.GHSA)
        self.assertEqual(identifier.value, "GHSA-rf4j-j272-fj86")

        identifier = advisory.identifiers[1]
        self.assertEqual(identifier.type, IdentifierType.CVE)
        self.assertEqual(identifier.value, "CVE-2018-6188")

        self.assertEqual(len(advisory.references), 5)
        self.assertEqual(
            advisory.references[0].url,
            "https://nvd.nist.gov/vuln/detail/CVE-2018-6188",
        )

        self.assertEqual(
            advisory.published_at,
            datetime(2018, 10, 3, 21, 13, 54, tzinfo=timezone.utc),
        )
        self.assertEqual(
            advisory.updated_at,
            datetime(2022, 4, 26, 18, 35, 37, tzinfo=timezone.utc),
        )

        self.assertIsNone(advisory.withdrawn_at)


DEPENDABOT_ALERT = {
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
}


class DependabotAlertTestCase(unittest.TestCase):
    def test_from_dict(self):
        alert = DependabotAlert.from_dict(DEPENDABOT_ALERT)

        self.assertEqual(alert.number, 2)
        self.assertEqual(alert.state, AlertState.DISMISSED)

        self.assertEqual(alert.dependency.package.ecosystem, "pip")
        self.assertEqual(alert.dependency.package.name, "django")
        self.assertEqual(
            alert.dependency.manifest_path, "path/to/requirements.txt"
        )
        self.assertEqual(alert.dependency.scope, DependencyScope.RUNTIME)

        self.assertEqual(alert.security_advisory.cve_id, "CVE-2018-6188")
        self.assertEqual(alert.security_advisory.ghsa_id, "GHSA-rf4j-j272-fj86")
        self.assertEqual(
            alert.security_advisory.cvss.vector_string,
            "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        )
        self.assertEqual(alert.security_advisory.cvss.score, 7.5)
        self.assertRegex(
            alert.security_advisory.summary, "^Django allows remote attacker.*"
        )
        self.assertRegex(
            alert.security_advisory.description,
            "^django\.contrib\.auth\.forms\.AuthenticationForm in Django 2\.0.*",
        )

        self.assertEqual(len(alert.security_advisory.vulnerabilities), 2)
        vuln = alert.security_advisory.vulnerabilities[0]
        self.assertEqual(vuln.package.ecosystem, "pip")
        self.assertEqual(vuln.package.name, "django")
        self.assertEqual(vuln.severity, Severity.HIGH)
        self.assertEqual(vuln.vulnerable_version_range, ">= 2.0.0, < 2.0.2")
        self.assertEqual(vuln.first_patched_version.identifier, "2.0.2")

        vuln = alert.security_advisory.vulnerabilities[1]
        self.assertEqual(vuln.package.ecosystem, "pip")
        self.assertEqual(vuln.package.name, "django")
        self.assertEqual(vuln.severity, Severity.HIGH)
        self.assertEqual(vuln.vulnerable_version_range, ">= 1.11.8, < 1.11.10")
        self.assertEqual(vuln.first_patched_version.identifier, "1.11.10")

        self.assertEqual(len(alert.security_advisory.cwes), 1)
        cwe = alert.security_advisory.cwes[0]
        self.assertEqual(cwe.cwe_id, "CWE-200")
        self.assertEqual(
            cwe.name,
            "Exposure of Sensitive Information to an Unauthorized Actor",
        )

        self.assertEqual(len(alert.security_advisory.identifiers), 2)
        identifier = alert.security_advisory.identifiers[0]
        self.assertEqual(identifier.type, IdentifierType.GHSA)
        self.assertEqual(identifier.value, "GHSA-rf4j-j272-fj86")

        identifier = alert.security_advisory.identifiers[1]
        self.assertEqual(identifier.type, IdentifierType.CVE)
        self.assertEqual(identifier.value, "CVE-2018-6188")

        self.assertEqual(len(alert.security_advisory.references), 5)
        self.assertEqual(
            alert.security_advisory.references[0].url,
            "https://nvd.nist.gov/vuln/detail/CVE-2018-6188",
        )

        self.assertEqual(
            alert.security_advisory.published_at,
            datetime(2018, 10, 3, 21, 13, 54, tzinfo=timezone.utc),
        )
        self.assertEqual(
            alert.security_advisory.updated_at,
            datetime(2022, 4, 26, 18, 35, 37, tzinfo=timezone.utc),
        )

        self.assertIsNone(alert.security_advisory.withdrawn_at)

        self.assertEqual(alert.security_vulnerability.package.ecosystem, "pip")
        self.assertEqual(alert.security_vulnerability.package.name, "django")
        self.assertEqual(
            alert.security_vulnerability.vulnerable_version_range,
            ">= 2.0.0, < 2.0.2",
        )
        self.assertEqual(
            alert.security_vulnerability.first_patched_version.identifier,
            "2.0.2",
        )
        self.assertEqual(alert.security_vulnerability.severity, Severity.HIGH)

        self.assertEqual(
            alert.url,
            "https://api.github.com/repos/octo-org/octo-repo/dependabot/alerts/2",
        )
        self.assertEqual(
            alert.html_url,
            "https://github.com/octo-org/octo-repo/security/dependabot/2",
        )

        self.assertEqual(
            alert.created_at,
            datetime(2022, 6, 15, 7, 43, 3, tzinfo=timezone.utc),
        )
        self.assertEqual(
            alert.updated_at,
            datetime(2022, 8, 23, 14, 29, 47, tzinfo=timezone.utc),
        )
        self.assertEqual(
            alert.dismissed_at,
            datetime(2022, 8, 23, 14, 29, 47, tzinfo=timezone.utc),
        )

        self.assertEqual(alert.dismissed_by.login, "octocat")
        self.assertEqual(alert.dismissed_reason, DismissedReason.TOLERABLE_RISK)
        self.assertEqual(
            alert.dismissed_comment,
            "This alert is accurate but we use a sanitizer.",
        )

        self.assertIsNone(alert.fixed_at)
        self.assertIsNone(alert.auto_dismissed_at)

        self.assertEqual(alert.repository.id, 217723378)
