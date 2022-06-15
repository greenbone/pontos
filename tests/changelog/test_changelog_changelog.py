# -*- coding: utf-8 -*-
# Copyright (C) 2020-2022 Greenbone Networks GmbH
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
import unittest

from pontos import changelog

UNRELEASED = """
## Unreleased
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...main 
"""


class ChangelogTestCase(unittest.TestCase):
    def test_return_none_when_no_unreleased_information_found(self):
        test_md = """
# Changelog
something, somehing
- unreleased
- not unreleased
## 1.0.0
### added
- cool stuff 1
- cool stuff 2
"""
        _, cl = changelog.update(test_md, "", "")
        self.assertEqual(cl, "")

    def test_find_unreleased_information_before_another_version(self):
        test_md = f"""
# Changelog
something, somehing
- unreleased
- not unreleased
{UNRELEASED}
## 1.0.0
### added
- cool stuff 1
- cool stuff 2
        """
        changed = """
## Unreleased
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...main 
"""

        _, result = changelog.update(test_md, "", "")
        self.assertEqual(result.strip(), changed.strip())


def test_find_unreleased_information_no_other_version(self):
    test_md = UNRELEASED

    _, result = changelog.update(test_md, "", "")
    self.assertEqual(result.strip(), UNRELEASED.strip())


def test_find_unreleased_information_before_after_another_version(self):
    test_md = f"""
# Changelog
something, somehing
- unreleased
- not unreleased
## 1.0.0
### added
- cool stuff 1
- cool stuff 2
{UNRELEASED}
        """

    _, result = changelog.update(test_md, "", "")
    self.assertEqual(result.strip(), UNRELEASED.strip())
