# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=line-too-long, invalid-name

import unittest

from pontos.github.models.search import (
    InDescriptionQualifier,
    InNameQualifier,
    InReadmeQualifier,
    InTopicsQualifier,
    IsPrivateQualifier,
    IsPublicQualifier,
    NotQualifier,
    OrganizationQualifier,
    RepositoryQualifier,
    UserQualifier,
)


class QualifierTestCase(unittest.TestCase):
    def test_name(self):
        q = InNameQualifier()
        self.assertEqual(str(q), "in:name")

    def test_description(self):
        q = InDescriptionQualifier()
        self.assertEqual(str(q), "in:description")

    def test_topics(self):
        q = InTopicsQualifier()
        self.assertEqual(str(q), "in:topics")

    def test_readme(self):
        q = InReadmeQualifier()
        self.assertEqual(str(q), "in:readme")

    def test_not(self):
        q = NotQualifier(InNameQualifier())
        self.assertEqual(str(q), "-in:name")

    def test_repository(self):
        q = RepositoryQualifier("foo/bar")
        self.assertEqual(str(q), "repo:foo/bar")

    def test_organization(self):
        q = OrganizationQualifier("foo")
        self.assertEqual(str(q), "org:foo")

    def test_user(self):
        q = UserQualifier("foo")
        self.assertEqual(str(q), "user:foo")

    def test_is_public(self):
        q = IsPublicQualifier()
        self.assertEqual(str(q), "is:public")

    def test_is_private(self):
        q = IsPrivateQualifier()
        self.assertEqual(str(q), "is:private")
