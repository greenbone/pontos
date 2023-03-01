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

# pylint: disable=too-many-lines

import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, call, patch

from httpx import HTTPStatusError, Request, Response

from pontos.git.git import ConfigScope, Git
from pontos.release.main import parse_args
from pontos.release.release import ReleaseReturnValue, release
from pontos.terminal.terminal import Terminal
from pontos.testing import temp_git_repository
from pontos.version.errors import VersionError
from pontos.version.go import GoVersionCommand
from pontos.version.version import (
    Version,
    VersionCalculator,
    VersionCommand,
    VersionUpdate,
)


def mock_terminal() -> MagicMock:
    return MagicMock(spec=Terminal)


@patch.dict("os.environ", {"GITHUB_TOKEN": "foo", "GITHUB_USER": "user"})
class ReleaseTestCase(unittest.TestCase):
    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_version(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.1")
        release_version = Version("0.0.2")
        next_version = Version("1.0.0.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        create_changelog_mock.return_value = "A Changelog"
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-version",
                "0.0.2",
                "--next-version",
                "1.0.0.dev1",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )

        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)]
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        git_mock.return_value.add.assert_has_calls(
            [call("MyProject.conf"), call("MyProject.conf")]
        )
        git_mock.return_value.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2",
                    verify=False,
                    gpg_signing_key="123",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.0.dev1\n",
                    verify=False,
                    gpg_signing_key="123",
                ),
            ]
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="123", message="Automatic release to 0.0.2"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_patch(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.1")
        release_version = Version("0.0.2")
        next_version = Version("1.0.0.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        create_changelog_mock.return_value = "A Changelog"
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        version_command_mock.get_current_version.return_value = current_version
        version_command_mock.get_version_calculator.return_value = (
            VersionCalculator()
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-type",
                "patch",
                "--next-version",
                "1.0.0.dev1",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        git_mock.return_value.add.assert_has_calls(
            [call("MyProject.conf"), call("MyProject.conf")]
        )
        git_mock.return_value.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2",
                    verify=False,
                    gpg_signing_key="123",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.0.dev1\n",
                    verify=False,
                    gpg_signing_key="123",
                ),
            ]
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="123", message="Automatic release to 0.0.2"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_calendar(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.1")
        release_version = Version("23.2.0")
        next_version = Version("23.2.1.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        create_changelog_mock.return_value = "A Changelog"
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        version_command_mock.get_current_version.return_value = current_version
        version_calculator = MagicMock(spec=VersionCalculator)
        version_calculator.next_calendar_version.return_value = release_version
        version_command_mock.get_version_calculator.return_value = (
            version_calculator
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-type",
                "calendar",
                "--next-version",
                "23.2.1.dev1",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        version_calculator.next_calendar_version.assert_called_once_with(
            current_version
        )
        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)]
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        git_mock.return_value.add.assert_has_calls(
            [call("MyProject.conf"), call("MyProject.conf")]
        )
        git_mock.return_value.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 23.2.0",
                    verify=False,
                    gpg_signing_key="123",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 23.2.1.dev1\n",
                    verify=False,
                    gpg_signing_key="123",
                ),
            ]
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v23.2.0", gpg_key_id="123", message="Automatic release to 23.2.0"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_minor(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.1")
        release_version = Version("0.1.0")
        next_version = Version("0.1.1.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        create_changelog_mock.return_value = "A Changelog"
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        version_command_mock.get_current_version.return_value = current_version
        version_command_mock.get_version_calculator.return_value = (
            VersionCalculator()
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-type",
                "minor",
                "--next-version",
                "0.1.1.dev1",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        git_mock.return_value.add.assert_has_calls(
            [call("MyProject.conf"), call("MyProject.conf")]
        )
        git_mock.return_value.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.1.0",
                    verify=False,
                    gpg_signing_key="123",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 0.1.1.dev1\n",
                    verify=False,
                    gpg_signing_key="123",
                ),
            ]
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.1.0", gpg_key_id="123", message="Automatic release to 0.1.0"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_major(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.1")
        release_version = Version("1.0.0")
        next_version = Version("1.0.1.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        create_changelog_mock.return_value = "A Changelog"
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        version_command_mock.get_current_version.return_value = current_version
        version_command_mock.get_version_calculator.return_value = (
            VersionCalculator()
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-type",
                "major",
                "--next-version",
                "1.0.1.dev1",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        git_mock.return_value.add.assert_has_calls(
            [call("MyProject.conf"), call("MyProject.conf")]
        )
        git_mock.return_value.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 1.0.0",
                    verify=False,
                    gpg_signing_key="123",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.1.dev1\n",
                    verify=False,
                    gpg_signing_key="123",
                ),
            ]
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v1.0.0", gpg_key_id="123", message="Automatic release to 1.0.0"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_alpha(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.1")
        release_version = Version("0.0.2a1")
        next_version = Version("0.0.2a1+dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        create_changelog_mock.return_value = "A Changelog"
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        version_command_mock.get_current_version.return_value = current_version
        version_command_mock.get_version_calculator.return_value = (
            VersionCalculator()
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-type",
                "alpha",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        git_mock.return_value.add.assert_has_calls(
            [call("MyProject.conf"), call("MyProject.conf")]
        )
        git_mock.return_value.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2a1",
                    verify=False,
                    gpg_signing_key="123",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 0.0.2a1+dev1\n",
                    verify=False,
                    gpg_signing_key="123",
                ),
            ]
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.2a1", gpg_key_id="123", message="Automatic release to 0.0.2a1"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_beta(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.1")
        release_version = Version("0.0.2b1")
        next_version = Version("0.0.2b1+dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        create_changelog_mock.return_value = "A Changelog"
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        version_command_mock.get_current_version.return_value = current_version
        version_command_mock.get_version_calculator.return_value = (
            VersionCalculator()
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-type",
                "beta",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        git_mock.return_value.add.assert_has_calls(
            [call("MyProject.conf"), call("MyProject.conf")]
        )
        git_mock.return_value.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2b1",
                    verify=False,
                    gpg_signing_key="123",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 0.0.2b1+dev1\n",
                    verify=False,
                    gpg_signing_key="123",
                ),
            ]
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.2b1", gpg_key_id="123", message="Automatic release to 0.0.2b1"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_release_candidate(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.1")
        release_version = Version("0.0.2rc1")
        next_version = Version("0.0.2rc1+dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        create_changelog_mock.return_value = "A Changelog"
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        version_command_mock.get_current_version.return_value = current_version
        version_command_mock.get_version_calculator.return_value = (
            VersionCalculator()
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-type",
                "release-candidate",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        git_mock.return_value.add.assert_has_calls(
            [call("MyProject.conf"), call("MyProject.conf")]
        )
        git_mock.return_value.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2rc1",
                    verify=False,
                    gpg_signing_key="123",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 0.0.2rc1+dev1\n",
                    verify=False,
                    gpg_signing_key="123",
                ),
            ]
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.2rc1",
            gpg_key_id="123",
            message="Automatic release to 0.0.2rc1",
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    def test_no_token(self):
        _, _, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
            ]
        )

        released = release(
            terminal=mock_terminal(),
            args=args,
            token=None,
        )

        self.assertEqual(released, ReleaseReturnValue.TOKEN_MISSING)

    def test_no_project_settings(self):
        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
                "--git-signing-key",
                "123",
            ]
        )
        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        self.assertEqual(
            released, ReleaseReturnValue.PROJECT_SETTINGS_NOT_FOUND
        )

    @patch("pontos.release.release.gather_project", autospec=True)
    def test_no_release_error(self, gather_project_mock: MagicMock):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.get_current_version.side_effect = VersionError(
            "An error"
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-type",
                "patch",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        self.assertEqual(released, ReleaseReturnValue.NO_RELEASE_VERSION)

    @patch("pontos.release.release.gather_project", autospec=True)
    def test_no_release(self, gather_project_mock: MagicMock):
        version_command_mock = MagicMock(spec=VersionCommand)
        version_calculator_mock = MagicMock(spec=VersionCalculator)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.get_current_version.return_value = None
        version_command_mock.get_version_calculator.return_value = (
            version_calculator_mock
        )
        version_calculator_mock.next_patch_version.return_value = None

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-type",
                "patch",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        self.assertEqual(released, ReleaseReturnValue.NO_RELEASE_VERSION)

    @patch("pontos.release.release.Git", autospec=True)
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_has_tag(
        self,
        gather_project_mock: MagicMock,
        git_mock: MagicMock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        git_mock.return_value.list_tags.return_value = ["v0.0.1"]

        _, token, args = parse_args(
            [
                "release",
                "--release-version",
                "0.0.1",
                "--project",
                "bla",
                "--git-signing-key",
                "1337",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                token=token,
                args=args,
            )

            self.assertEqual(released, ReleaseReturnValue.ALREADY_TAKEN)

        git_mock.return_value.list_tags.assert_called_once()

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_update_version_error(
        self,
        gather_project_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.side_effect = VersionError(
            "An error"
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_not_called()

        version_command_mock.update_version.assert_called_once_with(
            Version("0.0.1")
        )

        create_release_mock.assert_not_awaited()

        git_mock.return_value.add.assert_not_called()
        git_mock.return_value.commit.assert_not_called()
        git_mock.return_value.tag.assert_not_called()

        self.assertEqual(released, ReleaseReturnValue.UPDATE_VERSION_ERROR)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_github_create_release_failure(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.0")
        release_version = Version("0.0.1")
        next_version = Version("0.0.2.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"
        create_release_mock.side_effect = HTTPStatusError(
            "Error during a request",
            request=MagicMock(spec=Request),
            response=MagicMock(spec=Response),
        )

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
                "--git-signing-key",
                "123",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_called_once_with(
            follow_tags=True, remote=None
        )
        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            "Automatic release to 0.0.1", verify=False, gpg_signing_key="123"
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="123", message="Automatic release to 0.0.1"
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        self.assertEqual(released, ReleaseReturnValue.CREATE_RELEASE_ERROR)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_update_version_after_release_error(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.0")
        release_version = Version("0.0.1")
        next_version = Version("0.0.2.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        create_changelog_mock.return_value = "A Changelog"
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionError("An error"),
        ]

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_called_once_with(
            follow_tags=True, remote=None
        )

        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)]
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        git_mock.return_value.add.assert_called_once_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_once_with(
            "Automatic release to 0.0.1", verify=False, gpg_signing_key="123"
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="123", message="Automatic release to 0.0.1"
        )

        self.assertEqual(
            released, ReleaseReturnValue.UPDATE_VERSION_AFTER_RELEASE_ERROR
        )

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_to_specific_git_remote(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock,
    ):
        current_version = Version("0.0.0")
        release_version = Version("0.0.1")
        next_version = Version("0.0.2.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
                "--git-remote-name",
                "upstream",
                "--git-signing-key",
                "1234",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote="upstream"),
                call(follow_tags=True, remote="upstream"),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)],
        )

        git_mock.return_value.add.assert_called_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="1234", message="Automatic release to 0.0.1"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_without_git_prefix(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock,
    ):
        current_version = Version("0.0.0")
        release_version = Version("0.0.1")
        next_version = Version("0.0.2.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
                "--git-signing-key",
                "1234",
                "--git-tag-prefix",
                "",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)],
        )

        git_mock.return_value.add.assert_called_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_mock.return_value.tag.assert_called_once_with(
            "0.0.1", gpg_key_id="1234", message="Automatic release to 0.0.1"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch("pontos.release.release.GitHubAsyncRESTApi", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_github_api(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        github_api_mock: AsyncMock,
        git_mock,
    ):
        current_version = Version("0.0.0")
        release_version = Version("0.0.1")
        next_version = Version("0.0.2.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"
        create_api_mock = AsyncMock()
        github_api_mock.return_value.releases.create = create_api_mock

        _, token, args = parse_args(
            [
                "release",
                "--space",
                "bar",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
                "--git-remote-name",
                "upstream",
                "--git-signing-key",
                "1234",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote="upstream"),
                call(follow_tags=True, remote="upstream"),
            ],
        )

        create_api_mock.assert_awaited_once_with(
            "bar/foo",
            "v0.0.1",
            name="foo 0.0.1",
            body="A Changelog",
            prerelease=False,
        )

        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)],
        )

        git_mock.return_value.add.assert_called_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="1234", message="Automatic release to 0.0.1"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch("pontos.release.release.GitHubAsyncRESTApi", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_github_api_pre_release(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        github_api_mock: AsyncMock,
        git_mock,
    ):
        current_version = Version("0.0.0")
        release_version = Version("0.0.1a1")
        next_version = Version("0.0.1a1+dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"
        create_api_mock = AsyncMock()
        github_api_mock.return_value.releases.create = create_api_mock

        _, token, args = parse_args(
            [
                "release",
                "--space",
                "bar",
                "--project",
                "foo",
                "--release-version",
                "0.0.1a1",
                "--next-version",
                "0.0.1a1+dev1",
                "--git-remote-name",
                "upstream",
                "--git-signing-key",
                "1234",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote="upstream"),
                call(follow_tags=True, remote="upstream"),
            ],
        )

        create_api_mock.assert_awaited_once_with(
            "bar/foo",
            "v0.0.1a1",
            name="foo 0.0.1a1",
            body="A Changelog",
            prerelease=True,
        )

        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)],
        )

        git_mock.return_value.add.assert_called_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.1a1+dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.1a1",
            gpg_key_id="1234",
            message="Automatic release to 0.0.1a1",
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog",
        autospec=True,
    )
    def test_release_with_go_project(
        self,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock,
    ):
        release_version = Version("0.0.2")

        create_changelog_mock.return_value = "A Changelog"
        _, token, args = parse_args(["release", "--release-type", "patch"])

        with temp_git_repository() as temp_dir:
            git = Git()
            git.config("user.signingkey", "1234", scope=ConfigScope.LOCAL)
            git.add_remote("origin", "http://foo/bar.git")

            go_mod = temp_dir / GoVersionCommand.project_file_name
            go_mod.touch()
            version_file = temp_dir / GoVersionCommand.version_file_path
            version_file.write_text('var version = "0.0.1"', encoding="utf8")

            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

        git_mock.return_value.push.assert_called_with(
            follow_tags=True, remote=None
        )
        git_mock.return_value.add.assert_called_with(
            GoVersionCommand.version_file_path
        )
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.3.dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="1234", message="Automatic release to 0.0.2"
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", "A Changelog"),
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    @patch("pontos.release.release.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_with_changelog(
        self,
        gather_project_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        cc_git_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = Version("0.0.1")
        release_version = Version("0.0.2")
        next_version = Version("1.0.0.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["project.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["project.conf", "version.lang"],
            ),
        ]
        get_last_release_version_mock.return_value = current_version
        cc_git_mock.return_value.log.return_value = [
            "1234567 Add: foo bar",
            "8abcdef Add: bar baz",
            "8abcd3f Add bar baz",
            "8abcd3d Adding bar baz",
            "1337abc Change: bar to baz",
            "42a42a4 Remove: foo bar again",
            "fedcba8 Test: bar baz testing",
            "dead901 Refactor: bar baz ref",
            "fedcba8 Fix: bar baz fixing",
            "d0c4d0c Doc: bar baz documenting",
        ]
        today = datetime.today().strftime("%Y-%m-%d")
        expected_changelog = f"""## [0.0.2] - {today}

## Added
* foo bar [1234567](https://github.com/greenbone/foo/commit/1234567)
* bar baz [8abcdef](https://github.com/greenbone/foo/commit/8abcdef)

## Removed
* foo bar again [42a42a4](https://github.com/greenbone/foo/commit/42a42a4)

## Changed
* bar to baz [1337abc](https://github.com/greenbone/foo/commit/1337abc)

## Bug Fixes
* bar baz fixing [fedcba8](https://github.com/greenbone/foo/commit/fedcba8)

[0.0.2]: https://github.com/greenbone/foo/compare/v0.0.1...v0.0.2"""

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--git-signing-key",
                "123",
                "--release-version",
                "0.0.2",
                "--next-version",
                "1.0.0.dev1",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.list_tags.assert_called_once_with()

        cc_git_mock.return_value.log.assert_called_once_with(
            "v0.0.1..HEAD", oneline=True
        )

        git_mock.return_value.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ]
        )

        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)]
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],
            (release_version, "foo", expected_changelog),
        )

        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="123", message="Automatic release to 0.0.2"
        )
        git_mock.return_value.add.assert_has_calls(
            [call("project.conf"), call("project.conf"), call("version.lang")]
        )
        git_mock.return_value.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2",
                    verify=False,
                    gpg_signing_key="123",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.0.dev1\n",
                    verify=False,
                    gpg_signing_key="123",
                ),
            ]
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)

    @patch("pontos.release.release.Git", autospec=True)
    @patch(
        "pontos.release.release.ReleaseCommand._create_release", autospec=True
    )
    @patch(
        "pontos.release.release.ReleaseCommand._create_changelog", autospec=True
    )
    @patch("pontos.release.release.gather_project", autospec=True)
    def test_release_local(
        self,
        gather_project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock,
    ):
        current_version = Version("0.0.0")
        release_version = Version("0.0.1")
        next_version = Version("0.0.2.dev1")
        version_command_mock = MagicMock(spec=VersionCommand)
        gather_project_mock.return_value = version_command_mock
        version_command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=["MyProject.conf"],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=["MyProject.conf"],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"

        _, token, args = parse_args(
            [
                "release",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
                "--git-signing-key",
                "1234",
                "--local",
            ]
        )

        with temp_git_repository():
            released = release(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

        git_mock.return_value.push.assert_not_called()

        create_release_mock.assert_not_awaited()

        version_command_mock.update_version.assert_has_calls(
            [call(release_version), call(next_version)]
        )

        git_mock.return_value.add.assert_called_with("MyProject.conf")
        git_mock.return_value.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_mock.return_value.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="1234", message="Automatic release to 0.0.1"
        )

        self.assertEqual(released, ReleaseReturnValue.SUCCESS)
