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

from datetime import datetime, timezone
from unittest.mock import MagicMock

import httpx

from pontos.github.api.tags import GitHubAsyncRESTTags
from pontos.github.models.tag import GitObjectType, Tag, VerificationReason
from tests.github.api import GitHubAsyncRESTTestCase, create_response

TAG_JSON = {
    "node_id": "MDM6VGFnOTQwYmQzMzYyNDhlZmFlMGY5ZWU1YmM3YjJkNWM5ODU4ODdiMTZhYw==",
    "tag": "v0.0.1",
    "sha": "940bd336248efae0f9ee5bc7b2d5c985887b16ac",
    "url": "https://api.github.com/repos/octocat/Hello-World/git/tags/940bd336248efae0f9ee5bc7b2d5c985887b16ac",
    "message": "initial version",
    "tagger": {
        "name": "Monalisa Octocat",
        "email": "octocat@github.com",
        "date": "2014-11-07T22:01:45Z",
    },
    "object": {
        "type": "commit",
        "sha": "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c",
        "url": "https://api.github.com/repos/octocat/Hello-World/git/commits/c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c",
    },
    "verification": {
        "verified": False,
        "reason": "unsigned",
        "signature": None,
        "payload": None,
    },
}


class GitHubAsyncRESTTagsTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTTags

    def assertTag(self, tag: Tag):  # pylint: disable=invalid-name
        self.assertEqual(
            tag.node_id,
            "MDM6VGFnOTQwYmQzMzYyNDhlZmFlMGY5ZWU1YmM3YjJkNWM5ODU4ODdiMTZhYw==",
        )
        self.assertEqual(tag.tag, "v0.0.1")
        self.assertEqual(tag.sha, "940bd336248efae0f9ee5bc7b2d5c985887b16ac")
        self.assertEqual(
            tag.url,
            "https://api.github.com/repos/octocat/Hello-World/git/tags/940bd336248efae0f9ee5bc7b2d5c985887b16ac",
        )
        self.assertEqual(tag.message, "initial version")

        tagger = tag.tagger
        self.assertEqual(tagger.name, "Monalisa Octocat")
        self.assertEqual(tagger.email, "octocat@github.com")
        self.assertEqual(
            tagger.date, datetime(2014, 11, 7, 22, 1, 45, tzinfo=timezone.utc)
        )

        tag_object = tag.object
        self.assertEqual(tag_object.type, GitObjectType.COMMIT)
        self.assertEqual(
            tag_object.sha, "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c"
        )
        self.assertEqual(
            tag_object.url,
            "https://api.github.com/repos/octocat/Hello-World/git/commits/c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c",
        )

        verification = tag.verification
        self.assertFalse(verification.verified)
        self.assertEqual(verification.reason, VerificationReason.UNSIGNED)
        self.assertIsNone(verification.payload)
        self.assertIsNone(verification.signature)

    async def test_create(self):
        response = create_response()
        response.json.return_value = TAG_JSON
        self.client.post.return_value = response

        tag = await self.api.create(
            "octocat/Hello-World",
            "v0.0.1",
            "initial version",
            "Monalisa Octocat",
            "octocat@github.com",
            "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c",
        )

        self.client.post.assert_awaited_once_with(
            "/repos/octocat/Hello-World/git/tags",
            data={
                "tag": "v0.0.1",
                "message": "initial version",
                "object": "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c",
                "type": "commit",
                "tagger": {
                    "name": "Monalisa Octocat",
                    "email": "octocat@github.com",
                },
            },
        )

        self.assertTag(tag)

    async def test_create_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.create(
                "octocat/Hello-World",
                "v0.0.1",
                "initial version",
                "Monalisa Octocat",
                "octocat@github.com",
                "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c",
            )

        self.client.post.assert_awaited_once_with(
            "/repos/octocat/Hello-World/git/tags",
            data={
                "tag": "v0.0.1",
                "message": "initial version",
                "object": "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c",
                "type": "commit",
                "tagger": {
                    "name": "Monalisa Octocat",
                    "email": "octocat@github.com",
                },
            },
        )

    async def test_create_tag_reference(self):
        response = create_response()
        self.client.post.return_value = response

        await self.api.create_tag_reference(
            "foo/bar", "v1.0.0", "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c"
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/git/refs",
            data={
                "ref": "refs/tags/v1.0.0",
                "sha": "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c",
            },
        )

    async def test_create_tag_reference_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.create_tag_reference(
                "foo/bar", "v1.0.0", "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c"
            )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/git/refs",
            data={
                "ref": "refs/tags/v1.0.0",
                "sha": "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c",
            },
        )

    async def test_get(self):
        response = create_response()
        response.json.return_value = TAG_JSON
        self.client.get.return_value = response

        tag = await self.api.get("octocat/Hello-World", "v0.0.1")

        self.client.get.assert_awaited_once_with(
            "/repos/octocat/Hello-World/git/tags/v0.0.1"
        )

        self.assertTag(tag)

    async def test_get_failure(self):
        response = create_response()
        self.client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.get("octocat/Hello-World", "v0.0.1")

        self.client.get.assert_awaited_once_with(
            "/repos/octocat/Hello-World/git/tags/v0.0.1"
        )
