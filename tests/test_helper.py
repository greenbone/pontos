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
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from pontos.helper import DEFAULT_TIMEOUT, DownloadProgressIterable, download


class DownloadProgressIterableTestCase(unittest.TestCase):
    def test_properties(self):
        content = ["foo", "bar", "baz"]
        destination = Path("foo")
        length = 123
        url = "bar"
        download_progress = DownloadProgressIterable(
            content_iterator=content,
            destination=destination,
            length=length,
            url=url,
        )

        self.assertEqual(download_progress.url, url)
        self.assertEqual(download_progress.length, length)
        self.assertEqual(download_progress.destination, destination)

    def test_progress_without_length(self):
        content = ["foo", "bar", "baz"]
        destination = MagicMock()
        writer = MagicMock()
        context_manager = MagicMock()
        context_manager.__enter__.return_value = writer
        destination.open.return_value = context_manager
        download_progress = DownloadProgressIterable(
            content_iterator=content,
            destination=destination,
            length=None,
            url="foo",
        )

        self.assertEqual(download_progress.url, "foo")

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
        download_progress = DownloadProgressIterable(
            content_iterator=content,
            destination=destination,
            length=9,
            url="foo",
        )

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
        download_progress = DownloadProgressIterable(
            content_iterator=content,
            destination=destination,
            length=9,
            url="foo",
        )

        download_progress.run()
        destination.open.assert_called_once()
        writer.write.assert_has_calls((call("foo"), call("bar"), call("baz")))


class DownloadTestCase(unittest.TestCase):
    @patch("pontos.github.api.httpx.stream")
    def test_download_without_destination(
        self,
        requests_mock: MagicMock,
    ):
        response = MagicMock()
        response.iter_bytes.return_value = [b"foo", b"bar", b"baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = None
        response_stream = MagicMock()
        response_stream.__enter__.return_value = response
        requests_mock.return_value = response_stream

        with download(
            "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz"  # pylint: disable=line-too-long
        ) as download_progress:

            requests_mock.assert_called_once_with(
                "GET",
                "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz",  # pylint: disable=line-too-long
                follow_redirects=True,
                timeout=DEFAULT_TIMEOUT,
            )
            response_headers.get.assert_called_once_with("content-length")

            self.assertIsNone(download_progress.length)
            self.assertEqual(
                download_progress.destination, Path("v21.11.0.tar.gz")
            )

            it = iter(download_progress)
            progress = next(it)
            self.assertIsNone(progress)
            progress = next(it)
            self.assertIsNone(progress)
            progress = next(it)
            self.assertIsNone(progress)

            with self.assertRaises(StopIteration):
                next(it)

            download_progress.destination.unlink()

    @patch("pontos.github.api.Path")
    @patch("pontos.github.api.httpx.stream")
    def test_download_with_content_length(
        self, requests_mock: MagicMock, path_mock: MagicMock
    ):
        response = MagicMock()
        response.iter_bytes.return_value = [b"foo", b"bar", b"baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = "9"
        response_stream = MagicMock()
        response_stream.__enter__.return_value = response
        requests_mock.return_value = response_stream

        download_file = path_mock()
        file_mock = MagicMock()
        file_mock.__enter__.return_value = file_mock
        download_file.open.return_value = file_mock

        with download(
            "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz",  # pylint: disable=line-too-long
            download_file,
        ) as download_progress:

            requests_mock.assert_called_once_with(
                "GET",
                "https://github.com/greenbone/pontos/archive/refs/tags/v21.11.0.tar.gz",  # pylint: disable=line-too-long
                timeout=DEFAULT_TIMEOUT,
                follow_redirects=True,
            )
            response_headers.get.assert_called_once_with("content-length")

            self.assertEqual(download_progress.length, 9)

            it = iter(download_progress)

            progress = next(it)
            self.assertEqual(progress, 1 / 3)
            file_mock.write.assert_called_with(b"foo")

            progress = next(it)
            self.assertEqual(progress, 2 / 3)
            file_mock.write.assert_called_with(b"bar")

            progress = next(it)
            self.assertEqual(progress, 1)
            file_mock.write.assert_called_with(b"baz")

            with self.assertRaises(StopIteration):
                next(it)
