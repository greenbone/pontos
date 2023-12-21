# SPDX-FileCopyrightText: 2021-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

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
            "::warning file=bar,line=123,endLine=234,col=1,endColumn=2,title=Foo Bar::foo"  # pylint: disable=line-too-long # noqa: E501
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
            "::error file=bar,line=123,endLine=234,col=1,endColumn=2,title=Foo Bar::foo"  # pylint: disable=line-too-long # noqa: E501
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
            "::notice file=bar,line=123,endLine=234,col=1,endColumn=2,title=Foo Bar::foo"  # pylint: disable=line-too-long # noqa: E501
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

    @patch.dict("os.environ", {}, clear=True)
    def test_output_no_env(self):
        with self.assertRaises(GitHubActionsError):
            ActionIO.output("foo", "bar")

    @patch.dict("os.environ", {"GITHUB_OUTPUT": ""}, clear=True)
    def test_output_empty_env(self):
        with self.assertRaises(GitHubActionsError):
            ActionIO.output("foo", "bar")

    @patch.dict("os.environ", {}, clear=True)
    def test_no_github_output(self):
        self.assertFalse(ActionIO.has_output())

    @patch.dict(
        "os.environ", {"GITHUB_OUTPUT": "/foo/github.output"}, clear=True
    )
    def test_has_github_output(self):
        self.assertTrue(ActionIO.has_output())

    def test_out(self):
        with temp_directory() as temp_dir:
            outfile = temp_dir / "github.output"
            with patch.dict(
                "os.environ",
                {"GITHUB_OUTPUT": str(outfile.absolute())},
                clear=True,
            ):
                with ActionIO.out() as output:
                    output.write("foo", "bar")

            self.assertEqual(outfile.read_text(encoding="utf8"), "foo=bar\n")

    @patch.dict("os.environ", {}, clear=True)
    def test_out_failure(self):
        with self.assertRaisesRegex(
            GitHubActionsError,
            "GITHUB_OUTPUT environment variable not set. Can't write "
            "action output.",
        ):
            with ActionIO.out():
                pass
