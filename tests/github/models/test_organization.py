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

# pylint: disable=line-too-long, redefined-builtin

import unittest
from datetime import datetime, timezone

from pontos.github.models.organization import License, Repository


class LicenseTestCase(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "key": "gpl-3.0",
            "name": "GNU General Public License v3.0",
            "spdx_id": "GPL-3.0",
            "url": "https://api.github.com/licenses/gpl-3.0",
            "node_id": "MDc6TGljZW5zZTk=",
        }

        license = License.from_dict(data)

        self.assertEqual(license.key, "gpl-3.0")
        self.assertEqual(license.name, "GNU General Public License v3.0")
        self.assertEqual(license.spdx_id, "GPL-3.0")
        self.assertEqual(license.url, "https://api.github.com/licenses/gpl-3.0")
        self.assertEqual(license.node_id, "MDc6TGljZW5zZTk=")


class RepositoryTestCase(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "id": 103647077,
            "node_id": "MDEwOlJlcG9zaXRvcnkxMDM2NDcwNzc=",
            "name": "gvm-tools",
            "full_name": "greenbone/gvm-tools",
            "private": False,
            "owner": {
                "login": "greenbone",
                "id": 31986857,
                "node_id": "MDEyOk9yZ2FuaXphdGlvbjMxOTg2ODU3",
                "avatar_url": "https://avatars.githubusercontent.com/u/31986857?v=4",
                "gravatar_id": "",
                "url": "https://api.github.com/users/greenbone",
                "html_url": "https://github.com/greenbone",
                "followers_url": "https://api.github.com/users/greenbone/followers",
                "following_url": "https://api.github.com/users/greenbone/following{/other_user}",
                "gists_url": "https://api.github.com/users/greenbone/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/greenbone/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/greenbone/subscriptions",
                "organizations_url": "https://api.github.com/users/greenbone/orgs",
                "repos_url": "https://api.github.com/users/greenbone/repos",
                "events_url": "https://api.github.com/users/greenbone/events{/privacy}",
                "received_events_url": "https://api.github.com/users/greenbone/received_events",
                "type": "Organization",
                "site_admin": False,
            },
            "html_url": "https://github.com/greenbone/gvm-tools",
            "description": "Remote control your Greenbone Community Edition or Greenbone Enterprise Appliance",
            "fork": False,
            "url": "https://api.github.com/repos/greenbone/gvm-tools",
            "forks_url": "https://api.github.com/repos/greenbone/gvm-tools/forks",
            "keys_url": "https://api.github.com/repos/greenbone/gvm-tools/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/greenbone/gvm-tools/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/greenbone/gvm-tools/teams",
            "hooks_url": "https://api.github.com/repos/greenbone/gvm-tools/hooks",
            "issue_events_url": "https://api.github.com/repos/greenbone/gvm-tools/issues/events{/number}",
            "events_url": "https://api.github.com/repos/greenbone/gvm-tools/events",
            "assignees_url": "https://api.github.com/repos/greenbone/gvm-tools/assignees{/user}",
            "branches_url": "https://api.github.com/repos/greenbone/gvm-tools/branches{/branch}",
            "tags_url": "https://api.github.com/repos/greenbone/gvm-tools/tags",
            "blobs_url": "https://api.github.com/repos/greenbone/gvm-tools/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/greenbone/gvm-tools/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/greenbone/gvm-tools/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/greenbone/gvm-tools/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/greenbone/gvm-tools/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/greenbone/gvm-tools/languages",
            "stargazers_url": "https://api.github.com/repos/greenbone/gvm-tools/stargazers",
            "contributors_url": "https://api.github.com/repos/greenbone/gvm-tools/contributors",
            "subscribers_url": "https://api.github.com/repos/greenbone/gvm-tools/subscribers",
            "subscription_url": "https://api.github.com/repos/greenbone/gvm-tools/subscription",
            "commits_url": "https://api.github.com/repos/greenbone/gvm-tools/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/greenbone/gvm-tools/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/greenbone/gvm-tools/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/greenbone/gvm-tools/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/greenbone/gvm-tools/contents/{+path}",
            "compare_url": "https://api.github.com/repos/greenbone/gvm-tools/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/greenbone/gvm-tools/merges",
            "archive_url": "https://api.github.com/repos/greenbone/gvm-tools/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/greenbone/gvm-tools/downloads",
            "issues_url": "https://api.github.com/repos/greenbone/gvm-tools/issues{/number}",
            "pulls_url": "https://api.github.com/repos/greenbone/gvm-tools/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/greenbone/gvm-tools/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/greenbone/gvm-tools/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/greenbone/gvm-tools/labels{/name}",
            "releases_url": "https://api.github.com/repos/greenbone/gvm-tools/releases{/id}",
            "deployments_url": "https://api.github.com/repos/greenbone/gvm-tools/deployments",
            "created_at": "2017-09-15T10:54:42Z",
            "updated_at": "2022-11-01T07:45:33Z",
            "pushed_at": "2022-11-07T09:21:30Z",
            "git_url": "git://github.com/greenbone/gvm-tools.git",
            "ssh_url": "git@github.com:greenbone/gvm-tools.git",
            "clone_url": "https://github.com/greenbone/gvm-tools.git",
            "svn_url": "https://github.com/greenbone/gvm-tools",
            "homepage": "https://greenbone.github.io/gvm-tools/",
            "size": 3461,
            "stargazers_count": 128,
            "watchers_count": 128,
            "language": "Python",
            "has_issues": True,
            "has_projects": False,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": True,
            "has_discussions": False,
            "forks_count": 74,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 3,
            "license": {
                "key": "gpl-3.0",
                "name": "GNU General Public License v3.0",
                "spdx_id": "GPL-3.0",
                "url": "https://api.github.com/licenses/gpl-3.0",
                "node_id": "MDc6TGljZW5zZTk=",
            },
            "allow_forking": True,
            "is_template": False,
            "web_commit_signoff_required": False,
            "topics": [
                "gmp",
                "gmp-scripts",
                "greenbone",
                "greenbone-vulnerability-manager",
                "gvm",
                "gvm-cli",
                "gvm-pyshell",
                "gvm-script",
                "omp",
                "openvas",
                "openvas-cli",
                "osp",
                "python",
                "vulnerability",
                "vulnerability-assessment",
                "vulnerability-management",
            ],
            "visibility": "public",
            "forks": 74,
            "open_issues": 3,
            "watchers": 128,
            "default_branch": "main",
        }

        repo = Repository.from_dict(data)

        self.assertEqual(repo.id, 103647077)
        self.assertEqual(repo.node_id, "MDEwOlJlcG9zaXRvcnkxMDM2NDcwNzc=")
        self.assertEqual(repo.name, "gvm-tools")
        self.assertEqual(repo.full_name, "greenbone/gvm-tools")
        self.assertEqual(repo.private, False)
        self.assertEqual(repo.owner.login, "greenbone")
        self.assertEqual(repo.owner.id, 31986857)
        self.assertEqual(repo.owner.node_id, "MDEyOk9yZ2FuaXphdGlvbjMxOTg2ODU3")
        self.assertEqual(
            repo.owner.avatar_url,
            "https://avatars.githubusercontent.com/u/31986857?v=4",
        )
        self.assertEqual(repo.owner.gravatar_id, "")
        self.assertEqual(
            repo.owner.url, "https://api.github.com/users/greenbone"
        )
        self.assertEqual(repo.owner.html_url, "https://github.com/greenbone")
        self.assertEqual(
            repo.owner.followers_url,
            "https://api.github.com/users/greenbone/followers",
        )
        self.assertEqual(
            repo.owner.following_url,
            "https://api.github.com/users/greenbone/following{/other_user}",
        )
        self.assertEqual(
            repo.owner.gists_url,
            "https://api.github.com/users/greenbone/gists{/gist_id}",
        )
        self.assertEqual(
            repo.owner.starred_url,
            "https://api.github.com/users/greenbone/starred{/owner}{/repo}",
        )
        self.assertEqual(
            repo.owner.subscriptions_url,
            "https://api.github.com/users/greenbone/subscriptions",
        )
        self.assertEqual(
            repo.owner.organizations_url,
            "https://api.github.com/users/greenbone/orgs",
        )
        self.assertEqual(
            repo.owner.repos_url, "https://api.github.com/users/greenbone/repos"
        )
        self.assertEqual(
            repo.owner.events_url,
            "https://api.github.com/users/greenbone/events{/privacy}",
        )
        self.assertEqual(
            repo.owner.received_events_url,
            "https://api.github.com/users/greenbone/received_events",
        )
        self.assertEqual(repo.owner.type, "Organization")
        self.assertFalse(repo.owner.site_admin)
        self.assertEqual(
            repo.html_url, "https://github.com/greenbone/gvm-tools"
        )
        self.assertEqual(
            repo.description,
            "Remote control your Greenbone Community Edition or Greenbone Enterprise Appliance",
        )
        self.assertEqual(repo.fork, False)
        self.assertEqual(
            repo.url, "https://api.github.com/repos/greenbone/gvm-tools"
        )
        self.assertEqual(
            repo.forks_url,
            "https://api.github.com/repos/greenbone/gvm-tools/forks",
        )
        self.assertEqual(
            repo.keys_url,
            "https://api.github.com/repos/greenbone/gvm-tools/keys{/key_id}",
        )
        self.assertEqual(
            repo.collaborators_url,
            "https://api.github.com/repos/greenbone/gvm-tools/collaborators{/collaborator}",
        )
        self.assertEqual(
            repo.teams_url,
            "https://api.github.com/repos/greenbone/gvm-tools/teams",
        )
        self.assertEqual(
            repo.hooks_url,
            "https://api.github.com/repos/greenbone/gvm-tools/hooks",
        )
        self.assertEqual(
            repo.issue_events_url,
            "https://api.github.com/repos/greenbone/gvm-tools/issues/events{/number}",
        )
        self.assertEqual(
            repo.events_url,
            "https://api.github.com/repos/greenbone/gvm-tools/events",
        )
        self.assertEqual(
            repo.assignees_url,
            "https://api.github.com/repos/greenbone/gvm-tools/assignees{/user}",
        )
        self.assertEqual(
            repo.branches_url,
            "https://api.github.com/repos/greenbone/gvm-tools/branches{/branch}",
        )
        self.assertEqual(
            repo.tags_url,
            "https://api.github.com/repos/greenbone/gvm-tools/tags",
        )
        self.assertEqual(
            repo.blobs_url,
            "https://api.github.com/repos/greenbone/gvm-tools/git/blobs{/sha}",
        )
        self.assertEqual(
            repo.git_tags_url,
            "https://api.github.com/repos/greenbone/gvm-tools/git/tags{/sha}",
        )
        self.assertEqual(
            repo.git_refs_url,
            "https://api.github.com/repos/greenbone/gvm-tools/git/refs{/sha}",
        )
        self.assertEqual(
            repo.trees_url,
            "https://api.github.com/repos/greenbone/gvm-tools/git/trees{/sha}",
        )
        self.assertEqual(
            repo.statuses_url,
            "https://api.github.com/repos/greenbone/gvm-tools/statuses/{sha}",
        )
        self.assertEqual(
            repo.languages_url,
            "https://api.github.com/repos/greenbone/gvm-tools/languages",
        )
        self.assertEqual(
            repo.stargazers_url,
            "https://api.github.com/repos/greenbone/gvm-tools/stargazers",
        )
        self.assertEqual(
            repo.contributors_url,
            "https://api.github.com/repos/greenbone/gvm-tools/contributors",
        )
        self.assertEqual(
            repo.subscribers_url,
            "https://api.github.com/repos/greenbone/gvm-tools/subscribers",
        )
        self.assertEqual(
            repo.subscription_url,
            "https://api.github.com/repos/greenbone/gvm-tools/subscription",
        )
        self.assertEqual(
            repo.commits_url,
            "https://api.github.com/repos/greenbone/gvm-tools/commits{/sha}",
        )
        self.assertEqual(
            repo.git_commits_url,
            "https://api.github.com/repos/greenbone/gvm-tools/git/commits{/sha}",
        )
        self.assertEqual(
            repo.comments_url,
            "https://api.github.com/repos/greenbone/gvm-tools/comments{/number}",
        )
        self.assertEqual(
            repo.issue_comment_url,
            "https://api.github.com/repos/greenbone/gvm-tools/issues/comments{/number}",
        )
        self.assertEqual(
            repo.contents_url,
            "https://api.github.com/repos/greenbone/gvm-tools/contents/{+path}",
        )
        self.assertEqual(
            repo.compare_url,
            "https://api.github.com/repos/greenbone/gvm-tools/compare/{base}...{head}",
        )
        self.assertEqual(
            repo.merges_url,
            "https://api.github.com/repos/greenbone/gvm-tools/merges",
        )
        self.assertEqual(
            repo.archive_url,
            "https://api.github.com/repos/greenbone/gvm-tools/{archive_format}{/ref}",
        )
        self.assertEqual(
            repo.downloads_url,
            "https://api.github.com/repos/greenbone/gvm-tools/downloads",
        )
        self.assertEqual(
            repo.issues_url,
            "https://api.github.com/repos/greenbone/gvm-tools/issues{/number}",
        )
        self.assertEqual(
            repo.pulls_url,
            "https://api.github.com/repos/greenbone/gvm-tools/pulls{/number}",
        )
        self.assertEqual(
            repo.milestones_url,
            "https://api.github.com/repos/greenbone/gvm-tools/milestones{/number}",
        )
        self.assertEqual(
            repo.notifications_url,
            "https://api.github.com/repos/greenbone/gvm-tools/notifications{?since,all,participating}",
        )
        self.assertEqual(
            repo.labels_url,
            "https://api.github.com/repos/greenbone/gvm-tools/labels{/name}",
        )
        self.assertEqual(
            repo.releases_url,
            "https://api.github.com/repos/greenbone/gvm-tools/releases{/id}",
        )
        self.assertEqual(
            repo.deployments_url,
            "https://api.github.com/repos/greenbone/gvm-tools/deployments",
        )
        self.assertEqual(
            repo.created_at,
            datetime(2017, 9, 15, 10, 54, 42, tzinfo=timezone.utc),
        )
        self.assertEqual(
            repo.updated_at,
            datetime(2022, 11, 1, 7, 45, 33, tzinfo=timezone.utc),
        )
        self.assertEqual(
            repo.pushed_at,
            datetime(2022, 11, 7, 9, 21, 30, tzinfo=timezone.utc),
        )
        self.assertEqual(
            repo.git_url, "git://github.com/greenbone/gvm-tools.git"
        )
        self.assertEqual(repo.ssh_url, "git@github.com:greenbone/gvm-tools.git")
        self.assertEqual(
            repo.clone_url, "https://github.com/greenbone/gvm-tools.git"
        )
        self.assertEqual(repo.svn_url, "https://github.com/greenbone/gvm-tools")
        self.assertEqual(
            repo.homepage, "https://greenbone.github.io/gvm-tools/"
        )
        self.assertEqual(repo.size, 3461)
        self.assertEqual(repo.stargazers_count, 128)
        self.assertEqual(repo.watchers_count, 128)
        self.assertEqual(repo.language, "Python")
        self.assertEqual(repo.has_issues, True)
        self.assertEqual(repo.has_projects, False)
        self.assertEqual(repo.has_downloads, True)
        self.assertEqual(repo.has_wiki, True)
        self.assertEqual(repo.has_pages, True)
        self.assertEqual(repo.has_discussions, False)
        self.assertEqual(repo.forks_count, 74)
        self.assertEqual(repo.mirror_url, None)
        self.assertEqual(repo.archived, False)
        self.assertEqual(repo.disabled, False)
        self.assertEqual(repo.open_issues_count, 3)
        self.assertEqual(repo.license.key, "gpl-3.0")
        self.assertEqual(repo.license.name, "GNU General Public License v3.0")
        self.assertEqual(repo.license.spdx_id, "GPL-3.0")
        self.assertEqual(
            repo.license.url, "https://api.github.com/licenses/gpl-3.0"
        )
        self.assertEqual(repo.license.node_id, "MDc6TGljZW5zZTk=")
        self.assertTrue(repo.allow_forking)
        self.assertFalse(repo.is_template)
        self.assertFalse(repo.web_commit_signoff_required)
        self.assertEqual(
            repo.topics,
            [
                "gmp",
                "gmp-scripts",
                "greenbone",
                "greenbone-vulnerability-manager",
                "gvm",
                "gvm-cli",
                "gvm-pyshell",
                "gvm-script",
                "omp",
                "openvas",
                "openvas-cli",
                "osp",
                "python",
                "vulnerability",
                "vulnerability-assessment",
                "vulnerability-management",
            ],
        )
        self.assertEqual(repo.visibility, "public")
        self.assertEqual(repo.forks, 74)
        self.assertEqual(repo.open_issues, 3)
        self.assertEqual(repo.watchers, 128)
        self.assertEqual(repo.default_branch, "main")
