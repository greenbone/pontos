# Copyright (C) 2021-2022 Greenbone Networks GmbH
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
from unittest.mock import patch

from pontos.github.actions.core import ActionIO, Console
from pontos.github.actions.errors import GitHubActionsError
from pontos.testing import temp_directory


@patch("builtins.print")
class ConsoleTestCase(unittest.TestCase):
    def test_start_group(self, print_mock):
        Console.start_group("Foo")
        print_mock.assert_called_once_with("::group::Foo")

    def test_end_group(self, print_mock):
        Console.end_group()
        print_mock.assert_called_once_with("::endgroup::")

    def test_group(self, print_mock):
        with Console.group("Foo"):
            print_mock.assert_called_once_with("::group::Foo")

        print_mock.assert_called_with("::endgroup::")

    def test_warning(self, print_mock):
        Console.warning(
            "foo",
            name="bar",
            line="123",
            end_line="234",
            column="1",
            end_column="2",
            title="Foo Bar",
        )
        print_mock.assert_called_once_with(
            "::warning file=bar,line=123,endLine=234,col=1,endColumn=2,title=Foo Bar::foo"  # pylint: disable=line-too-long
        )

    def test_error(self, print_mock):
        Console.error(
            "foo",
            name="bar",
            line="123",
            end_line="234",
            column="1",
            end_column="2",
            title="Foo Bar",
        )
        print_mock.assert_called_once_with(
            "::error file=bar,line=123,endLine=234,col=1,endColumn=2,title=Foo Bar::foo"  # pylint: disable=line-too-long
        )

    def test_notice(self, print_mock):
        Console.notice(
            "foo",
            name="bar",
            line="123",
            end_line="234",
            column="1",
            end_column="2",
            title="Foo Bar",
        )
        print_mock.assert_called_once_with(
            "::notice file=bar,line=123,endLine=234,col=1,endColumn=2,title=Foo Bar::foo"  # pylint: disable=line-too-long
        )

    def test_log(self, print_mock):
        Console.log("foo")

        print_mock.assert_called_once_with("foo")

    def test_debug(self, print_mock):
        Console.debug("foo")

        print_mock.assert_called_once_with("::debug::foo")


class ActionIOTestCase(unittest.TestCase):
    @patch.dict(
        "os.environ", {"INPUT_FOO": "1234", "INPUT_FOO_BAR": "2345"}, clear=True
    )
    def test_input(self):
        self.assertEqual(ActionIO.input("foo"), "1234")
        self.assertEqual(ActionIO.input("FOO"), "1234")
        self.assertEqual(ActionIO.input("FoO"), "1234")

        self.assertEqual(ActionIO.input("foo bar"), "2345")
        self.assertEqual(ActionIO.input("FOO_BAR"), "2345")
        self.assertEqual(ActionIO.input("FoO BaR"), "2345")

    def test_output(self):
        with temp_directory() as temp_dir:
            file_path = temp_dir / "github.output"

            with patch.dict(
                "os.environ", {"GITHUB_OUTPUT": str(file_path)}, clear=True
            ):
                ActionIO.output("foo", "bar")
                ActionIO.output("lorem", "ipsum")

                output = file_path.read_text(encoding="utf8")

                self.assertEqual(output, "foo=bar\nlorem=ipsum\n")

    def test_output_no_env(self):
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(
            GitHubActionsError
        ):
            ActionIO.output("foo", "bar")

    def test_output_empty_env(self):
        with patch.dict(
            "os.environ", {"GITHUB_OUTPUT": ""}, clear=True
        ), self.assertRaises(GitHubActionsError):
            ActionIO.output("foo", "bar")
