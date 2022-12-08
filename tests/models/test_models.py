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

# pylint: disable=no-member, disallowed-name

import unittest

from pontos.models import Model, ModelAttribute, dotted_attributes


class ModelTestCase(unittest.TestCase):
    def test_from_dict(self):
        model = Model.from_dict(
            {
                "x": 1,
                "y": 2,
                "hello": "World",
                "baz": [1, 2, 3],
                "bar": {"a": "b"},
            }
        )

        self.assertEqual(model.x, 1)
        self.assertEqual(model.y, 2)
        self.assertEqual(model.hello, "World")
        self.assertEqual(model.baz, [1, 2, 3])
        self.assertEqual(model.bar.a, "b")


class DottedAttributesTestCase(unittest.TestCase):
    def test_with_new_class(self):
        class Foo:
            pass

        foo = Foo()
        attrs = {"bar": 123, "hello": "World", "baz": [1, 2, 3]}

        foo = dotted_attributes(foo, attrs)

        self.assertEqual(foo.bar, 123)
        self.assertEqual(foo.baz, [1, 2, 3])
        self.assertEqual(foo.hello, "World")

    def test_with_github_model_attribute(self):
        foo = ModelAttribute()
        attrs = {"bar": 123, "hello": "World", "baz": [1, 2, 3]}

        foo = dotted_attributes(foo, attrs)

        self.assertEqual(foo.bar, 123)
        self.assertEqual(foo.baz, [1, 2, 3])
        self.assertEqual(foo.hello, "World")
