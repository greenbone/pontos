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

# pylint: disable=line-too-long

import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from pontos.git.git import ConfigScope, Git
from pontos.release.main import parse_args
from pontos.release.prepare import PrepareReturnValue, prepare
from pontos.terminal.terminal import Terminal
from pontos.testing import temp_git_repository
from pontos.version.calculator import VersionCalculator
from pontos.version.errors import VersionError
from pontos.version.go import GoVersionCommand
from pontos.version.version import VersionCommand, VersionUpdate


def mock_terminal() -> MagicMock:
    return MagicMock(spec=Terminal)


@patch.dict("os.environ", {"GITHUB_TOKEN": "foo", "GITHUB_USER": "user"})
class PrepareTestCase(unittest.TestCase):
    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.find_signing_key", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.prepare.gather_project", autospec=True)
    def test_prepare_release_type_version(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        find_signing_key_mock: MagicMock,
        git_mock: MagicMock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.return_value = VersionUpdate(
            previous="0.0.0", new="0.0.1", changed_files=["MyProject.conf"]
        )
        create_changelog_mock.return_value = "A changelog text"
        find_signing_key_mock.return_value = "0815"

        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(released, PrepareReturnValue.SUCCESS)

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            "Automatic release to 0.0.1", verify=False, gpg_signing_key="0815"
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.1",
            message="Automatic release to 0.0.1",
            gpg_key_id="0815",
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.find_signing_key", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.prepare.gather_project", autospec=True)
    def test_prepare_release_type_calendar(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        find_signing_key_mock: MagicMock,
        git_mock: MagicMock,
    ):
        calculator = VersionCalculator()
        current_version = "21.6.0"
        calendar_version = calculator.next_calendar_version(current_version)
        version_command_mock = MagicMock(spec=VersionCommand)
        version_command_mock.get_current_version.return_value = current_version
        version_command_mock.get_version_calculator.return_value = calculator
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.return_value = VersionUpdate(
            previous=current_version,
            new=calendar_version,
            changed_files=["MyProject.conf"],
        )
        create_changelog_mock.return_value = "A changelog text"
        find_signing_key_mock.return_value = "0815"

        _, _, args = parse_args(
            ["prepare", "--project", "foo", "--release-type", "calendar"]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(released, PrepareReturnValue.SUCCESS)

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            f"Automatic release to {calendar_version}",
            verify=False,
            gpg_signing_key="0815",
        )
        git_mock.return_value.tag.assert_called_once_with(
            f"v{calendar_version}",
            message=f"Automatic release to {calendar_version}",
            gpg_key_id="0815",
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.find_signing_key", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.prepare.gather_project", autospec=True)
    def test_prepare_release_type_patch(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        find_signing_key_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = "21.6.0"
        next_patch_version = "21.6.1"
        calculator = VersionCalculator()
        version_command_mock = MagicMock(spec=VersionCommand)
        version_command_mock.get_current_version.return_value = current_version
        version_command_mock.get_version_calculator.return_value = calculator
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.return_value = VersionUpdate(
            previous=current_version,
            new=next_patch_version,
            changed_files=["MyProject.conf"],
        )
        create_changelog_mock.return_value = "A changelog text"
        find_signing_key_mock.return_value = "0815"

        _, _, args = parse_args(
            ["prepare", "--project", "foo", "--release-type", "patch"]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(released, PrepareReturnValue.SUCCESS)

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            f"Automatic release to {next_patch_version}",
            verify=False,
            gpg_signing_key="0815",
        )
        git_mock.return_value.tag.assert_called_once_with(
            f"v{next_patch_version}",
            message=f"Automatic release to {next_patch_version}",
            gpg_key_id="0815",
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.find_signing_key", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.prepare.gather_project", autospec=True)
    def test_prepare_release_type_minor(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        find_signing_key_mock: MagicMock,
        git_mock: MagicMock,
    ):
        calculator = VersionCalculator()
        current_version = "21.6.0"
        next_version = "21.7.0"
        version_command_mock = MagicMock(spec=VersionCommand)
        version_command_mock.get_current_version.return_value = current_version
        version_command_mock.get_version_calculator.return_value = calculator
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.return_value = VersionUpdate(
            previous=current_version,
            new=next_version,
            changed_files=["MyProject.conf"],
        )
        create_changelog_mock.return_value = "A changelog text"
        find_signing_key_mock.return_value = "0815"

        _, _, args = parse_args(
            ["prepare", "--project", "foo", "--release-type", "minor"]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(released, PrepareReturnValue.SUCCESS)

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            f"Automatic release to {next_version}",
            verify=False,
            gpg_signing_key="0815",
        )
        git_mock.return_value.tag.assert_called_once_with(
            f"v{next_version}",
            message=f"Automatic release to {next_version}",
            gpg_key_id="0815",
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.find_signing_key", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.prepare.gather_project", autospec=True)
    def test_prepare_release_type_major(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        find_signing_key_mock: MagicMock,
        git_mock: MagicMock,
    ):
        calculator = VersionCalculator()
        current_version = "21.6.0"
        next_version = "22.0.0"
        version_command_mock = MagicMock(spec=VersionCommand)
        version_command_mock.get_current_version.return_value = current_version
        version_command_mock.get_version_calculator.return_value = calculator
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.return_value = VersionUpdate(
            previous=current_version,
            new=next_version,
            changed_files=["MyProject.conf"],
        )
        create_changelog_mock.return_value = "A changelog text"
        find_signing_key_mock.return_value = "0815"

        _, _, args = parse_args(
            ["prepare", "--project", "foo", "--release-type", "major"]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(released, PrepareReturnValue.SUCCESS)

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            f"Automatic release to {next_version}",
            verify=False,
            gpg_signing_key="0815",
        )
        git_mock.return_value.tag.assert_called_once_with(
            f"v{next_version}",
            message=f"Automatic release to {next_version}",
            gpg_key_id="0815",
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.prepare.gather_project", autospec=True)
    def test_use_git_signing_key_on_prepare(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        git_mock: MagicMock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.return_value = VersionUpdate(
            previous="0.0.0", new="0.0.1", changed_files=["MyProject.conf"]
        )
        create_changelog_mock.return_value = "A changelog text"

        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--git-signing-key",
                "0815",
                "--release-version",
                "0.0.1",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )

        self.assertEqual(released, PrepareReturnValue.SUCCESS)

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="0815", message="Automatic release to 0.0.1"
        )
        git_mock.return_value.commit.assert_called_once_with(
            "Automatic release to 0.0.1", verify=False, gpg_signing_key="0815"
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    def test_no_release_when_no_project_found(
        self,
        _git_mock: MagicMock,
    ):
        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(
            released, PrepareReturnValue.PROJECT_SETTINGS_NOT_FOUND
        )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.gather_project", autospec=True)
    def test_no_release_version_error(
        self,
        gather_project_mock: MagicMock,
        _git_mock: MagicMock,
    ):
        version_calculator_mock = MagicMock(spec=VersionCalculator)
        version_calculator_mock.next_patch_version.side_effect = VersionError(
            "An error"
        )
        version_command_mock = MagicMock(spec=VersionCommand)
        version_command_mock.get_version_calculator.return_value = (
            version_calculator_mock
        )
        gather_project_mock.return_value = version_command_mock

        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--release-type",
                "patch",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )

        self.assertEqual(released, PrepareReturnValue.NO_RELEASE_VERSION)

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.gather_project", autospec=True)
    def test_no_release_version(
        self,
        gather_project_mock: MagicMock,
        _git_mock: MagicMock,
    ):
        version_calculator_mock = MagicMock(spec=VersionCalculator)
        version_calculator_mock.next_patch_version.return_value = None
        version_command_mock = MagicMock(spec=VersionCommand)
        version_command_mock.get_version_calculator.return_value = (
            version_calculator_mock
        )
        gather_project_mock.return_value = version_command_mock

        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--release-type",
                "patch",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )

        self.assertEqual(released, PrepareReturnValue.NO_RELEASE_VERSION)

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.gather_project", autospec=True)
    def test_fail_if_tag_is_already_taken(
        self,
        gather_project_mock: MagicMock,
        git_mock: MagicMock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        git_mock.return_value.list_tags.return_value = ["v0.0.1"]

        _, _, args = parse_args(
            [
                "prepare",
                "--release-version",
                "0.0.1",
                "--project",
                "bla",
                "--git-signing-key",
                "1337",
            ]
        )

        with temp_git_repository():
            release = prepare(
                terminal=mock_terminal(),
                args=args,
            )

            self.assertEqual(release, PrepareReturnValue.ALREADY_TAKEN)

        git_mock.return_value.list_tags.assert_called_once()

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.gather_project", autospec=True)
    def test_updating_version_error(
        self,
        gather_project_mock: MagicMock,
        _git_mock: MagicMock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.side_effect = VersionError(
            "Error updating the version"
        )

        _, _, args = parse_args(
            [
                "prepare",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
            ]
        )
        with temp_git_repository():
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )
        self.assertEqual(released, PrepareReturnValue.UPDATE_VERSION_ERROR)

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch("pontos.release.prepare.ChangelogBuilder", autospec=True)
    @patch("pontos.release.prepare.gather_project", autospec=True)
    @patch("pontos.release.prepare.get_last_release_version", autospec=True)
    def test_prepare_conventional_commits(
        self,
        get_last_release_verson_mock: MagicMock,
        gather_project_mock: MagicMock,
        changelog_builder_mock: MagicMock,
        git_mock: MagicMock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.return_value = VersionUpdate(
            previous="0.0.1", new="1.2.3", changed_files=["MyProject.conf"]
        )
        get_last_release_verson_mock.return_value = "0.0.1"
        content = """## [1.2.3] - 2021-08-23

## Added

* Need for commits. [1234567](https://github.com/foo/bar/commit/1234567)

## Changed

* fooooo. [1234568](https://github.com/foo/bar/commit/1234568)

[1.2.3]: https://github.com/y0urself/test_workflows/compare/0.0.1...1.2.3"""

        with temp_git_repository() as temp_dir:
            release_file = temp_dir / ".release.md"
            changelog_dir = temp_dir / "changelog"
            changelog_dir.mkdir(parents=True)
            changelog_file = changelog_dir / "v1.2.3.md"
            changelog_file.write_text(content, encoding="utf8")

            _, _, args = parse_args(
                [
                    "prepare",
                    "--project",
                    "foo",
                    "--release-version",
                    "1.2.3",
                ]
            )
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )

            self.assertEqual(released, PrepareReturnValue.SUCCESS)

            git_mock.return_value.add.assert_has_calls(
                [call("MyProject.conf"), call(Path("changelog/v1.2.3.md"))]
            )

            changelog_builder_mock.return_value.create_changelog_file.assert_called_once_with(
                Path("changelog/v1.2.3.md"),
                last_version="0.0.1",
                next_version="1.2.3",
            )

            expected_release_content = """## [1.2.3] - 2021-08-23

## Added

* Need for commits. [1234567](https://github.com/foo/bar/commit/1234567)

## Changed

* fooooo. [1234568](https://github.com/foo/bar/commit/1234568)

[1.2.3]: https://github.com/y0urself/test_workflows/compare/0.0.1...1.2.3"""

            self.assertEqual(
                release_file.read_text(encoding="utf-8"),
                expected_release_content,
            )

    @patch("pontos.release.prepare.Git", autospec=True)
    @patch(
        "pontos.release.prepare.PrepareCommand._create_changelog",
        autospec=True,
    )
    def test_prepare(
        self,
        create_changelog_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = "21.6.0"
        next_patch_version = "21.6.1"
        gpg_key_id = "0815"
        create_changelog_mock.return_value = "A changelog text"

        _, _, args = parse_args(["prepare", "--release-type", "patch"])
        with temp_git_repository() as temp_dir:
            git = Git()
            git.config("user.signingkey", gpg_key_id, scope=ConfigScope.LOCAL)
            git.add_remote("origin", "http://foo/bar.git")

            go_mod = temp_dir / GoVersionCommand.project_file_name
            go_mod.touch()
            version_file = temp_dir / GoVersionCommand.version_file_path
            version_file.write_text(
                f'var version = "{current_version}"', encoding="utf8"
            )
            released = prepare(
                terminal=mock_terminal(),
                args=args,
            )

            self.assertEqual(released, PrepareReturnValue.SUCCESS)

            git_mock.return_value.add.assert_called_with(
                GoVersionCommand.version_file_path
            )
            git_mock.return_value.commit.assert_called_with(
                f"Automatic release to {next_patch_version}",
                verify=False,
                gpg_signing_key=gpg_key_id,
            )

            self.assertTrue(
                next_patch_version in version_file.read_text(encoding="utf8")
            )
