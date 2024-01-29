# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import io
import unittest
from argparse import ArgumentParser
from contextlib import redirect_stderr

from pontos.github.script.errors import GitHubScriptError
from pontos.github.script.load import (
    load_script,
    run_add_arguments_function,
    run_github_script_function,
)
from pontos.testing import temp_file, temp_python_module
from tests import IsolatedAsyncioTestCase


class LoadScriptTestCase(unittest.TestCase):
    def test_load_script(self):
        with (
            temp_file("def foo():\n\treturn 1", name="foo.py") as f,
            load_script(f) as module,
        ):
            self.assertIsNotNone(module)
            self.assertIsNotNone(module.foo)
            self.assertEqual(module.foo(), 1)

    def test_load_script_module(self):
        with (
            temp_python_module(
                "def foo():\n\treturn 1", name="github-foo-script"
            ),
            load_script("github-foo-script") as module,
        ):
            self.assertIsNotNone(module)
            self.assertIsNotNone(module.foo)
            self.assertEqual(module.foo(), 1)

    def test_load_script_failure(self):
        with self.assertRaisesRegex(
            ModuleNotFoundError, "No module named 'baz'"
        ):
            with load_script("foo/bar/baz.py"):
                pass


class RunAddArgumentsFunction(unittest.TestCase):
    def test_add_arguments_function(self):
        with (
            temp_file(
                "def add_script_arguments(parser):\n\t"
                "parser.add_argument('--foo')",
                name="foo.py",
            ) as f,
            load_script(f) as module,
        ):
            parser = ArgumentParser()
            run_add_arguments_function(module, parser)
            args = parser.parse_args(["--foo", "123"])
            self.assertEqual(args.foo, "123")

    def test_no_add_arguments_function(self):
        with (
            temp_file(
                "def foo():\n\tpass",
                name="foo.py",
            ) as f,
            load_script(f) as module,
        ):
            parser = ArgumentParser()
            run_add_arguments_function(module, parser)
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                parser.parse_args(["--foo", "123"])


class RunGithubScriptFunctionTestCase(IsolatedAsyncioTestCase):
    def test_run_async_github_script_function(self):
        with (
            temp_file(
                "async def github_script(api, args):\n\treturn 1",
                name="foo.py",
            ) as f,
            load_script(f) as module,
        ):
            self.assertEqual(
                run_github_script_function(module, "123", 123, {}), 1
            )

    def test_sync_github_script_function_not_supported(self):
        with (
            temp_file(
                "def github_script(api, args):\n\treturn 1",
                name="foo.py",
            ) as f,
            load_script(f) as module,
        ):
            with self.assertRaises(GitHubScriptError):
                run_github_script_function(module, "123", 123, {})

    def test_no_github_script_function(self):
        with (
            temp_file(
                "def foo():\n\tpass",
                name="foo.py",
            ) as f,
            load_script(f) as module,
        ):
            with self.assertRaises(GitHubScriptError):
                run_github_script_function(module, "123", 123, {})
