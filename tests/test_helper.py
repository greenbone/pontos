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

import unittest
from unittest.mock import MagicMock, call

from pontos.helper import DownloadProgressIterable


class DownloadProgressIterableTestCase(unittest.TestCase):
    def test_progress_without_length(self):
        content = ["foo", "bar", "baz"]
        destination = MagicMock()
        writer = MagicMock()
        context_manager = MagicMock()
        context_manager.__enter__.return_value = writer
        destination.open.return_value = context_manager
        download_progress = DownloadProgressIterable(content, destination, None)

        it = iter(download_progress)
        progress = next(it)
        writer.write.assert_called_with("foo")
        self.assertIsNone(progress)
        progress = next(it)
        writer.write.assert_called_with("bar")
        self.assertIsNone(progress)
        progress = next(it)
        writer.write.assert_called_with("baz")
        self.assertIsNone(progress)

        with self.assertRaises(StopIteration):
            next(it)

    def test_progress(self):
        content = ["foo", "bar", "baz"]
        destination = MagicMock()
        writer = MagicMock()
        context_manager = MagicMock()
        context_manager.__enter__.return_value = writer
        destination.open.return_value = context_manager
        download_progress = DownloadProgressIterable(content, destination, 9)

        it = iter(download_progress)
        progress = next(it)
        writer.write.assert_called_with("foo")
        self.assertEqual(progress, 1 / 3.0)
        progress = next(it)
        writer.write.assert_called_with("bar")
        self.assertEqual(progress, 2 / 3.0)
        progress = next(it)
        writer.write.assert_called_with("baz")
        self.assertEqual(progress, 1)

        with self.assertRaises(StopIteration):
            next(it)

    def test_run(self):
        content = ["foo", "bar", "baz"]
        destination = MagicMock()
        writer = MagicMock()
        context_manager = MagicMock()
        context_manager.__enter__.return_value = writer
        destination.open.return_value = context_manager
        download_progress = DownloadProgressIterable(content, destination, 9)

        download_progress.run()
        destination.open.assert_called_once()
        writer.write.assert_has_calls((call("foo"), call("bar"), call("baz")))
