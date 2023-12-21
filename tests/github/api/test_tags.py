# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=too-many-lines, redefined-builtin, line-too-long
# ruff: noqa: E501

from datetime import datetime, timezone
from unittest.mock import MagicMock

import httpx

from pontos.github.api.tags import GitHubAsyncRESTTags
from pontos.github.models.tag import GitObjectType, Tag, VerificationReason
from tests import AsyncIteratorMock, aiter, anext
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


TAGS_JSON = [
    {
        "name": "v0.1.0",
        "zipball_url": "https://api.github.com/repos/foo/ui/zipball/refs/tags/v0.1.0",
        "tarball_url": "https://api.github.com/repos/foo/ui/tarball/refs/tags/v0.1.0",
        "commit": {
            "sha": "b55408280162c20cf0ffef155618270d26fe7352",
            "url": "https://api.github.com/repos/foo/ui/commits/b55408280162c20cf0ffef155618270d26fe7352",
        },
        "node_id": "REF_kwDOHeuT1rByZWZzL3RhZ3MvdjAuMS4w",
    },
    {
        "name": "0.0.72",
        "zipball_url": "https://api.github.com/repos/foo/ui/zipball/refs/tags/0.0.72",
        "tarball_url": "https://api.github.com/repos/foo/ui/tarball/refs/tags/0.0.72",
        "commit": {
            "sha": "fd54097278df75332917d9d1a2d940083513a6b2",
            "url": "https://api.github.com/repos/foo/ui/commits/fd54097278df75332917d9d1a2d940083513a6b2",
        },
        "node_id": "REF_kwDOHeuT1rByZWZzL3RhZ3MvMC4wLjcy",
    },
]


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

    async def test_get_all(self):
        response = create_response()
        response.json.return_value = TAGS_JSON
        self.client.get_all.return_value = AsyncIteratorMock([response])

        async_it = aiter(self.api.get_all("foo"))

        tag = await anext(async_it)
        self.assertEqual(tag.name, "v0.1.0")
        self.assertEqual(
            tag.commit.sha, "b55408280162c20cf0ffef155618270d26fe7352"
        )
        self.assertEqual(
            tag.commit.url,
            "https://api.github.com/repos/foo/ui/commits/b55408280162c20cf0ffef155618270d26fe7352",
        )
        self.assertEqual(
            tag.zipball_url,
            "https://api.github.com/repos/foo/ui/zipball/refs/tags/v0.1.0",
        )
        self.assertEqual(
            tag.tarball_url,
            "https://api.github.com/repos/foo/ui/tarball/refs/tags/v0.1.0",
        )
        self.assertEqual(tag.node_id, "REF_kwDOHeuT1rByZWZzL3RhZ3MvdjAuMS4w")
        tag2 = await anext(async_it)
        self.assertEqual(tag2.name, "0.0.72")
