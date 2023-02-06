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

# pylint: disable=redefined-builtin,disallowed-name

import unittest
from enum import Enum
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import httpx

from pontos.errors import PontosError
from pontos.helper import (
    DEFAULT_TIMEOUT,
    AsyncDownloadProgressIterable,
    DownloadProgressIterable,
    add_sys_path,
    deprecated,
    download,
    download_async,
    ensure_unload_module,
    enum_or_value,
    parse_timedelta,
    snake_case,
    unload_module,
)
from pontos.testing import temp_file, temp_python_module
from tests import (
    AsyncIteratorMock,
    AsyncMock,
    IsolatedAsyncioTestCase,
    aiter,
    anext,
)
from tests.github.api import create_response


class AsyncDownloadProgressIterableTestCase(IsolatedAsyncioTestCase):
    def test_properties(self):
        content_iterator = AsyncIteratorMock(["1", "2"])

        download_iterable = AsyncDownloadProgressIterable(
            content_iterator=content_iterator, length=2, url="https://foo.bar"
        )

        self.assertEqual(download_iterable.length, 2)
        self.assertEqual(download_iterable.url, "https://foo.bar")

    async def test_download_progress(self):
        content_iterator = AsyncIteratorMock(["1", "2"])

        download_iterable = AsyncDownloadProgressIterable(
            content_iterator=content_iterator, length=2, url="https://foo.bar"
        )

        it = aiter(download_iterable)
        content, progress = await anext(it)

        self.assertEqual(content, "1")
        self.assertEqual(progress, 50)

        content, progress = await anext(it)
        self.assertEqual(content, "2")
        self.assertEqual(progress, 100)

    async def test_download_progress_without_length(self):
        content_iterator = AsyncIteratorMock(["1", "2"])

        download_iterable = AsyncDownloadProgressIterable(
            content_iterator=content_iterator,
            length=None,
            url="https://foo.bar",
        )

        it = aiter(download_iterable)
        content, progress = await anext(it)

        self.assertEqual(content, "1")
        self.assertIsNone(progress)

        content, progress = await anext(it)
        self.assertEqual(content, "2")
        self.assertIsNone(progress)


class DownloadAsyncTestCase(IsolatedAsyncioTestCase):
    async def test_download_async(self):
        response = create_response()
        response.aiter_bytes.return_value = AsyncIteratorMock(["1", "2"])
        stream = AsyncMock()
        stream.__aenter__.return_value = response

        async with download_async(
            stream, content_length=2
        ) as download_iterable:
            it = aiter(download_iterable)
            content, progress = await anext(it)

            self.assertEqual(content, "1")
            self.assertEqual(progress, 50)

            content, progress = await anext(it)
            self.assertEqual(content, "2")
            self.assertEqual(progress, 100)

    async def test_download_async_content_length(self):
        response = create_response(headers=MagicMock())
        response.aiter_bytes.return_value = AsyncIteratorMock(["1", "2"])
        response.headers.get.return_value = 2
        stream = AsyncMock()
        stream.__aenter__.return_value = response

        async with download_async(stream) as download_iterable:
            it = aiter(download_iterable)
            content, progress = await anext(it)

            self.assertEqual(content, "1")
            self.assertEqual(progress, 50)

            content, progress = await anext(it)
            self.assertEqual(content, "2")
            self.assertEqual(progress, 100)

    async def test_download_async_failure(self):
        response = create_response()
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )
        stream = AsyncMock()
        stream.__aenter__.return_value = response

        with self.assertRaises(httpx.HTTPStatusError):
            async with download_async(stream, content_length=2):
                pass


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
    @patch("pontos.github.api.api.httpx.stream")
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
                headers=None,
                params=None,
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

    @patch("pontos.helper.Path")
    @patch("pontos.github.api.api.httpx.stream")
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
                headers=None,
                params=None,
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


