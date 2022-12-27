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

# pylint: disable=line-too-long, too-many-lines

import unittest
from datetime import datetime, timezone

from pontos.github.models.base import Permission, TeamPrivacy
from pontos.github.models.pull_request import (
    AuthorAssociation,
    MilestoneState,
    PullRequest,
    PullRequestState,
)


class PullRequestTestCase(unittest.TestCase):
    def test_from_dict(self):
        pr = PullRequest.from_dict(
            {
                "url": "https://api.github.com/repos/octocat/Hello-World/pulls/1347",
                "id": 1,
                "node_id": "MDExOlB1bGxSZXF1ZXN0MQ==",
                "html_url": "https://github.com/octocat/Hello-World/pull/1347",
                "diff_url": "https://github.com/octocat/Hello-World/pull/1347.diff",
                "patch_url": "https://github.com/octocat/Hello-World/pull/1347.patch",
                "issue_url": "https://api.github.com/repos/octocat/Hello-World/issues/1347",
                "commits_url": "https://api.github.com/repos/octocat/Hello-World/pulls/1347/commits",
                "review_comments_url": "https://api.github.com/repos/octocat/Hello-World/pulls/1347/comments",
                "review_comment_url": "https://api.github.com/repos/octocat/Hello-World/pulls/comments{/number}",
                "comments_url": "https://api.github.com/repos/octocat/Hello-World/issues/1347/comments",
                "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/6dcb09b5b57875f334f61aebed695e2e4193db5e",
                "number": 1347,
                "state": "open",
                "locked": True,
                "title": "Amazing new feature",
                "user": {
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
                "body": "Please pull these awesome changes in!",
                "labels": [
                    {
                        "id": 208045946,
                        "node_id": "MDU6TGFiZWwyMDgwNDU5NDY=",
                        "url": "https://api.github.com/repos/octocat/Hello-World/labels/bug",
                        "name": "bug",
                        "description": "Something isn't working",
                        "color": "f29513",
                        "default": True,
                    }
                ],
                "milestone": {
                    "url": "https://api.github.com/repos/octocat/Hello-World/milestones/1",
                    "html_url": "https://github.com/octocat/Hello-World/milestones/v1.0",
                    "labels_url": "https://api.github.com/repos/octocat/Hello-World/milestones/1/labels",
                    "id": 1002604,
                    "node_id": "MDk6TWlsZXN0b25lMTAwMjYwNA==",
                    "number": 1,
                    "state": "open",
                    "title": "v1.0",
                    "description": "Tracking milestone for version 1.0",
                    "creator": {
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
                    "open_issues": 4,
                    "closed_issues": 8,
                    "created_at": "2011-04-10T20:09:31Z",
                    "updated_at": "2014-03-03T18:58:10Z",
                    "closed_at": "2013-02-12T13:22:01Z",
                    "due_on": "2012-10-09T23:39:01Z",
                },
                "active_lock_reason": "too heated",
                "created_at": "2011-01-26T19:01:12Z",
                "updated_at": "2011-01-26T19:01:12Z",
                "closed_at": "2011-01-26T19:01:12Z",
                "merged_at": "2011-01-26T19:01:12Z",
                "merge_commit_sha": "e5bd3914e2e596debea16f433f57875b5b90bcd6",
                "assignee": {
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
                "assignees": [
                    {
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
                    {
                        "login": "hubot",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/hubot_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/hubot",
                        "html_url": "https://github.com/hubot",
                        "followers_url": "https://api.github.com/users/hubot/followers",
                        "following_url": "https://api.github.com/users/hubot/following{/other_user}",
                        "gists_url": "https://api.github.com/users/hubot/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/hubot/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/hubot/subscriptions",
                        "organizations_url": "https://api.github.com/users/hubot/orgs",
                        "repos_url": "https://api.github.com/users/hubot/repos",
                        "events_url": "https://api.github.com/users/hubot/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/hubot/received_events",
                        "type": "User",
                        "site_admin": True,
                    },
                ],
                "requested_reviewers": [
                    {
                        "login": "other_user",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/other_user_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/other_user",
                        "html_url": "https://github.com/other_user",
                        "followers_url": "https://api.github.com/users/other_user/followers",
                        "following_url": "https://api.github.com/users/other_user/following{/other_user}",
                        "gists_url": "https://api.github.com/users/other_user/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/other_user/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/other_user/subscriptions",
                        "organizations_url": "https://api.github.com/users/other_user/orgs",
                        "repos_url": "https://api.github.com/users/other_user/repos",
                        "events_url": "https://api.github.com/users/other_user/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/other_user/received_events",
                        "type": "User",
                        "site_admin": False,
                    }
                ],
                "requested_teams": [
                    {
                        "id": 1,
                        "node_id": "MDQ6VGVhbTE=",
                        "url": "https://api.github.com/teams/1",
                        "html_url": "https://github.com/orgs/github/teams/justice-league",
                        "name": "Justice League",
                        "slug": "justice-league",
                        "description": "A great team.",
                        "privacy": "closed",
                        "permission": "admin",
                        "members_url": "https://api.github.com/teams/1/members{/member}",
                        "repositories_url": "https://api.github.com/teams/1/repos",
                    }
                ],
                "head": {
                    "label": "octocat:new-topic",
                    "ref": "new-topic",
                    "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
                    "user": {
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
                    "repo": {
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
                        "topics": ["octocat", "atom", "electron", "api"],
                        "has_issues": True,
                        "has_projects": True,
                        "has_wiki": True,
                        "has_pages": False,
                        "has_downloads": True,
                        "has_discussions": False,
                        "archived": False,
                        "disabled": False,
                        "pushed_at": "2011-01-26T19:06:43Z",
                        "created_at": "2011-01-26T19:01:12Z",
                        "updated_at": "2011-01-26T19:14:43Z",
                        "permissions": {
                            "admin": False,
                            "push": False,
                            "pull": True,
                        },
                        "allow_rebase_merge": True,
                        "allow_squash_merge": True,
                        "allow_merge_commit": True,
                        "allow_forking": True,
                        "forks": 123,
                        "open_issues": 123,
                        "license": {
                            "key": "mit",
                            "name": "MIT License",
                            "url": "https://api.github.com/licenses/mit",
                            "spdx_id": "MIT",
                            "node_id": "MDc6TGljZW5zZW1pdA==",
                        },
                        "watchers": 123,
                    },
                },
                "base": {
                    "label": "octocat:master",
                    "ref": "master",
                    "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
                    "user": {
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
                    "repo": {
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
                        "topics": ["octocat", "atom", "electron", "api"],
                        "has_issues": True,
                        "has_projects": True,
                        "has_wiki": True,
                        "has_pages": False,
                        "has_downloads": True,
                        "has_discussions": False,
                        "archived": False,
                        "disabled": False,
                        "pushed_at": "2011-01-26T19:06:43Z",
                        "created_at": "2011-01-26T19:01:12Z",
                        "updated_at": "2011-01-26T19:14:43Z",
                        "permissions": {
                            "admin": False,
                            "push": False,
                            "pull": True,
                        },
                        "allow_rebase_merge": True,
                        "temp_clone_token": "ABTLWHOULUVAXGTRYU7OC2876QJ2O",
                        "allow_squash_merge": True,
                        "allow_merge_commit": True,
                        "allow_forking": True,
                        "forks": 123,
                        "open_issues": 123,
                        "license": {
                            "key": "mit",
                            "name": "MIT License",
                            "url": "https://api.github.com/licenses/mit",
                            "spdx_id": "MIT",
                            "node_id": "MDc6TGljZW5zZW1pdA==",
                        },
                        "watchers": 123,
                    },
                },
                "_links": {
                    "self": {
                        "href": "https://api.github.com/repos/octocat/Hello-World/pulls/1347"
                    },
                    "html": {
                        "href": "https://github.com/octocat/Hello-World/pull/1347"
                    },
                    "issue": {
                        "href": "https://api.github.com/repos/octocat/Hello-World/issues/1347"
                    },
                    "comments": {
                        "href": "https://api.github.com/repos/octocat/Hello-World/issues/1347/comments"
                    },
                    "review_comments": {
                        "href": "https://api.github.com/repos/octocat/Hello-World/pulls/1347/comments"
                    },
                    "review_comment": {
                        "href": "https://api.github.com/repos/octocat/Hello-World/pulls/comments{/number}"
                    },
                    "commits": {
                        "href": "https://api.github.com/repos/octocat/Hello-World/pulls/1347/commits"
                    },
                    "statuses": {
                        "href": "https://api.github.com/repos/octocat/Hello-World/statuses/6dcb09b5b57875f334f61aebed695e2e4193db5e"
                    },
                },
                "author_association": "OWNER",
                "auto_merge": None,
                "draft": False,
                "merged": False,
                "mergeable": True,
                "rebaseable": True,
                "mergeable_state": "clean",
                "merged_by": {
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
                "comments": 10,
                "review_comments": 0,
                "maintainer_can_modify": True,
                "commits": 3,
                "additions": 100,
                "deletions": 3,
                "changed_files": 5,
            }
        )

        self.assertEqual(
            pr.url,
            "https://api.github.com/repos/octocat/Hello-World/pulls/1347",
        )
        self.assertEqual(pr.id, 1)
        self.assertEqual(pr.node_id, "MDExOlB1bGxSZXF1ZXN0MQ==")
        self.assertEqual(
            pr.html_url, "https://github.com/octocat/Hello-World/pull/1347"
        )
        self.assertEqual(
            pr.diff_url, "https://github.com/octocat/Hello-World/pull/1347.diff"
        )
        self.assertEqual(
            pr.patch_url,
            "https://github.com/octocat/Hello-World/pull/1347.patch",
        )
        self.assertEqual(
            pr.issue_url,
            "https://api.github.com/repos/octocat/Hello-World/issues/1347",
        )
        self.assertEqual(
            pr.commits_url,
            "https://api.github.com/repos/octocat/Hello-World/pulls/1347/commits",
        )
        self.assertEqual(
            pr.review_comments_url,
            "https://api.github.com/repos/octocat/Hello-World/pulls/1347/comments",
        )
        self.assertEqual(
            pr.review_comment_url,
            "https://api.github.com/repos/octocat/Hello-World/pulls/comments{/number}",
        )
        self.assertEqual(
            pr.comments_url,
            "https://api.github.com/repos/octocat/Hello-World/issues/1347/comments",
        )
        self.assertEqual(
            pr.statuses_url,
            "https://api.github.com/repos/octocat/Hello-World/statuses/6dcb09b5b57875f334f61aebed695e2e4193db5e",
        )
        self.assertEqual(pr.number, 1347)
        self.assertEqual(pr.state, PullRequestState.OPEN)
        self.assertTrue(pr.locked)
        self.assertEqual(pr.title, "Amazing new feature")
        self.assertEqual(pr.body, "Please pull these awesome changes in!")
        self.assertEqual(pr.active_lock_reason, "too heated")
        self.assertEqual(
            pr.created_at, datetime(2011, 1, 26, 19, 1, 12, tzinfo=timezone.utc)
        )
        self.assertEqual(
            pr.updated_at, datetime(2011, 1, 26, 19, 1, 12, tzinfo=timezone.utc)
        )
        self.assertEqual(
            pr.closed_at, datetime(2011, 1, 26, 19, 1, 12, tzinfo=timezone.utc)
        )
        self.assertEqual(
            pr.merged_at, datetime(2011, 1, 26, 19, 1, 12, tzinfo=timezone.utc)
        )
        self.assertEqual(
            pr.merge_commit_sha, "e5bd3914e2e596debea16f433f57875b5b90bcd6"
        )
        self.assertEqual(pr.author_association, AuthorAssociation.OWNER)
        self.assertEqual(pr.auto_merge, None)
        self.assertEqual(pr.draft, False)
        self.assertEqual(pr.merged, False)
        self.assertEqual(pr.mergeable, True)
        self.assertEqual(pr.rebaseable, True)
        self.assertEqual(pr.mergeable_state, "clean")
        self.assertEqual(pr.comments, 10)
        self.assertEqual(pr.review_comments, 0)
        self.assertTrue(pr.maintainer_can_modify)
        self.assertEqual(pr.commits, 3)
        self.assertEqual(pr.additions, 100)
        self.assertEqual(pr.deletions, 3)
        self.assertEqual(pr.changed_files, 5)

        user = pr.user
        self.assertEqual(user.login, "octocat")
        self.assertEqual(user.id, 1)
        self.assertEqual(user.node_id, "MDQ6VXNlcjE=")
        self.assertEqual(
            user.avatar_url, "https://github.com/images/error/octocat_happy.gif"
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/octocat")
        self.assertEqual(user.html_url, "https://github.com/octocat")
        self.assertEqual(
            user.followers_url, "https://api.github.com/users/octocat/followers"
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/octocat/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/octocat/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/octocat/subscriptions",
        )
        self.assertEqual(
            user.organizations_url, "https://api.github.com/users/octocat/orgs"
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/octocat/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/octocat/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/octocat/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertFalse(user.site_admin)

        self.assertEqual(len(pr.labels), 1)
        label = pr.labels[0]
        self.assertEqual(label.id, 208045946)
        self.assertEqual(label.node_id, "MDU6TGFiZWwyMDgwNDU5NDY=")
        self.assertEqual(
            label.url,
            "https://api.github.com/repos/octocat/Hello-World/labels/bug",
        )
        self.assertEqual(label.name, "bug")
        self.assertEqual(label.description, "Something isn't working")
        self.assertEqual(label.color, "f29513")
        self.assertTrue(label.default)

        milestone = pr.milestone
        self.assertEqual(
            milestone.url,
            "https://api.github.com/repos/octocat/Hello-World/milestones/1",
        )
        self.assertEqual(
            milestone.html_url,
            "https://github.com/octocat/Hello-World/milestones/v1.0",
        )
        self.assertEqual(
            milestone.labels_url,
            "https://api.github.com/repos/octocat/Hello-World/milestones/1/labels",
        )
        self.assertEqual(milestone.id, 1002604)
        self.assertEqual(milestone.node_id, "MDk6TWlsZXN0b25lMTAwMjYwNA==")
        self.assertEqual(milestone.number, 1)
        self.assertEqual(milestone.state, MilestoneState.OPEN)
        self.assertEqual(milestone.title, "v1.0")
        self.assertEqual(
            milestone.description, "Tracking milestone for version 1.0"
        )
        self.assertEqual(milestone.open_issues, 4)
        self.assertEqual(milestone.closed_issues, 8)
        self.assertEqual(
            milestone.created_at,
            datetime(2011, 4, 10, 20, 9, 31, tzinfo=timezone.utc),
        )
        self.assertEqual(
            milestone.updated_at,
            datetime(2014, 3, 3, 18, 58, 10, tzinfo=timezone.utc),
        )
        self.assertEqual(
            milestone.closed_at,
            datetime(2013, 2, 12, 13, 22, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(
            milestone.due_on,
            datetime(2012, 10, 9, 23, 39, 1, tzinfo=timezone.utc),
        )

        creator = milestone.creator
        self.assertEqual(creator.login, "octocat")
        self.assertEqual(creator.id, 1)
        self.assertEqual(creator.node_id, "MDQ6VXNlcjE=")
        self.assertEqual(
            creator.avatar_url,
            "https://github.com/images/error/octocat_happy.gif",
        )
        self.assertEqual(creator.gravatar_id, "")
        self.assertEqual(creator.url, "https://api.github.com/users/octocat")
        self.assertEqual(creator.html_url, "https://github.com/octocat")
        self.assertEqual(
            creator.followers_url,
            "https://api.github.com/users/octocat/followers",
        )
        self.assertEqual(
            creator.following_url,
            "https://api.github.com/users/octocat/following{/other_user}",
        )
        self.assertEqual(
            creator.gists_url,
            "https://api.github.com/users/octocat/gists{/gist_id}",
        )
        self.assertEqual(
            creator.starred_url,
            "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        )
        self.assertEqual(
            creator.subscriptions_url,
            "https://api.github.com/users/octocat/subscriptions",
        )
        self.assertEqual(
            creator.organizations_url,
            "https://api.github.com/users/octocat/orgs",
        )
        self.assertEqual(
            creator.repos_url, "https://api.github.com/users/octocat/repos"
        )
        self.assertEqual(
            creator.events_url,
            "https://api.github.com/users/octocat/events{/privacy}",
        )
        self.assertEqual(
            creator.received_events_url,
            "https://api.github.com/users/octocat/received_events",
        )
        self.assertEqual(creator.type, "User")
        self.assertEqual(creator.site_admin, False)

        user = pr.assignee
        self.assertEqual(user.login, "octocat")
        self.assertEqual(user.id, 1)
        self.assertEqual(user.node_id, "MDQ6VXNlcjE=")
        self.assertEqual(
            user.avatar_url, "https://github.com/images/error/octocat_happy.gif"
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/octocat")
        self.assertEqual(user.html_url, "https://github.com/octocat")
        self.assertEqual(
            user.followers_url, "https://api.github.com/users/octocat/followers"
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/octocat/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/octocat/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/octocat/subscriptions",
        )
        self.assertEqual(
            user.organizations_url, "https://api.github.com/users/octocat/orgs"
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/octocat/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/octocat/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/octocat/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertFalse(user.site_admin)

        self.assertEqual(len(pr.assignees), 2)
        user = pr.assignees[0]
        self.assertEqual(user.login, "octocat")
        self.assertEqual(user.id, 1)
        self.assertEqual(user.node_id, "MDQ6VXNlcjE=")
        self.assertEqual(
            user.avatar_url, "https://github.com/images/error/octocat_happy.gif"
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/octocat")
        self.assertEqual(user.html_url, "https://github.com/octocat")
        self.assertEqual(
            user.followers_url, "https://api.github.com/users/octocat/followers"
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/octocat/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/octocat/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/octocat/subscriptions",
        )
        self.assertEqual(
            user.organizations_url, "https://api.github.com/users/octocat/orgs"
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/octocat/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/octocat/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/octocat/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertFalse(user.site_admin)

        user = pr.assignees[1]
        self.assertEqual(user.login, "hubot")
        self.assertEqual(user.id, 1)
        self.assertEqual(user.node_id, "MDQ6VXNlcjE=")
        self.assertEqual(
            user.avatar_url, "https://github.com/images/error/hubot_happy.gif"
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/hubot")
        self.assertEqual(user.html_url, "https://github.com/hubot")
        self.assertEqual(
            user.followers_url, "https://api.github.com/users/hubot/followers"
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/hubot/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url, "https://api.github.com/users/hubot/gists{/gist_id}"
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/hubot/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/hubot/subscriptions",
        )
        self.assertEqual(
            user.organizations_url, "https://api.github.com/users/hubot/orgs"
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/hubot/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/hubot/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/hubot/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertTrue(user.site_admin)

        self.assertEqual(len(pr.requested_reviewers), 1)
        reviewer = pr.requested_reviewers[0]
        self.assertEqual(reviewer.login, "other_user")
        self.assertEqual(reviewer.id, 1)
        self.assertEqual(reviewer.node_id, "MDQ6VXNlcjE=")
        self.assertEqual(
            reviewer.avatar_url,
            "https://github.com/images/error/other_user_happy.gif",
        )
        self.assertEqual(reviewer.gravatar_id, "")
        self.assertEqual(
            reviewer.url, "https://api.github.com/users/other_user"
        )
        self.assertEqual(reviewer.html_url, "https://github.com/other_user")
        self.assertEqual(
            reviewer.followers_url,
            "https://api.github.com/users/other_user/followers",
        )
        self.assertEqual(
            reviewer.following_url,
            "https://api.github.com/users/other_user/following{/other_user}",
        )
        self.assertEqual(
            reviewer.gists_url,
            "https://api.github.com/users/other_user/gists{/gist_id}",
        )
        self.assertEqual(
            reviewer.starred_url,
            "https://api.github.com/users/other_user/starred{/owner}{/repo}",
        )
        self.assertEqual(
            reviewer.subscriptions_url,
            "https://api.github.com/users/other_user/subscriptions",
        )
        self.assertEqual(
            reviewer.organizations_url,
            "https://api.github.com/users/other_user/orgs",
        )
        self.assertEqual(
            reviewer.repos_url, "https://api.github.com/users/other_user/repos"
        )
        self.assertEqual(
            reviewer.events_url,
            "https://api.github.com/users/other_user/events{/privacy}",
        )
        self.assertEqual(
            reviewer.received_events_url,
            "https://api.github.com/users/other_user/received_events",
        )
        self.assertEqual(reviewer.type, "User")
        self.assertEqual(reviewer.site_admin, False)

        self.assertEqual(len(pr.requested_teams), 1)
        team = pr.requested_teams[0]
        self.assertEqual(team.id, 1)
        self.assertEqual(team.node_id, "MDQ6VGVhbTE=")
        self.assertEqual(team.url, "https://api.github.com/teams/1")
        self.assertEqual(
            team.html_url, "https://github.com/orgs/github/teams/justice-league"
        )
        self.assertEqual(team.name, "Justice League")
        self.assertEqual(team.slug, "justice-league")
        self.assertEqual(team.description, "A great team.")
        self.assertEqual(team.privacy, TeamPrivacy.CLOSED)
        self.assertEqual(team.permission, Permission.ADMIN)
        self.assertEqual(
            team.members_url, "https://api.github.com/teams/1/members{/member}"
        )
        self.assertEqual(
            team.repositories_url, "https://api.github.com/teams/1/repos"
        )

        head = pr.head
        self.assertEqual(head.label, "octocat:new-topic")
        self.assertEqual(head.ref, "new-topic")
        self.assertEqual(head.sha, "6dcb09b5b57875f334f61aebed695e2e4193db5e")

        user = head.user
        self.assertEqual(user.login, "octocat")
        self.assertEqual(user.id, 1)
        self.assertEqual(user.node_id, "MDQ6VXNlcjE=")
        self.assertEqual(
            user.avatar_url, "https://github.com/images/error/octocat_happy.gif"
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/octocat")
        self.assertEqual(user.html_url, "https://github.com/octocat")
        self.assertEqual(
            user.followers_url, "https://api.github.com/users/octocat/followers"
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/octocat/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/octocat/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/octocat/subscriptions",
        )
        self.assertEqual(
            user.organizations_url, "https://api.github.com/users/octocat/orgs"
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/octocat/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/octocat/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/octocat/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertFalse(user.site_admin)

        repo = head.repo
        self.assertEqual(repo.id, 1296269)
        self.assertEqual(repo.node_id, "MDEwOlJlcG9zaXRvcnkxMjk2MjY5")
        self.assertEqual(repo.name, "Hello-World")
        self.assertEqual(repo.full_name, "octocat/Hello-World")
        self.assertFalse(repo.private)
        self.assertEqual(
            repo.html_url, "https://github.com/octocat/Hello-World"
        )
        self.assertEqual(repo.description, "This your first repo!")
        self.assertEqual(repo.fork, False)
        self.assertEqual(
            repo.url, "https://api.github.com/repos/octocat/Hello-World"
        )
        self.assertEqual(
            repo.archive_url,
            "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
        )
        self.assertEqual(
            repo.assignees_url,
            "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
        )
        self.assertEqual(
            repo.blobs_url,
            "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
        )
        self.assertEqual(
            repo.branches_url,
            "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
        )
        self.assertEqual(
            repo.collaborators_url,
            "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
        )
        self.assertEqual(
            repo.comments_url,
            "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
        )
        self.assertEqual(
            repo.commits_url,
            "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
        )
        self.assertEqual(
            repo.compare_url,
            "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
        )
        self.assertEqual(
            repo.contents_url,
            "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
        )
        self.assertEqual(
            repo.contributors_url,
            "https://api.github.com/repos/octocat/Hello-World/contributors",
        )
        self.assertEqual(
            repo.deployments_url,
            "https://api.github.com/repos/octocat/Hello-World/deployments",
        )
        self.assertEqual(
            repo.downloads_url,
            "https://api.github.com/repos/octocat/Hello-World/downloads",
        )
        self.assertEqual(
            repo.events_url,
            "https://api.github.com/repos/octocat/Hello-World/events",
        )
        self.assertEqual(
            repo.forks_url,
            "https://api.github.com/repos/octocat/Hello-World/forks",
        )
        self.assertEqual(
            repo.git_commits_url,
            "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
        )
        self.assertEqual(
            repo.git_refs_url,
            "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
        )
        self.assertEqual(
            repo.git_tags_url,
            "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
        )
        self.assertEqual(repo.git_url, "git:github.com/octocat/Hello-World.git")
        self.assertEqual(
            repo.issue_comment_url,
            "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
        )
        self.assertEqual(
            repo.issue_events_url,
            "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
        )
        self.assertEqual(
            repo.issues_url,
            "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
        )
        self.assertEqual(
            repo.keys_url,
            "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
        )
        self.assertEqual(
            repo.labels_url,
            "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
        )
        self.assertEqual(
            repo.languages_url,
            "https://api.github.com/repos/octocat/Hello-World/languages",
        )
        self.assertEqual(
            repo.merges_url,
            "https://api.github.com/repos/octocat/Hello-World/merges",
        )
        self.assertEqual(
            repo.milestones_url,
            "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
        )
        self.assertEqual(
            repo.notifications_url,
            "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
        )
        self.assertEqual(
            repo.pulls_url,
            "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
        )
        self.assertEqual(
            repo.releases_url,
            "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
        )
        self.assertEqual(repo.ssh_url, "git@github.com:octocat/Hello-World.git")
        self.assertEqual(
            repo.stargazers_url,
            "https://api.github.com/repos/octocat/Hello-World/stargazers",
        )
        self.assertEqual(
            repo.statuses_url,
            "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
        )
        self.assertEqual(
            repo.subscribers_url,
            "https://api.github.com/repos/octocat/Hello-World/subscribers",
        )
        self.assertEqual(
            repo.subscription_url,
            "https://api.github.com/repos/octocat/Hello-World/subscription",
        )
        self.assertEqual(
            repo.tags_url,
            "https://api.github.com/repos/octocat/Hello-World/tags",
        )
        self.assertEqual(
            repo.teams_url,
            "https://api.github.com/repos/octocat/Hello-World/teams",
        )
        self.assertEqual(
            repo.trees_url,
            "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
        )
        self.assertEqual(
            repo.clone_url, "https://github.com/octocat/Hello-World.git"
        )
        self.assertEqual(
            repo.mirror_url, "git:git.example.com/octocat/Hello-World"
        )
        self.assertEqual(
            repo.hooks_url,
            "https://api.github.com/repos/octocat/Hello-World/hooks",
        )
        self.assertEqual(
            repo.svn_url, "https://svn.github.com/octocat/Hello-World"
        )
        self.assertEqual(repo.homepage, "https://github.com")
        self.assertIsNone(repo.language)
        self.assertEqual(repo.forks_count, 9)
        self.assertEqual(repo.stargazers_count, 80)
        self.assertEqual(repo.watchers_count, 80)
        self.assertEqual(repo.size, 108)
        self.assertEqual(repo.default_branch, "master")
        self.assertEqual(repo.open_issues_count, 0)
        self.assertEqual(repo.topics, ["octocat", "atom", "electron", "api"])
        self.assertTrue(repo.has_issues)
        self.assertTrue(repo.has_projects)
        self.assertTrue(repo.has_wiki)
        self.assertFalse(repo.has_pages)
        self.assertTrue(repo.has_downloads)
        self.assertFalse(repo.has_discussions)
        self.assertFalse(repo.archived)
        self.assertFalse(repo.disabled)
        self.assertEqual(
            repo.pushed_at,
            datetime(2011, 1, 26, 19, 6, 43, tzinfo=timezone.utc),
        )
        self.assertEqual(
            repo.created_at,
            datetime(2011, 1, 26, 19, 1, 12, tzinfo=timezone.utc),
        )
        self.assertEqual(
            repo.updated_at,
            datetime(2011, 1, 26, 19, 14, 43, tzinfo=timezone.utc),
        )
        self.assertTrue(repo.allow_rebase_merge)
        self.assertTrue(repo.allow_squash_merge)
        self.assertTrue(repo.allow_merge_commit)
        self.assertTrue(repo.allow_forking)
        self.assertEqual(repo.forks, 123)
        self.assertEqual(repo.open_issues, 123)
        self.assertEqual(repo.watchers, 123)

        user = repo.owner
        self.assertEqual(user.login, "octocat")
        self.assertEqual(user.id, 1)
        self.assertEqual(user.node_id, "MDQ6VXNlcjE=")
        self.assertEqual(
            user.avatar_url, "https://github.com/images/error/octocat_happy.gif"
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/octocat")
        self.assertEqual(user.html_url, "https://github.com/octocat")
        self.assertEqual(
            user.followers_url, "https://api.github.com/users/octocat/followers"
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/octocat/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/octocat/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/octocat/subscriptions",
        )
        self.assertEqual(
            user.organizations_url, "https://api.github.com/users/octocat/orgs"
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/octocat/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/octocat/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/octocat/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertFalse(user.site_admin)

        license = repo.license  # pylint: disable=redefined-builtin
        self.assertEqual(license.key, "mit")
        self.assertEqual(license.name, "MIT License")
        self.assertEqual(license.url, "https://api.github.com/licenses/mit")
        self.assertEqual(license.spdx_id, "MIT")
        self.assertEqual(license.node_id, "MDc6TGljZW5zZW1pdA==")

        self.assertFalse(repo.permissions.admin)
        self.assertFalse(repo.permissions.push)
        self.assertTrue(repo.permissions.pull)

        base = pr.base
        self.assertEqual(base.label, "octocat:master")
        self.assertEqual(base.ref, "master")
        self.assertEqual(base.sha, "6dcb09b5b57875f334f61aebed695e2e4193db5e")

        user = base.user
        self.assertEqual(user.login, "octocat")
        self.assertEqual(user.id, 1)
        self.assertEqual(user.node_id, "MDQ6VXNlcjE=")
        self.assertEqual(
            user.avatar_url, "https://github.com/images/error/octocat_happy.gif"
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/octocat")
        self.assertEqual(user.html_url, "https://github.com/octocat")
        self.assertEqual(
            user.followers_url, "https://api.github.com/users/octocat/followers"
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/octocat/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/octocat/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/octocat/subscriptions",
        )
        self.assertEqual(
            user.organizations_url, "https://api.github.com/users/octocat/orgs"
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/octocat/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/octocat/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/octocat/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertFalse(user.site_admin)

        repo = base.repo
        self.assertEqual(repo.id, 1296269)
        self.assertEqual(repo.node_id, "MDEwOlJlcG9zaXRvcnkxMjk2MjY5")
        self.assertEqual(repo.name, "Hello-World")
        self.assertEqual(repo.full_name, "octocat/Hello-World")
        self.assertFalse(repo.private)
        self.assertEqual(
            repo.html_url, "https://github.com/octocat/Hello-World"
        )
        self.assertEqual(repo.description, "This your first repo!")
        self.assertEqual(repo.fork, False)
        self.assertEqual(
            repo.url, "https://api.github.com/repos/octocat/Hello-World"
        )
        self.assertEqual(
            repo.archive_url,
            "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
        )
        self.assertEqual(
            repo.assignees_url,
            "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
        )
        self.assertEqual(
            repo.blobs_url,
            "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
        )
        self.assertEqual(
            repo.branches_url,
            "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
        )
        self.assertEqual(
            repo.collaborators_url,
            "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
        )
        self.assertEqual(
            repo.comments_url,
            "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
        )
        self.assertEqual(
            repo.commits_url,
            "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
        )
        self.assertEqual(
            repo.compare_url,
            "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
        )
        self.assertEqual(
            repo.contents_url,
            "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
        )
        self.assertEqual(
            repo.contributors_url,
            "https://api.github.com/repos/octocat/Hello-World/contributors",
        )
        self.assertEqual(
            repo.deployments_url,
            "https://api.github.com/repos/octocat/Hello-World/deployments",
        )
        self.assertEqual(
            repo.downloads_url,
            "https://api.github.com/repos/octocat/Hello-World/downloads",
        )
        self.assertEqual(
            repo.events_url,
            "https://api.github.com/repos/octocat/Hello-World/events",
        )
        self.assertEqual(
            repo.forks_url,
            "https://api.github.com/repos/octocat/Hello-World/forks",
        )
        self.assertEqual(
            repo.git_commits_url,
            "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
        )
        self.assertEqual(
            repo.git_refs_url,
            "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
        )
        self.assertEqual(
            repo.git_tags_url,
            "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
        )
        self.assertEqual(repo.git_url, "git:github.com/octocat/Hello-World.git")
        self.assertEqual(
            repo.issue_comment_url,
            "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
        )
        self.assertEqual(
            repo.issue_events_url,
            "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
        )
        self.assertEqual(
            repo.issues_url,
            "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
        )
        self.assertEqual(
            repo.keys_url,
            "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
        )
        self.assertEqual(
            repo.labels_url,
            "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
        )
        self.assertEqual(
            repo.languages_url,
            "https://api.github.com/repos/octocat/Hello-World/languages",
        )
        self.assertEqual(
            repo.merges_url,
            "https://api.github.com/repos/octocat/Hello-World/merges",
        )
        self.assertEqual(
            repo.milestones_url,
            "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
        )
        self.assertEqual(
            repo.notifications_url,
            "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
        )
        self.assertEqual(
            repo.pulls_url,
            "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
        )
        self.assertEqual(
            repo.releases_url,
            "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
        )
        self.assertEqual(repo.ssh_url, "git@github.com:octocat/Hello-World.git")
        self.assertEqual(
            repo.stargazers_url,
            "https://api.github.com/repos/octocat/Hello-World/stargazers",
        )
        self.assertEqual(
            repo.statuses_url,
            "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
        )
        self.assertEqual(
            repo.subscribers_url,
            "https://api.github.com/repos/octocat/Hello-World/subscribers",
        )
        self.assertEqual(
            repo.subscription_url,
            "https://api.github.com/repos/octocat/Hello-World/subscription",
        )
        self.assertEqual(
            repo.tags_url,
            "https://api.github.com/repos/octocat/Hello-World/tags",
        )
        self.assertEqual(
            repo.teams_url,
            "https://api.github.com/repos/octocat/Hello-World/teams",
        )
        self.assertEqual(
            repo.trees_url,
            "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
        )
        self.assertEqual(
            repo.clone_url, "https://github.com/octocat/Hello-World.git"
        )
        self.assertEqual(
            repo.mirror_url, "git:git.example.com/octocat/Hello-World"
        )
        self.assertEqual(
            repo.hooks_url,
            "https://api.github.com/repos/octocat/Hello-World/hooks",
        )
        self.assertEqual(
            repo.svn_url, "https://svn.github.com/octocat/Hello-World"
        )
        self.assertEqual(repo.homepage, "https://github.com")
        self.assertIsNone(repo.language)
        self.assertEqual(repo.forks_count, 9)
        self.assertEqual(repo.stargazers_count, 80)
        self.assertEqual(repo.watchers_count, 80)
        self.assertEqual(repo.size, 108)
        self.assertEqual(repo.default_branch, "master")
        self.assertEqual(repo.open_issues_count, 0)
        self.assertEqual(repo.topics, ["octocat", "atom", "electron", "api"])
        self.assertTrue(repo.has_issues)
        self.assertTrue(repo.has_projects)
        self.assertTrue(repo.has_wiki)
        self.assertFalse(repo.has_pages)
        self.assertTrue(repo.has_downloads)
        self.assertFalse(repo.has_discussions)
        self.assertFalse(repo.archived)
        self.assertFalse(repo.disabled)
        self.assertEqual(
            repo.pushed_at,
            datetime(2011, 1, 26, 19, 6, 43, tzinfo=timezone.utc),
        )
        self.assertEqual(
            repo.created_at,
            datetime(2011, 1, 26, 19, 1, 12, tzinfo=timezone.utc),
        )
        self.assertEqual(
            repo.updated_at,
            datetime(2011, 1, 26, 19, 14, 43, tzinfo=timezone.utc),
        )
        self.assertTrue(repo.allow_rebase_merge)
        self.assertTrue(repo.allow_squash_merge)
        self.assertTrue(repo.allow_merge_commit)
        self.assertTrue(repo.allow_forking)
        self.assertEqual(repo.forks, 123)
        self.assertEqual(repo.open_issues, 123)
        self.assertEqual(repo.watchers, 123)

        user = pr.merged_by
        self.assertEqual(user.login, "octocat")
        self.assertEqual(user.id, 1)
        self.assertEqual(user.node_id, "MDQ6VXNlcjE=")
        self.assertEqual(
            user.avatar_url, "https://github.com/images/error/octocat_happy.gif"
        )
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/octocat")
        self.assertEqual(user.html_url, "https://github.com/octocat")
        self.assertEqual(
            user.followers_url, "https://api.github.com/users/octocat/followers"
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/octocat/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/octocat/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/octocat/subscriptions",
        )
        self.assertEqual(
            user.organizations_url, "https://api.github.com/users/octocat/orgs"
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/octocat/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/octocat/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/octocat/received_events",
        )
        self.assertEqual(user.type, "User")
        self.assertFalse(user.site_admin)
