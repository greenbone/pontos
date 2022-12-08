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

from pontos.github.api.teams import TeamPrivacy
from pontos.github.models.base import App, Permission, Team, User


class UserTestCase(unittest.TestCase):
    def test_from_dict(self):
        data = {
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
        }

        user = User.from_dict(data)

        self.assertEqual(user.login, "greenbone")
        self.assertEqual(user.id, 31986857)
        self.assertEqual(user.node_id, "MDEyOk9yZ2FuaXphdGlvbjMxOTg2ODU3")
        self.assertEqual(user.gravatar_id, "")
        self.assertEqual(user.url, "https://api.github.com/users/greenbone")
        self.assertEqual(user.html_url, "https://github.com/greenbone")
        self.assertEqual(
            user.followers_url,
            "https://api.github.com/users/greenbone/followers",
        )
        self.assertEqual(
            user.following_url,
            "https://api.github.com/users/greenbone/following{/other_user}",
        )
        self.assertEqual(
            user.gists_url,
            "https://api.github.com/users/greenbone/gists{/gist_id}",
        )
        self.assertEqual(
            user.starred_url,
            "https://api.github.com/users/greenbone/starred{/owner}{/repo}",
        )
        self.assertEqual(
            user.subscriptions_url,
            "https://api.github.com/users/greenbone/subscriptions",
        )
        self.assertEqual(
            user.organizations_url,
            "https://api.github.com/users/greenbone/orgs",
        )
        self.assertEqual(
            user.repos_url, "https://api.github.com/users/greenbone/repos"
        )
        self.assertEqual(
            user.events_url,
            "https://api.github.com/users/greenbone/events{/privacy}",
        )
        self.assertEqual(
            user.received_events_url,
            "https://api.github.com/users/greenbone/received_events",
        )
        self.assertEqual(user.type, "Organization")
        self.assertFalse(user.site_admin)


class TeamTestCase(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "name": "python-gvm-maintainers",
            "id": 3764115,
            "node_id": "MDQ6VGVhbTM3NjQxMTU=",
            "slug": "python-gvm-maintainers",
            "description": "Maintainers of python code at GVM",
            "privacy": "closed",
            "url": "https://api.github.com/organizations/31986857/team/3764115",
            "html_url": "https://github.com/orgs/greenbone/teams/python-gvm-maintainers",
            "members_url": "https://api.github.com/organizations/31986857/team/3764115/members{/member}",
            "repositories_url": "https://api.github.com/organizations/31986857/team/3764115/repos",
            "permission": "pull",
            "parent": None,
        }

        team = Team.from_dict(data)

        self.assertEqual(team.name, "python-gvm-maintainers")
        self.assertEqual(team.id, 3764115)
        self.assertEqual(team.node_id, "MDQ6VGVhbTM3NjQxMTU=")
        self.assertEqual(team.slug, "python-gvm-maintainers")
        self.assertEqual(team.description, "Maintainers of python code at GVM")
        self.assertEqual(team.privacy, TeamPrivacy.CLOSED)
        self.assertEqual(
            team.url,
            "https://api.github.com/organizations/31986857/team/3764115",
        )
        self.assertEqual(
            team.html_url,
            "https://github.com/orgs/greenbone/teams/python-gvm-maintainers",
        )
        self.assertEqual(
            team.members_url,
            "https://api.github.com/organizations/31986857/team/3764115/members{/member}",
        )
        self.assertEqual(
            team.repositories_url,
            "https://api.github.com/organizations/31986857/team/3764115/repos",
        )
        self.assertEqual(team.permission, Permission.PULL)
        self.assertIsNone(team.parent)


class AppTestCase(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "id": 1,
            "slug": "octoapp",
            "node_id": "MDExOkludGVncmF0aW9uMQ==",
            "owner": {
                "login": "github",
                "id": 1,
                "node_id": "MDEyOk9yZ2FuaXphdGlvbjE=",
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/orgs/github",
                "html_url": "https://github.com/github",
                "followers_url": "https://api.github.com/users/github/followers",
                "following_url": "https://api.github.com/users/github/following{/other_user}",
                "gists_url": "https://api.github.com/users/github/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/github/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/github/subscriptions",
                "organizations_url": "https://api.github.com/users/github/orgs",
                "repos_url": "https://api.github.com/orgs/github/repos",
                "events_url": "https://api.github.com/orgs/github/events",
                "received_events_url": "https://api.github.com/users/github/received_events",
                "type": "Organization",
                "site_admin": False,
            },
            "name": "Octocat App",
            "description": "",
            "external_url": "https://example.com",
            "html_url": "https://github.com/apps/octoapp",
            "created_at": "2017-07-08T16:18:44-04:00",
            "updated_at": "2017-07-08T16:18:44-04:00",
            "events": ["push", "pull_request"],
        }

        app = App.from_dict(data)

        self.assertEqual(app.id, 1)
        self.assertEqual(app.slug, "octoapp")
        self.assertEqual(app.node_id, "MDExOkludGVncmF0aW9uMQ==")
        self.assertEqual(app.owner.login, "github")
        self.assertEqual(app.owner.id, 1)
        self.assertEqual(app.owner.node_id, "MDEyOk9yZ2FuaXphdGlvbjE=")
        self.assertEqual(
            app.owner.avatar_url,
            "https://github.com/images/error/octocat_happy.gif",
        )
        self.assertEqual(app.owner.gravatar_id, "")
        self.assertEqual(app.owner.url, "https://api.github.com/orgs/github")
        self.assertEqual(app.owner.html_url, "https://github.com/github")
        self.assertEqual(
            app.owner.followers_url,
            "https://api.github.com/users/github/followers",
        )
        self.assertEqual(
            app.owner.following_url,
            "https://api.github.com/users/github/following{/other_user}",
        )
        self.assertEqual(
            app.owner.gists_url,
            "https://api.github.com/users/github/gists{/gist_id}",
        )
        self.assertEqual(
            app.owner.starred_url,
            "https://api.github.com/users/github/starred{/owner}{/repo}",
        )
        self.assertEqual(
            app.owner.subscriptions_url,
            "https://api.github.com/users/github/subscriptions",
        )
        self.assertEqual(
            app.owner.organizations_url,
            "https://api.github.com/users/github/orgs",
        )
        self.assertEqual(
            app.owner.repos_url, "https://api.github.com/orgs/github/repos"
        )
        self.assertEqual(
            app.owner.events_url, "https://api.github.com/orgs/github/events"
        )
        self.assertEqual(app.owner.type, "Organization")
        self.assertFalse(app.owner.site_admin)
        self.assertEqual(app.name, "Octocat App")
        self.assertEqual(app.description, "")
        self.assertEqual(app.external_url, "https://example.com")
        self.assertEqual(app.html_url, "https://github.com/apps/octoapp")
        self.assertEqual(app.created_at, "2017-07-08T16:18:44-04:00")
        self.assertEqual(app.updated_at, "2017-07-08T16:18:44-04:00")
        self.assertEqual(app.events, ["push", "pull_request"])
