# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later


import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from pontos.git import Git
from pontos.release.helper import ReleaseType
from pontos.release.show import (
    OutputFormat,
    ShowReleaseCommand,
    ShowReleaseReturnValue,
)
from pontos.testing import temp_file, temp_git_repository
from pontos.version.schemes import PEP440VersioningScheme


def setup_git_repo(temp_git: Path) -> None:
    some_file = temp_git / "some-file.txt"
    some_file.touch()

    git = Git()
    git.add(some_file)
    git.commit("Add some file", gpg_sign=False, verify=False)
    git.tag("v1.0.0", sign=False)


class ShowTestCase(unittest.TestCase):
    def test_env_output(self):
        terminal = MagicMock()
        with temp_git_repository() as temp_git:
            setup_git_repo(temp_git)

            show_cmd = ShowReleaseCommand(
                terminal=terminal, error_terminal=MagicMock()
            )

            return_val = show_cmd.run(
                versioning_scheme=PEP440VersioningScheme,
                release_type=ReleaseType.PATCH,
                release_version=None,
                git_tag_prefix="v",
                output_format=OutputFormat.ENV,
            )

            self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

            terminal.print.assert_has_calls(
                [
                    call("LAST_RELEASE_VERSION=1.0.0"),
                    call("LAST_RELEASE_VERSION_MAJOR=1"),
                    call("LAST_RELEASE_VERSION_MINOR=0"),
                    call("LAST_RELEASE_VERSION_PATCH=0"),
                    call("RELEASE_VERSION=1.0.1"),
                    call("RELEASE_VERSION_MAJOR=1"),
                    call("RELEASE_VERSION_MINOR=0"),
                    call("RELEASE_VERSION_PATCH=1"),
                ]
            )

            return_val = show_cmd.run(
                versioning_scheme=PEP440VersioningScheme,
                release_type=ReleaseType.MINOR,
                release_version=None,
                git_tag_prefix="v",
                output_format=OutputFormat.ENV,
            )

            self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

            terminal.print.assert_has_calls(
                [
                    call("LAST_RELEASE_VERSION=1.0.0"),
                    call("LAST_RELEASE_VERSION_MAJOR=1"),
                    call("LAST_RELEASE_VERSION_MINOR=0"),
                    call("LAST_RELEASE_VERSION_PATCH=0"),
                    call("RELEASE_VERSION=1.1.0"),
                    call("RELEASE_VERSION_MAJOR=1"),
                    call("RELEASE_VERSION_MINOR=1"),
                    call("RELEASE_VERSION_PATCH=0"),
                ]
            )

            return_val = show_cmd.run(
                versioning_scheme=PEP440VersioningScheme,
                release_type=ReleaseType.MAJOR,
                release_version=None,
                git_tag_prefix="v",
                output_format=OutputFormat.ENV,
            )

            self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

            terminal.print.assert_has_calls(
                [
                    call("LAST_RELEASE_VERSION=1.0.0"),
                    call("LAST_RELEASE_VERSION_MAJOR=1"),
                    call("LAST_RELEASE_VERSION_MINOR=0"),
                    call("LAST_RELEASE_VERSION_PATCH=0"),
                    call("RELEASE_VERSION=2.0.0"),
                    call("RELEASE_VERSION_MAJOR=2"),
                    call("RELEASE_VERSION_MINOR=0"),
                    call("RELEASE_VERSION_PATCH=0"),
                ]
            )

    def test_json_output(self):
        terminal = MagicMock()
        with temp_git_repository() as temp_git:
            setup_git_repo(temp_git)

            show_cmd = ShowReleaseCommand(
                terminal=terminal, error_terminal=MagicMock()
            )

            return_val = show_cmd.run(
                versioning_scheme=PEP440VersioningScheme,
                release_type=ReleaseType.PATCH,
                release_version=None,
                git_tag_prefix="v",
                output_format=OutputFormat.JSON,
            )

            expected = """{
  "release_version": "1.0.1",
  "release_version_major": 1,
  "release_version_minor": 0,
  "release_version_patch": 1,
  "last_release_version": "1.0.0",
  "last_release_version_major": 1,
  "last_release_version_minor": 0,
  "last_release_version_patch": 0
}"""

            self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

            terminal.print.assert_called_once_with(expected)
            terminal.reset_mock()

            return_val = show_cmd.run(
                versioning_scheme=PEP440VersioningScheme,
                release_type=ReleaseType.MINOR,
                release_version=None,
                git_tag_prefix="v",
                output_format=OutputFormat.JSON,
            )

            expected = """{
  "release_version": "1.1.0",
  "release_version_major": 1,
  "release_version_minor": 1,
  "release_version_patch": 0,
  "last_release_version": "1.0.0",
  "last_release_version_major": 1,
  "last_release_version_minor": 0,
  "last_release_version_patch": 0
}"""

            self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

            terminal.print.assert_called_once_with(expected)
            terminal.reset_mock()

            return_val = show_cmd.run(
                versioning_scheme=PEP440VersioningScheme,
                release_type=ReleaseType.MAJOR,
                release_version=None,
                git_tag_prefix="v",
                output_format=OutputFormat.JSON,
            )

            expected = """{
  "release_version": "2.0.0",
  "release_version_major": 2,
  "release_version_minor": 0,
  "release_version_patch": 0,
  "last_release_version": "1.0.0",
  "last_release_version_major": 1,
  "last_release_version_minor": 0,
  "last_release_version_patch": 0
}"""

            self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

            terminal.print.assert_called_once_with(expected)

    def test_github_action_output(self):
        terminal = MagicMock()
        with temp_git_repository() as temp_git:
            setup_git_repo(temp_git)

            show_cmd = ShowReleaseCommand(
                terminal=terminal, error_terminal=MagicMock()
            )

            output_file = temp_git.absolute() / "output"

            with patch.dict(
                "os.environ", {"GITHUB_OUTPUT": f"{output_file}"}, clear=True
            ):
                return_val = show_cmd.run(
                    versioning_scheme=PEP440VersioningScheme,
                    release_type=ReleaseType.PATCH,
                    release_version=None,
                    git_tag_prefix="v",
                    output_format=OutputFormat.GITHUB_ACTION,
                )

                self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

                expected = """last_release_version=1.0.0
last_release_version_major=1
last_release_version_minor=0
last_release_version_patch=0
release_version_major=1
release_version_minor=0
release_version_patch=1
release_version=1.0.1
"""
                actual = output_file.read_text(encoding="utf8")

                self.assertEqual(expected, actual)

                output_file.unlink()

                return_val = show_cmd.run(
                    versioning_scheme=PEP440VersioningScheme,
                    release_type=ReleaseType.MINOR,
                    release_version=None,
                    git_tag_prefix="v",
                    output_format=OutputFormat.GITHUB_ACTION,
                )

                self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

                expected = """last_release_version=1.0.0
last_release_version_major=1
last_release_version_minor=0
last_release_version_patch=0
release_version_major=1
release_version_minor=1
release_version_patch=0
release_version=1.1.0
"""
                actual = output_file.read_text(encoding="utf8")

                self.assertEqual(expected, actual)

                output_file.unlink()

                return_val = show_cmd.run(
                    versioning_scheme=PEP440VersioningScheme,
                    release_type=ReleaseType.MAJOR,
                    release_version=None,
                    git_tag_prefix="v",
                    output_format=OutputFormat.GITHUB_ACTION,
                )

                self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

                expected = """last_release_version=1.0.0
last_release_version_major=1
last_release_version_minor=0
last_release_version_patch=0
release_version_major=2
release_version_minor=0
release_version_patch=0
release_version=2.0.0
"""
                actual = output_file.read_text(encoding="utf8")

                self.assertEqual(expected, actual)

                output_file.unlink()

    def test_initial_release(self):
        terminal = MagicMock()
        with temp_git_repository():
            show_cmd = ShowReleaseCommand(
                terminal=terminal, error_terminal=MagicMock()
            )

            return_val = show_cmd.run(
                versioning_scheme=PEP440VersioningScheme,
                release_type=ReleaseType.VERSION,
                release_version=PEP440VersioningScheme.parse_version("1.0.0"),
                git_tag_prefix="v",
                output_format=OutputFormat.ENV,
            )

            self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

            terminal.print.assert_has_calls(
                [
                    call("LAST_RELEASE_VERSION="),
                    call("LAST_RELEASE_VERSION_MAJOR="),
                    call("LAST_RELEASE_VERSION_MINOR="),
                    call("LAST_RELEASE_VERSION_PATCH="),
                    call("RELEASE_VERSION=1.0.0"),
                    call("RELEASE_VERSION_MAJOR=1"),
                    call("RELEASE_VERSION_MINOR=0"),
                    call("RELEASE_VERSION_PATCH=0"),
                ]
            )

            terminal.reset_mock()

            return_val = show_cmd.run(
                versioning_scheme=PEP440VersioningScheme,
                release_type=ReleaseType.VERSION,
                release_version=PEP440VersioningScheme.parse_version("1.0.0"),
                git_tag_prefix="v",
                output_format=OutputFormat.JSON,
            )

            expected = """{
  "release_version": "1.0.0",
  "release_version_major": 1,
  "release_version_minor": 0,
  "release_version_patch": 0,
  "last_release_version": "",
  "last_release_version_major": "",
  "last_release_version_minor": "",
  "last_release_version_patch": ""
}"""

            self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

            terminal.print.assert_called_once_with(expected)

            with temp_file(name="output") as output_file, patch.dict(
                "os.environ", {"GITHUB_OUTPUT": f"{output_file}"}, clear=True
            ):
                return_val = show_cmd.run(
                    versioning_scheme=PEP440VersioningScheme,
                    release_type=ReleaseType.VERSION,
                    release_version=PEP440VersioningScheme.parse_version(
                        "1.0.0"
                    ),
                    git_tag_prefix="v",
                    output_format=OutputFormat.GITHUB_ACTION,
                )

                self.assertEqual(return_val, ShowReleaseReturnValue.SUCCESS)

                expected = """last_release_version=
last_release_version_major=
last_release_version_minor=
last_release_version_patch=
release_version_major=1
release_version_minor=0
release_version_patch=0
release_version=1.0.0
"""
                actual = output_file.read_text(encoding="utf8")

                self.assertEqual(expected, actual)
