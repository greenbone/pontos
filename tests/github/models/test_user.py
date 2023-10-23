# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

import unittest
from datetime import datetime, timezone

from pontos.github.models.user import (
    EmailInformation,
    SSHPublicKey,
    SSHPublicKeyExtended,
)


class SSHPublicKeyTestCase(unittest.TestCase):
    def test_from_dict(self):
        key = SSHPublicKey.from_dict({"id": 1, "key": "ssh-rsa AAA..."})

        self.assertEqual(key.id, 1)
        self.assertEqual(key.key, "ssh-rsa AAA...")


class SSHPublicKeyExtendedTestCase(unittest.TestCase):
    def test_from_dict(self):
        key = SSHPublicKeyExtended.from_dict(
            {
                "key": "2Sg8iYjAxxmI2LvUXpJjkYrMxURPc8r+dB7TJyvv1234",
                "id": 2,
                "url": "https://api.github.com/user/keys/2",
                "title": "ssh-rsa AAAAB3NzaC1yc2EAAA",
                "created_at": "2020-06-11T21:31:57Z",
                "verified": False,
                "read_only": False,
            }
        )

        self.assertEqual(key.id, 2)
        self.assertEqual(
            key.key, "2Sg8iYjAxxmI2LvUXpJjkYrMxURPc8r+dB7TJyvv1234"
        )
        self.assertEqual(key.url, "https://api.github.com/user/keys/2")
        self.assertEqual(key.title, "ssh-rsa AAAAB3NzaC1yc2EAAA")
        self.assertFalse(key.verified)
        self.assertFalse(key.read_only)
        self.assertEqual(
            key.created_at,
            datetime(2020, 6, 11, 21, 31, 57, tzinfo=timezone.utc),
        )


class EmailInformationTestCase(unittest.TestCase):
    def test_from_dict(self):
        email = EmailInformation.from_dict(
            {
                "email": "octocat@github.com",
                "verified": True,
                "primary": True,
                "visibility": "public",
            }
        )

        self.assertEqual(email.email, "octocat@github.com")
        self.assertEqual(email.visibility, "public")
        self.assertTrue(email.primary)
        self.assertTrue(email.verified)
