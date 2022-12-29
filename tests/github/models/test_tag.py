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

from pontos.github.models.tag import GitObjectType, Tag, VerificationReason


class TagModelTestCase(unittest.TestCase):
    def test_from_dict(self):
        data = {
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

        tag = Tag.from_dict(data)

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
