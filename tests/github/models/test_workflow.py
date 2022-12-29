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

import unittest
from datetime import datetime, timedelta, timezone

from pontos.github.models.base import Event
from pontos.github.models.workflow import (
    Workflow,
    WorkflowRun,
    WorkflowRunStatus,
    WorkflowState,
)


class WorkflowTestCase(unittest.TestCase):
    def test_from_dict(self):
        workflow = Workflow.from_dict(
            {
                "id": 1,
                "node_id": "MDg6V29ya2Zsb3cxNjEzMzU=",
                "name": "CI",
                "path": ".github/workflows/blank.yaml",
                "state": "active",
                "created_at": "2020-01-08T23:48:37.000-08:00",
                "updated_at": "2020-01-08T23:50:21.000-08:00",
                "url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/161335",
                "html_url": "https://github.com/octo-org/octo-repo/blob/master/.github/workflows/161335",
                "badge_url": "https://github.com/octo-org/octo-repo/workflows/CI/badge.svg",
            }
        )

        self.assertEqual(workflow.id, 1)
        self.assertEqual(workflow.node_id, "MDg6V29ya2Zsb3cxNjEzMzU=")
        self.assertEqual(workflow.name, "CI")
        self.assertEqual(workflow.path, ".github/workflows/blank.yaml")
        self.assertEqual(workflow.state, WorkflowState.ACTIVE)
        self.assertEqual(
            workflow.created_at,
            datetime(
                2020, 1, 8, 23, 48, 37, tzinfo=timezone(timedelta(hours=-8))
            ),
        )
        self.assertEqual(
            workflow.updated_at,
            datetime(
                2020, 1, 8, 23, 50, 21, tzinfo=timezone(timedelta(hours=-8))
            ),
        )
        self.assertEqual(
            workflow.url,
            "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/161335",
        )
        self.assertEqual(
            workflow.html_url,
            "https://github.com/octo-org/octo-repo/blob/master/.github/workflows/161335",
        )
        self.assertEqual(
            workflow.badge_url,
            "https://github.com/octo-org/octo-repo/workflows/CI/badge.svg",
        )