class DeprecatedTestCase(unittest.TestCase):
    def test_function(self):
        @deprecated
        def foo():
            pass

        with self.assertWarnsRegex(DeprecationWarning, "foo is deprecated"):
            foo()

        @deprecated()
        def foo2():
            pass

        with self.assertWarnsRegex(DeprecationWarning, "foo2 is deprecated"):
            foo2()

    def test_function_with_since(self):
        @deprecated(since="1.2.3")
        def foo():
            pass

        with self.assertWarnsRegex(
            DeprecationWarning, "deprecated since version 1.2.3"
        ):
            foo()

    def test_function_with_reason(self):
        @deprecated("Because it is obsolete.")
        def foo():
            pass

        with self.assertWarnsRegex(
            DeprecationWarning, "Because it is obsolete"
        ):
            foo()

        @deprecated(reason="Because it is obsolete.")
        def foo2():
            pass

        with self.assertWarnsRegex(
            DeprecationWarning, "Because it is obsolete"
        ):
            foo2()

    def test_class(self):
        @deprecated
        class Foo:
            pass

        with self.assertWarnsRegex(DeprecationWarning, "Foo is deprecated"):
            Foo()

        @deprecated()
        class Foo2:
            pass

        with self.assertWarnsRegex(DeprecationWarning, "Foo2 is deprecated"):
            Foo2()

    def test_class_with_since(self):
        @deprecated(since="1.2.3")
        class Foo:
            pass

        with self.assertWarnsRegex(
            DeprecationWarning, "deprecated since version 1.2.3"
        ):
            Foo()

    def test_class_with_reason(self):
        @deprecated("Because it is obsolete.")
        class Foo:
            pass

        with self.assertWarnsRegex(
            DeprecationWarning, "Because it is obsolete"
        ):
            Foo()

        @deprecated(reason="Because it is obsolete.")
        class Foo2:
            pass

        with self.assertWarnsRegex(
            DeprecationWarning, "Because it is obsolete"
        ):
            Foo2()

    def test_method(self):
        class Foo:
            @deprecated
            def bar(self):
                pass

        with self.assertWarnsRegex(DeprecationWarning, "bar is deprecated"):
            Foo().bar()

        class Foo2:
            @deprecated
            def bar(self):
                pass

        with self.assertWarnsRegex(DeprecationWarning, "bar is deprecated"):
            Foo2().bar()

    def test_method_with_since(self):
        class Foo:
            @deprecated(since="1.2.3")
            def bar(self):
                pass

        with self.assertWarnsRegex(
            DeprecationWarning, "deprecated since version 1.2.3"
        ):
            Foo().bar()

    def test_method_with_reason(self):
        class Foo:
            @deprecated("Because it is obsolete.")
            def bar(self):
                pass

        with self.assertWarnsRegex(
            DeprecationWarning, "Because it is obsolete"
        ):
            Foo().bar()

        class Foo2:
            @deprecated(reason="Because it is obsolete.")
            def bar(self):
                pass

        with self.assertWarnsRegex(
            DeprecationWarning, "Because it is obsolete"
        ):
            Foo2().bar()


class AddSysPathTestCase(unittest.TestCase):
    def test_add_sys_path(self):
        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import mymodule

        with temp_file("", name="mymodule.py") as module_path, add_sys_path(
            module_path.parent
        ):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import mymodule

        unload_module("mymodule")


class EnsureUnloadModuleTestCase(unittest.TestCase):
    def test_ensure_unload_module(self):
        with temp_python_module(
            "def foo():\n  pass", name="bar"
        ), ensure_unload_module("bar"):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import bar

        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import bar

    def test_ensure_unload_module_exception(self):
        with self.assertRaisesRegex(ValueError, "Ipsum"):
            with temp_python_module(
                "def func():\n  raise ValueError('Ipsum')", name="bar"
            ), ensure_unload_module("bar"):
                # pylint: disable=import-error,import-outside-toplevel,unused-import
                import bar

                bar.func()

        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import bar

    def test_add_sys_path_exception(self):
        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import mymodule

        try:
            with temp_file("", name="mymodule.py") as module_path, add_sys_path(
                module_path.parent
            ):
                # pylint: disable=import-error,import-outside-toplevel,unused-import
                import mymodule

                raise ValueError()
        except ValueError:
            pass
        finally:
            unload_module("mymodule")

        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import mymodule


class SnakeCaseTestCase(unittest.TestCase):
    def test_snake_case(self):
        self.assertEqual(snake_case("CamelCase"), "camel_case")
        self.assertEqual(snake_case("camelCase"), "camel_case")
        self.assertEqual(snake_case("snakecase"), "snakecase")
        self.assertEqual(snake_case("snake_case"), "snake_case")


class EnumOrValueTestCase(unittest.TestCase):
    def test_value(self):
        self.assertEqual(enum_or_value(None), None)
        self.assertEqual(enum_or_value("foo"), "foo")
        self.assertEqual(enum_or_value(123), 123)

    def test_enum(self):
        class Foo(Enum):
            BAR = "bar"
            BAZ = "baz"

        self.assertEqual(enum_or_value(Foo.BAR), "bar")
        self.assertEqual(enum_or_value(Foo.BAZ), "baz")


class ParseTimedeltaTestCase(unittest.TestCase):
    def test_parse_complex(self):
        delta = parse_timedelta("1w2d4h5m6s")

        self.assertEqual(delta.days, 9)
        self.assertEqual(delta.seconds, 14706)

    def test_parse_weeks(self):
        delta = parse_timedelta("1w")
        self.assertEqual(delta.days, 7)
        self.assertEqual(delta.seconds, 0)

        delta = parse_timedelta("1.5w")
        self.assertEqual(delta.days, 10)
        self.assertEqual(delta.seconds, 43200)

    def test_parse_days(self):
        delta = parse_timedelta("1d")
        self.assertEqual(delta.days, 1)
        self.assertEqual(delta.seconds, 0)

        delta = parse_timedelta("1.5d")
        self.assertEqual(delta.days, 1)
        self.assertEqual(delta.seconds, 43200)

    def test_parse_hours(self):
        delta = parse_timedelta("1h")
        self.assertEqual(delta.days, 0)
        self.assertEqual(delta.seconds, 3600)

        delta = parse_timedelta("1.5h")
        self.assertEqual(delta.days, 0)
        self.assertEqual(delta.seconds, 5400)

    def test_parse_error(self):
        with self.assertRaises(PontosError):
            parse_timedelta("foo")

        with self.assertRaises(PontosError):
            parse_timedelta("1d2x")

        with self.assertRaises(PontosError):
            parse_timedelta("1,2d")
