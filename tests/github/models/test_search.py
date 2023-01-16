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