class WorkflowRunTestCase(unittest.TestCase):
    def test_from_dict(self):
        run = WorkflowRun.from_dict(
            {
                "id": 1,
                "name": "Build",
                "node_id": "MDEyOldvcmtmbG93IFJ1bjI2OTI4OQ==",
                "check_suite_id": 42,
                "check_suite_node_id": "MDEwOkNoZWNrU3VpdGU0Mg==",
                "head_branch": "master",
                "head_sha": "acb5820ced9479c074f688cc328bf03f341a511d",
                "run_number": 562,
                "event": "push",
                "status": "queued",
                "conclusion": None,
                "workflow_id": 159038,
                "url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642",
                "html_url": "https://github.com/octo-org/octo-repo/actions/runs/30433642",
                "pull_requests": [],
                "created_at": "2020-01-22T19:33:08Z",
                "updated_at": "2020-01-22T19:33:08Z",
                "actor": {
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
                "run_attempt": 1,
                "run_started_at": "2020-01-22T19:33:08Z",
                "triggering_actor": {
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
                "jobs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/jobs",
                "logs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/logs",
                "check_suite_url": "https://api.github.com/repos/octo-org/octo-repo/check-suites/414944374",
                "artifacts_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/artifacts",
                "cancel_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/cancel",
                "rerun_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/rerun",
                "workflow_url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/159038",
                "head_commit": {
                    "id": "acb5820ced9479c074f688cc328bf03f341a511d",
                    "tree_id": "d23f6eedb1e1b9610bbc754ddb5197bfe7271223",
                    "message": "Create linter.yaml",
                    "timestamp": "2020-01-22T19:33:05Z",
                    "author": {
                        "name": "Octo Cat",
                        "email": "octocat@github.com",
                    },
                    "committer": {
                        "name": "GitHub",
                        "email": "noreply@github.com",
                    },
                },
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
                    "hooks_url": "http://api.github.com/repos/octocat/Hello-World/hooks",
                },
                "head_repository": {
                    "id": 217723378,
                    "node_id": "MDEwOlJlcG9zaXRvcnkyMTc3MjMzNzg=",
                    "name": "octo-repo",
                    "full_name": "octo-org/octo-repo",
                    "private": True,
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
                    "html_url": "https://github.com/octo-org/octo-repo",
                    "description": None,
                    "fork": False,
                    "url": "https://api.github.com/repos/octo-org/octo-repo",
                    "forks_url": "https://api.github.com/repos/octo-org/octo-repo/forks",
                    "keys_url": "https://api.github.com/repos/octo-org/octo-repo/keys{/key_id}",
                    "collaborators_url": "https://api.github.com/repos/octo-org/octo-repo/collaborators{/collaborator}",
                    "teams_url": "https://api.github.com/repos/octo-org/octo-repo/teams",
                    "hooks_url": "https://api.github.com/repos/octo-org/octo-repo/hooks",
                    "issue_events_url": "https://api.github.com/repos/octo-org/octo-repo/issues/events{/number}",
                    "events_url": "https://api.github.com/repos/octo-org/octo-repo/events",
                    "assignees_url": "https://api.github.com/repos/octo-org/octo-repo/assignees{/user}",
                    "branches_url": "https://api.github.com/repos/octo-org/octo-repo/branches{/branch}",
                    "tags_url": "https://api.github.com/repos/octo-org/octo-repo/tags",
                    "blobs_url": "https://api.github.com/repos/octo-org/octo-repo/git/blobs{/sha}",
                    "git_tags_url": "https://api.github.com/repos/octo-org/octo-repo/git/tags{/sha}",
                    "git_refs_url": "https://api.github.com/repos/octo-org/octo-repo/git/refs{/sha}",
                    "trees_url": "https://api.github.com/repos/octo-org/octo-repo/git/trees{/sha}",
                    "statuses_url": "https://api.github.com/repos/octo-org/octo-repo/statuses/{sha}",
                    "languages_url": "https://api.github.com/repos/octo-org/octo-repo/languages",
                    "stargazers_url": "https://api.github.com/repos/octo-org/octo-repo/stargazers",
                    "contributors_url": "https://api.github.com/repos/octo-org/octo-repo/contributors",
                    "subscribers_url": "https://api.github.com/repos/octo-org/octo-repo/subscribers",
                    "subscription_url": "https://api.github.com/repos/octo-org/octo-repo/subscription",
                    "commits_url": "https://api.github.com/repos/octo-org/octo-repo/commits{/sha}",
                    "git_commits_url": "https://api.github.com/repos/octo-org/octo-repo/git/commits{/sha}",
                    "comments_url": "https://api.github.com/repos/octo-org/octo-repo/comments{/number}",
                    "issue_comment_url": "https://api.github.com/repos/octo-org/octo-repo/issues/comments{/number}",
                    "contents_url": "https://api.github.com/repos/octo-org/octo-repo/contents/{+path}",
                    "compare_url": "https://api.github.com/repos/octo-org/octo-repo/compare/{base}...{head}",
                    "merges_url": "https://api.github.com/repos/octo-org/octo-repo/merges",
                    "archive_url": "https://api.github.com/repos/octo-org/octo-repo/{archive_format}{/ref}",
                    "downloads_url": "https://api.github.com/repos/octo-org/octo-repo/downloads",
                    "issues_url": "https://api.github.com/repos/octo-org/octo-repo/issues{/number}",
                    "pulls_url": "https://api.github.com/repos/octo-org/octo-repo/pulls{/number}",
                    "milestones_url": "https://api.github.com/repos/octo-org/octo-repo/milestones{/number}",
                    "notifications_url": "https://api.github.com/repos/octo-org/octo-repo/notifications{?since,all,participating}",
                    "labels_url": "https://api.github.com/repos/octo-org/octo-repo/labels{/name}",
                    "releases_url": "https://api.github.com/repos/octo-org/octo-repo/releases{/id}",
                    "deployments_url": "https://api.github.com/repos/octo-org/octo-repo/deployments",
                },
            }
        )

        self.assertEqual(run.id, 1)
        self.assertEqual(run.name, "Build")
        self.assertEqual(run.node_id, "MDEyOldvcmtmbG93IFJ1bjI2OTI4OQ==")
        self.assertEqual(run.check_suite_id, 42)
        self.assertEqual(run.check_suite_node_id, "MDEwOkNoZWNrU3VpdGU0Mg==")
        self.assertEqual(run.head_branch, "master")
        self.assertEqual(
            run.head_sha, "acb5820ced9479c074f688cc328bf03f341a511d"
        )
        self.assertEqual(run.run_number, 562)
        self.assertEqual(run.event, Event.PUSH)
        self.assertEqual(run.status, WorkflowRunStatus.QUEUED)
        self.assertEqual(run.conclusion, None)
        self.assertEqual(run.workflow_id, 159038)
        self.assertEqual(
            run.url,
            "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642",
        )
        self.assertEqual(
            run.html_url,
            "https://github.com/octo-org/octo-repo/actions/runs/30433642",
        )
        self.assertEqual(run.pull_requests, [])
        self.assertEqual(
            run.created_at,
            datetime(2020, 1, 22, 19, 33, 8, tzinfo=timezone.utc),
        )
        self.assertEqual(
            run.updated_at,
            datetime(2020, 1, 22, 19, 33, 8, tzinfo=timezone.utc),
        )
        self.assertEqual(run.run_attempt, 1)
        self.assertEqual(
            run.run_started_at,
            datetime(2020, 1, 22, 19, 33, 8, tzinfo=timezone.utc),
        )
        self.assertEqual(
            run.jobs_url,
            "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/jobs",
        )
        self.assertEqual(
            run.logs_url,
            "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/logs",
        )
        self.assertEqual(
            run.check_suite_url,
            "https://api.github.com/repos/octo-org/octo-repo/check-suites/414944374",
        )
        self.assertEqual(
            run.artifacts_url,
            "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/artifacts",
        )
        self.assertEqual(
            run.cancel_url,
            "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/cancel",
        )
        self.assertEqual(
            run.rerun_url,
            "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/rerun",
        )
        self.assertEqual(
            run.workflow_url,
            "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/159038",
        )
        commit = run.head_commit
        self.assertEqual(commit.id, "acb5820ced9479c074f688cc328bf03f341a511d")
        self.assertEqual(
            commit.tree_id, "d23f6eedb1e1b9610bbc754ddb5197bfe7271223"
        )
        self.assertEqual(commit.message, "Create linter.yaml")
        self.assertEqual(
            commit.timestamp,
            datetime(2020, 1, 22, 19, 33, 5, tzinfo=timezone.utc),
        )
        self.assertEqual(commit.author.name, "Octo Cat")
        self.assertEqual(commit.author.email, "octocat@github.com")
        self.assertEqual(commit.committer.name, "GitHub")
        self.assertEqual(commit.committer.email, "noreply@github.com")

        user = run.actor
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
        self.assertEqual(user.site_admin, False)

        user = run.triggering_actor
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
        self.assertEqual(user.site_admin, False)

        repo = run.repository
        self.assertEqual(repo.id, 1296269)
        self.assertEqual(repo.node_id, "MDEwOlJlcG9zaXRvcnkxMjk2MjY5")
        self.assertEqual(repo.name, "Hello-World")
        self.assertEqual(repo.full_name, "octocat/Hello-World")
        self.assertFalse(repo.private)
        self.assertEqual(
            repo.html_url, "https://github.com/octocat/Hello-World"
        )
        self.assertEqual(repo.description, "This your first repo!")
        self.assertFalse(repo.fork)
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
            repo.hooks_url,
            "http://api.github.com/repos/octocat/Hello-World/hooks",
        )

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
        self.assertEqual(user.site_admin, False)

        repo = run.head_repository
        self.assertEqual(repo.id, 217723378)
        self.assertEqual(repo.node_id, "MDEwOlJlcG9zaXRvcnkyMTc3MjMzNzg=")
        self.assertEqual(repo.name, "octo-repo")
        self.assertEqual(repo.full_name, "octo-org/octo-repo")
        self.assertTrue(repo.private)
        self.assertEqual(repo.html_url, "https://github.com/octo-org/octo-repo")
        self.assertIsNone(repo.description)
        self.assertFalse(repo.fork)
        self.assertEqual(
            repo.url, "https://api.github.com/repos/octo-org/octo-repo"
        )
        self.assertEqual(
            repo.forks_url,
            "https://api.github.com/repos/octo-org/octo-repo/forks",
        )
        self.assertEqual(
            repo.keys_url,
            "https://api.github.com/repos/octo-org/octo-repo/keys{/key_id}",
        )
        self.assertEqual(
            repo.collaborators_url,
            "https://api.github.com/repos/octo-org/octo-repo/collaborators{/collaborator}",
        )
        self.assertEqual(
            repo.teams_url,
            "https://api.github.com/repos/octo-org/octo-repo/teams",
        )
        self.assertEqual(
            repo.hooks_url,
            "https://api.github.com/repos/octo-org/octo-repo/hooks",
        )
        self.assertEqual(
            repo.issue_events_url,
            "https://api.github.com/repos/octo-org/octo-repo/issues/events{/number}",
        )
        self.assertEqual(
            repo.events_url,
            "https://api.github.com/repos/octo-org/octo-repo/events",
        )
        self.assertEqual(
            repo.assignees_url,
            "https://api.github.com/repos/octo-org/octo-repo/assignees{/user}",
        )
        self.assertEqual(
            repo.branches_url,
            "https://api.github.com/repos/octo-org/octo-repo/branches{/branch}",
        )
        self.assertEqual(
            repo.tags_url,
            "https://api.github.com/repos/octo-org/octo-repo/tags",
        )
        self.assertEqual(
            repo.blobs_url,
            "https://api.github.com/repos/octo-org/octo-repo/git/blobs{/sha}",
        )
        self.assertEqual(
            repo.git_tags_url,
            "https://api.github.com/repos/octo-org/octo-repo/git/tags{/sha}",
        )
        self.assertEqual(
            repo.git_refs_url,
            "https://api.github.com/repos/octo-org/octo-repo/git/refs{/sha}",
        )
        self.assertEqual(
            repo.trees_url,
            "https://api.github.com/repos/octo-org/octo-repo/git/trees{/sha}",
        )
        self.assertEqual(
            repo.statuses_url,
            "https://api.github.com/repos/octo-org/octo-repo/statuses/{sha}",
        )
        self.assertEqual(
            repo.languages_url,
            "https://api.github.com/repos/octo-org/octo-repo/languages",
        )
        self.assertEqual(
            repo.stargazers_url,
            "https://api.github.com/repos/octo-org/octo-repo/stargazers",
        )
        self.assertEqual(
            repo.contributors_url,
            "https://api.github.com/repos/octo-org/octo-repo/contributors",
        )
        self.assertEqual(
            repo.subscribers_url,
            "https://api.github.com/repos/octo-org/octo-repo/subscribers",
        )
        self.assertEqual(
            repo.subscription_url,
            "https://api.github.com/repos/octo-org/octo-repo/subscription",
        )
        self.assertEqual(
            repo.commits_url,
            "https://api.github.com/repos/octo-org/octo-repo/commits{/sha}",
        )
        self.assertEqual(
            repo.git_commits_url,
            "https://api.github.com/repos/octo-org/octo-repo/git/commits{/sha}",
        )
        self.assertEqual(
            repo.comments_url,
            "https://api.github.com/repos/octo-org/octo-repo/comments{/number}",
        )
        self.assertEqual(
            repo.issue_comment_url,
            "https://api.github.com/repos/octo-org/octo-repo/issues/comments{/number}",
        )
        self.assertEqual(
            repo.contents_url,
            "https://api.github.com/repos/octo-org/octo-repo/contents/{+path}",
        )
        self.assertEqual(
            repo.compare_url,
            "https://api.github.com/repos/octo-org/octo-repo/compare/{base}...{head}",
        )
        self.assertEqual(
            repo.merges_url,
            "https://api.github.com/repos/octo-org/octo-repo/merges",
        )
        self.assertEqual(
            repo.archive_url,
            "https://api.github.com/repos/octo-org/octo-repo/{archive_format}{/ref}",
        )
        self.assertEqual(
            repo.downloads_url,
            "https://api.github.com/repos/octo-org/octo-repo/downloads",
        )
        self.assertEqual(
            repo.issues_url,
            "https://api.github.com/repos/octo-org/octo-repo/issues{/number}",
        )
        self.assertEqual(
            repo.pulls_url,
            "https://api.github.com/repos/octo-org/octo-repo/pulls{/number}",
        )
        self.assertEqual(
            repo.milestones_url,
            "https://api.github.com/repos/octo-org/octo-repo/milestones{/number}",
        )
        self.assertEqual(
            repo.notifications_url,
            "https://api.github.com/repos/octo-org/octo-repo/notifications{?since,all,participating}",
        )
        self.assertEqual(
            repo.labels_url,
            "https://api.github.com/repos/octo-org/octo-repo/labels{/name}",
        )
        self.assertEqual(
            repo.releases_url,
            "https://api.github.com/repos/octo-org/octo-repo/releases{/id}",
        )
        self.assertEqual(
            repo.deployments_url,
            "https://api.github.com/repos/octo-org/octo-repo/deployments",
        )

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
        self.assertEqual(user.site_admin, False)
