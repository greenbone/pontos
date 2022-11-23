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

# pylint: disable=line-too-long

from unittest.mock import MagicMock

import httpx

from pontos.github.api.repositories import (
    GitHubAsyncRESTRepositories,
    GitIgnoreTemplate,
    LicenseType,
    MergeCommitMessage,
    MergeCommitTitle,
    SquashMergeCommitMessage,
    SquashMergeCommitTitle,
)
from tests.github.api import GitHubAsyncRESTTestCase, create_response

REPOSITORY_JSON = {
    "id": 1,
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
    "git_url": "git:github.com/octocat/Hello-World.git",
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
    "ssh_url": "git@github.com:octocat/Hello-World.git",
    "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
    "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
    "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
    "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
    "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
    "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
    "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
    "clone_url": "https://github.com/octocat/Hello-World.git",
    "mirror_url": "git:git.example.com/octocat/Hello-World",
    "hooks_url": "https://api.github.com/repos/octocat/Hello-World/hooks",
    "svn_url": "https://svn.github.com/octocat/Hello-World",
    "homepage": "https://github.com",
    "language": None,
    "forks_count": 9,
    "forks": 9,
    "stargazers_count": 80,
    "watchers_count": 80,
    "watchers": 80,
    "size": 108,
    "default_branch": "master",
    "open_issues_count": 0,
    "open_issues": 0,
    "is_template": False,
    "topics": ["octocat", "atom", "electron", "api"],
    "has_issues": True,
    "has_projects": True,
    "has_wiki": True,
    "has_pages": False,
    "has_downloads": True,
    "has_discussions": False,
    "archived": False,
    "disabled": False,
    "visibility": "public",
    "pushed_at": "2011-01-26T19:06:43Z",
    "created_at": "2011-01-26T19:01:12Z",
    "updated_at": "2011-01-26T19:14:43Z",
    "permissions": {"pull": True, "push": False, "admin": False},
    "allow_rebase_merge": True,
    "template_repository": {
        "id": 1296269,
        "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
        "name": "Hello-World-Template",
        "full_name": "octocat/Hello-World-Template",
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
        "html_url": "https://github.com/octocat/Hello-World-Template",
        "description": "This your first repo!",
        "fork": False,
        "url": "https://api.github.com/repos/octocat/Hello-World-Template",
        "archive_url": "https://api.github.com/repos/octocat/Hello-World-Template/{archive_format}{/ref}",
        "assignees_url": "https://api.github.com/repos/octocat/Hello-World-Template/assignees{/user}",
        "blobs_url": "https://api.github.com/repos/octocat/Hello-World-Template/git/blobs{/sha}",
        "branches_url": "https://api.github.com/repos/octocat/Hello-World-Template/branches{/branch}",
        "collaborators_url": "https://api.github.com/repos/octocat/Hello-World-Template/collaborators{/collaborator}",
        "comments_url": "https://api.github.com/repos/octocat/Hello-World-Template/comments{/number}",
        "commits_url": "https://api.github.com/repos/octocat/Hello-World-Template/commits{/sha}",
        "compare_url": "https://api.github.com/repos/octocat/Hello-World-Template/compare/{base}...{head}",
        "contents_url": "https://api.github.com/repos/octocat/Hello-World-Template/contents/{+path}",
        "contributors_url": "https://api.github.com/repos/octocat/Hello-World-Template/contributors",
        "deployments_url": "https://api.github.com/repos/octocat/Hello-World-Template/deployments",
        "downloads_url": "https://api.github.com/repos/octocat/Hello-World-Template/downloads",
        "events_url": "https://api.github.com/repos/octocat/Hello-World-Template/events",
        "forks_url": "https://api.github.com/repos/octocat/Hello-World-Template/forks",
        "git_commits_url": "https://api.github.com/repos/octocat/Hello-World-Template/git/commits{/sha}",
        "git_refs_url": "https://api.github.com/repos/octocat/Hello-World-Template/git/refs{/sha}",
        "git_tags_url": "https://api.github.com/repos/octocat/Hello-World-Template/git/tags{/sha}",
        "git_url": "git:github.com/octocat/Hello-World-Template.git",
        "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World-Template/issues/comments{/number}",
        "issue_events_url": "https://api.github.com/repos/octocat/Hello-World-Template/issues/events{/number}",
        "issues_url": "https://api.github.com/repos/octocat/Hello-World-Template/issues{/number}",
        "keys_url": "https://api.github.com/repos/octocat/Hello-World-Template/keys{/key_id}",
        "labels_url": "https://api.github.com/repos/octocat/Hello-World-Template/labels{/name}",
        "languages_url": "https://api.github.com/repos/octocat/Hello-World-Template/languages",
        "merges_url": "https://api.github.com/repos/octocat/Hello-World-Template/merges",
        "milestones_url": "https://api.github.com/repos/octocat/Hello-World-Template/milestones{/number}",
        "notifications_url": "https://api.github.com/repos/octocat/Hello-World-Template/notifications{?since,all,participating}",
        "pulls_url": "https://api.github.com/repos/octocat/Hello-World-Template/pulls{/number}",
        "releases_url": "https://api.github.com/repos/octocat/Hello-World-Template/releases{/id}",
        "ssh_url": "git@github.com:octocat/Hello-World-Template.git",
        "stargazers_url": "https://api.github.com/repos/octocat/Hello-World-Template/stargazers",
        "statuses_url": "https://api.github.com/repos/octocat/Hello-World-Template/statuses/{sha}",
        "subscribers_url": "https://api.github.com/repos/octocat/Hello-World-Template/subscribers",
        "subscription_url": "https://api.github.com/repos/octocat/Hello-World-Template/subscription",
        "tags_url": "https://api.github.com/repos/octocat/Hello-World-Template/tags",
        "teams_url": "https://api.github.com/repos/octocat/Hello-World-Template/teams",
        "trees_url": "https://api.github.com/repos/octocat/Hello-World-Template/git/trees{/sha}",
        "clone_url": "https://github.com/octocat/Hello-World-Template.git",
        "mirror_url": "git:git.example.com/octocat/Hello-World-Template",
        "hooks_url": "https://api.github.com/repos/octocat/Hello-World-Template/hooks",
        "svn_url": "https://svn.github.com/octocat/Hello-World-Template",
        "homepage": "https://github.com",
        "language": None,
        "forks": 9,
        "forks_count": 9,
        "stargazers_count": 80,
        "watchers_count": 80,
        "watchers": 80,
        "size": 108,
        "default_branch": "master",
        "open_issues": 0,
        "open_issues_count": 0,
        "is_template": True,
        "license": {
            "key": "mit",
            "name": "MIT License",
            "url": "https://api.github.com/licenses/mit",
            "spdx_id": "MIT",
            "node_id": "MDc6TGljZW5zZW1pdA==",
            "html_url": "https://api.github.com/licenses/mit",
        },
        "topics": ["octocat", "atom", "electron", "api"],
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True,
        "has_pages": False,
        "has_downloads": True,
        "archived": False,
        "disabled": False,
        "visibility": "public",
        "pushed_at": "2011-01-26T19:06:43Z",
        "created_at": "2011-01-26T19:01:12Z",
        "updated_at": "2011-01-26T19:14:43Z",
        "permissions": {"admin": False, "push": False, "pull": True},
        "allow_rebase_merge": True,
        "temp_clone_token": "ABTLWHOULUVAXGTRYU7OC2876QJ2O",
        "allow_squash_merge": True,
        "allow_auto_merge": False,
        "delete_branch_on_merge": True,
        "allow_merge_commit": True,
        "subscribers_count": 42,
        "network_count": 0,
    },
    "temp_clone_token": "ABTLWHOULUVAXGTRYU7OC2876QJ2O",
    "allow_squash_merge": True,
    "allow_auto_merge": False,
    "delete_branch_on_merge": True,
    "allow_merge_commit": True,
    "subscribers_count": 42,
    "network_count": 0,
    "license": {
        "key": "mit",
        "name": "MIT License",
        "spdx_id": "MIT",
        "url": "https://api.github.com/licenses/mit",
        "node_id": "MDc6TGljZW5zZW1pdA==",
    },
    "organization": {
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
        "type": "Organization",
        "site_admin": False,
    },
    "parent": {
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
        "git_url": "git:github.com/octocat/Hello-World.git",
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
        "ssh_url": "git@github.com:octocat/Hello-World.git",
        "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
        "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
        "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
        "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
        "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
        "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
        "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
        "clone_url": "https://github.com/octocat/Hello-World.git",
        "mirror_url": "git:git.example.com/octocat/Hello-World",
        "hooks_url": "https://api.github.com/repos/octocat/Hello-World/hooks",
        "svn_url": "https://svn.github.com/octocat/Hello-World",
        "homepage": "https://github.com",
        "language": None,
        "forks_count": 9,
        "stargazers_count": 80,
        "watchers_count": 80,
        "size": 108,
        "default_branch": "master",
        "open_issues_count": 0,
        "is_template": True,
        "topics": ["octocat", "atom", "electron", "api"],
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True,
        "has_pages": False,
        "has_downloads": True,
        "archived": False,
        "disabled": False,
        "visibility": "public",
        "pushed_at": "2011-01-26T19:06:43Z",
        "created_at": "2011-01-26T19:01:12Z",
        "updated_at": "2011-01-26T19:14:43Z",
        "permissions": {"admin": False, "push": False, "pull": True},
        "allow_rebase_merge": True,
        "temp_clone_token": "ABTLWHOULUVAXGTRYU7OC2876QJ2O",
        "allow_squash_merge": True,
        "allow_auto_merge": False,
        "delete_branch_on_merge": True,
        "allow_merge_commit": True,
        "subscribers_count": 42,
        "network_count": 0,
        "license": {
            "key": "mit",
            "name": "MIT License",
            "url": "https://api.github.com/licenses/mit",
            "spdx_id": "MIT",
            "node_id": "MDc6TGljZW5zZW1pdA==",
            "html_url": "https://api.github.com/licenses/mit",
        },
        "forks": 1,
        "open_issues": 1,
        "watchers": 1,
    },
    "source": {
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
        "git_url": "git:github.com/octocat/Hello-World.git",
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
        "ssh_url": "git@github.com:octocat/Hello-World.git",
        "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
        "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
        "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
        "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
        "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
        "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
        "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
        "clone_url": "https://github.com/octocat/Hello-World.git",
        "mirror_url": "git:git.example.com/octocat/Hello-World",
        "hooks_url": "https://api.github.com/repos/octocat/Hello-World/hooks",
        "svn_url": "https://svn.github.com/octocat/Hello-World",
        "homepage": "https://github.com",
        "language": None,
        "forks_count": 9,
        "stargazers_count": 80,
        "watchers_count": 80,
        "size": 108,
        "default_branch": "master",
        "open_issues_count": 0,
        "is_template": True,
        "topics": ["octocat", "atom", "electron", "api"],
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True,
        "has_pages": False,
        "has_downloads": True,
        "archived": False,
        "disabled": False,
        "visibility": "public",
        "pushed_at": "2011-01-26T19:06:43Z",
        "created_at": "2011-01-26T19:01:12Z",
        "updated_at": "2011-01-26T19:14:43Z",
        "permissions": {"admin": False, "push": False, "pull": True},
        "allow_rebase_merge": True,
        "temp_clone_token": "ABTLWHOULUVAXGTRYU7OC2876QJ2O",
        "allow_squash_merge": True,
        "allow_auto_merge": False,
        "delete_branch_on_merge": True,
        "allow_merge_commit": True,
        "subscribers_count": 42,
        "network_count": 0,
        "license": {
            "key": "mit",
            "name": "MIT License",
            "url": "https://api.github.com/licenses/mit",
            "spdx_id": "MIT",
            "node_id": "MDc6TGljZW5zZW1pdA==",
            "html_url": "https://api.github.com/licenses/mit",
        },
        "forks": 1,
        "open_issues": 1,
        "watchers": 1,
    },
}


class GitHubAsyncRESTRepositoriesTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTRepositories

    async def test_get(self):
        response = create_response()
        response.json.return_value = REPOSITORY_JSON
        self.client.get.return_value = response

        repo = await self.api.get("foo/bar")

        self.client.get.assert_awaited_once_with("/repos/foo/bar")

        self.assertEqual(repo.id, 1)

    async def test_get_failure(self):
        response = create_response()
        self.client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.get("foo/bar")

        self.client.get.assert_awaited_once_with("/repos/foo/bar")

    async def test_delete(self):
        response = create_response()
        self.client.delete.return_value = response

        await self.api.delete("foo/bar")

        self.client.delete.assert_awaited_once_with("/repos/foo/bar")

    async def test_delete_failure(self):
        response = create_response()
        self.client.delete.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.delete("foo/bar")

        self.client.delete.assert_awaited_once_with("/repos/foo/bar")

    async def test_create_with_defaults(self):
        response = create_response()
        response.json.return_value = REPOSITORY_JSON
        self.client.post.return_value = response

        repo = await self.api.create("foo", "bar")

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/repos",
            data={
                "name": "bar",
                "private": False,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True,
                "is_template": False,
                "has_downloads": True,
                "auto_init": False,
                "allow_squash_merge": True,
                "allow_merge_commit": True,
                "allow_rebase_merge": True,
                "allow_auto_merge": False,
                "allow_update_branch": False,
                "delete_branch_on_merge": False,
            },
        )

        self.assertEqual(repo.id, 1)

    async def test_create(self):
        response = create_response()
        response.json.return_value = REPOSITORY_JSON
        self.client.post.return_value = response

        repo = await self.api.create(
            "foo",
            "bar",
            private=True,
            has_issues=False,
            has_projects=False,
            has_wiki=False,
            is_template=True,
            team_id="123",
            has_downloads=False,
            auto_init=True,
            gitignore_template=GitIgnoreTemplate.PYTHON,
            license_template=LicenseType.MIT,
            allow_squash_merge=False,
            allow_merge_commit=False,
            allow_rebase_merge=False,
            allow_auto_merge=True,
            allow_update_branch=True,
            delete_branch_on_merge=True,
            squash_merge_commit_title=SquashMergeCommitTitle.COMMIT_OR_PR_TITLE,
            squash_merge_commit_message=SquashMergeCommitMessage.PR_BODY,
            merge_commit_title=MergeCommitTitle.MERGE_MESSAGE,
            merge_commit_message=MergeCommitMessage.PR_BODY,
        )

        self.client.post.assert_awaited_once_with(
            "/orgs/foo/repos",
            data={
                "name": "bar",
                "private": True,
                "has_issues": False,
                "has_projects": False,
                "has_wiki": False,
                "is_template": True,
                "team_id": "123",
                "has_downloads": False,
                "auto_init": True,
                "license_template": "mit",
                "gitignore_template": "Python",
                "allow_squash_merge": False,
                "allow_merge_commit": False,
                "allow_rebase_merge": False,
                "allow_auto_merge": True,
                "allow_update_branch": True,
                "delete_branch_on_merge": True,
                "squash_merge_commit_title": "COMMIT_OR_PR_TITLE",
                "squash_merge_commit_message": "PR_BODY",
                "merge_commit_title": "MERGE_MESSAGE",
                "merge_commit_message": "PR_BODY",
            },
        )

        self.assertEqual(repo.id, 1)

    async def test_archive(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.archive("foo/bar")

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar", data={"archived": True}
        )

    async def test_archive_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.archive("foo/bar")

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar", data={"archived": True}
        )

    async def test_update(self):
        response = create_response()
        response.json.return_value = REPOSITORY_JSON
        self.client.post.return_value = response

        repo = await self.api.update(
            "foo/bar",
            name="baz",
            description="A new Baz",
            homepage="http://baz.com",
            private=True,
            has_issues=False,
            has_projects=False,
            has_wiki=False,
            is_template=True,
            allow_squash_merge=False,
            allow_merge_commit=False,
            allow_rebase_merge=False,
            allow_auto_merge=True,
            allow_update_branch=True,
            delete_branch_on_merge=True,
            squash_merge_commit_title=SquashMergeCommitTitle.PR_TITLE,
            squash_merge_commit_message=SquashMergeCommitMessage.PR_BODY,
            merge_commit_title=MergeCommitTitle.PR_TITLE,
            merge_commit_message=MergeCommitMessage.PR_BODY,
            allow_forking=True,
            web_commit_signoff_required=True,
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar",
            data={
                "name": "baz",
                "description": "A new Baz",
                "homepage": "http://baz.com",
                "private": True,
                "has_issues": False,
                "has_projects": False,
                "has_wiki": False,
                "is_template": True,
                "allow_squash_merge": False,
                "allow_merge_commit": False,
                "allow_rebase_merge": False,
                "allow_auto_merge": True,
                "allow_update_branch": True,
                "delete_branch_on_merge": True,
                "squash_merge_commit_title": "PR_TITLE",
                "squash_merge_commit_message": "PR_BODY",
                "merge_commit_title": "PR_TITLE",
                "merge_commit_message": "PR_BODY",
                "allow_forking": True,
                "web_commit_signoff_required": True,
            },
        )

        self.assertEqual(repo.id, 1)

    async def test_update_with_defaults(self):
        response = create_response()
        response.json.return_value = REPOSITORY_JSON
        self.client.post.return_value = response

        repo = await self.api.update("foo/bar")

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar",
            data={
                "private": False,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True,
                "is_template": False,
                "allow_squash_merge": True,
                "allow_merge_commit": True,
                "allow_rebase_merge": True,
                "allow_auto_merge": False,
                "allow_update_branch": False,
                "delete_branch_on_merge": False,
                "allow_forking": False,
                "web_commit_signoff_required": False,
            },
        )

        self.assertEqual(repo.id, 1)

    async def test_update_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.update("foo/bar")

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar",
            data={
                "private": False,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True,
                "is_template": False,
                "allow_squash_merge": True,
                "allow_merge_commit": True,
                "allow_rebase_merge": True,
                "allow_auto_merge": False,
                "allow_update_branch": False,
                "delete_branch_on_merge": False,
                "allow_forking": False,
                "web_commit_signoff_required": False,
            },
        )
