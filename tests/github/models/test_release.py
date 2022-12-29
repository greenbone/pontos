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
from datetime import datetime, timezone

from pontos.github.models.release import Release, ReleaseAssetState


class ReleaseTestCase(unittest.TestCase):
    def test_from_dict(self):
        release = Release.from_dict(
            {
                "url": "https://api.github.com/repos/octocat/Hello-World/releases/1",
                "html_url": "https://github.com/octocat/Hello-World/releases/v1.0.0",
                "assets_url": "https://api.github.com/repos/octocat/Hello-World/releases/1/assets",
                "upload_url": "https://uploads.github.com/repos/octocat/Hello-World/releases/1/assets{?name,label}",
                "tarball_url": "https://api.github.com/repos/octocat/Hello-World/tarball/v1.0.0",
                "zipball_url": "https://api.github.com/repos/octocat/Hello-World/zipball/v1.0.0",
                "discussion_url": "https://github.com/octocat/Hello-World/discussions/90",
                "id": 1,
                "node_id": "MDc6UmVsZWFzZTE=",
                "tag_name": "v1.0.0",
                "target_commitish": "master",
                "name": "v1.0.0",
                "body": "Description of the release",
                "draft": False,
                "prerelease": False,
                "created_at": "2013-02-27T19:35:32Z",
                "published_at": "2013-02-27T19:35:32Z",
                "author": {
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
                "assets": [
                    {
                        "url": "https://api.github.com/repos/octocat/Hello-World/releases/assets/1",
                        "browser_download_url": "https://github.com/octocat/Hello-World/releases/download/v1.0.0/example.zip",
                        "id": 1,
                        "node_id": "MDEyOlJlbGVhc2VBc3NldDE=",
                        "name": "example.zip",
                        "label": "short description",
                        "state": "uploaded",
                        "content_type": "application/zip",
                        "size": 1024,
                        "download_count": 42,
                        "created_at": "2013-02-27T19:35:32Z",
                        "updated_at": "2013-02-27T19:35:32Z",
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
                    }
                ],
            }
        )

        self.assertEqual(
            release.url,
            "https://api.github.com/repos/octocat/Hello-World/releases/1",
        )
        self.assertEqual(
            release.html_url,
            "https://github.com/octocat/Hello-World/releases/v1.0.0",
        )
        self.assertEqual(
            release.assets_url,
            "https://api.github.com/repos/octocat/Hello-World/releases/1/assets",
        )
        self.assertEqual(
            release.upload_url,
            "https://uploads.github.com/repos/octocat/Hello-World/releases/1/assets{?name,label}",
        )
        self.assertEqual(
            release.tarball_url,
            "https://api.github.com/repos/octocat/Hello-World/tarball/v1.0.0",
        )
        self.assertEqual(
            release.zipball_url,
            "https://api.github.com/repos/octocat/Hello-World/zipball/v1.0.0",
        )
        self.assertEqual(
            release.discussion_url,
            "https://github.com/octocat/Hello-World/discussions/90",
        )
        self.assertEqual(release.id, 1)
        self.assertEqual(release.node_id, "MDc6UmVsZWFzZTE=")
        self.assertEqual(release.tag_name, "v1.0.0")
        self.assertEqual(release.target_commitish, "master")
        self.assertEqual(release.name, "v1.0.0")
        self.assertEqual(release.body, "Description of the release")
        self.assertFalse(release.draft)
        self.assertFalse(release.prerelease)
        self.assertEqual(
            release.created_at,
            datetime(2013, 2, 27, 19, 35, 32, tzinfo=timezone.utc),
        )
        self.assertEqual(
            release.published_at,
            datetime(2013, 2, 27, 19, 35, 32, tzinfo=timezone.utc),
        )

        user = release.author
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

        self.assertEqual(len(release.assets), 1)
        asset = release.assets[0]
        self.assertEqual(
            asset.url,
            "https://api.github.com/repos/octocat/Hello-World/releases/assets/1",
        )
        self.assertEqual(
            asset.browser_download_url,
            "https://github.com/octocat/Hello-World/releases/download/v1.0.0/example.zip",
        )
        self.assertEqual(asset.id, 1)
        self.assertEqual(asset.node_id, "MDEyOlJlbGVhc2VBc3NldDE=")
        self.assertEqual(asset.name, "example.zip")
        self.assertEqual(asset.label, "short description")
        self.assertEqual(asset.state, ReleaseAssetState.UPLOADED)
        self.assertEqual(asset.content_type, "application/zip")
        self.assertEqual(asset.size, 1024)
        self.assertEqual(asset.download_count, 42)
        self.assertEqual(
            asset.created_at,
            datetime(2013, 2, 27, 19, 35, 32, tzinfo=timezone.utc),
        )
        self.assertEqual(
            asset.updated_at,
            datetime(2013, 2, 27, 19, 35, 32, tzinfo=timezone.utc),
        )

        user = asset.uploader
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
