# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=too-many-lines, line-too-long, invalid-name

import unittest
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, Optional, Union
from unittest.mock import AsyncMock, MagicMock, call, patch

from httpx import HTTPStatusError, Request, Response

from pontos.git import ConfigScope, Git, ResetMode, StatusEntry
from pontos.github.actions.errors import GitHubActionsError
from pontos.release.create import (
    CreateReleaseReturnValue,
    ReleaseInformation,
    create_release,
)
from pontos.release.main import parse_args
from pontos.terminal.terminal import Terminal
from pontos.testing import temp_directory, temp_git_repository
from pontos.version import VersionError, VersionUpdate
from pontos.version.commands import GoVersionCommand
from pontos.version.schemes._pep440 import PEP440Version, PEP440VersioningScheme


def mock_terminal() -> MagicMock:
    return MagicMock(spec=Terminal)


def str_or_list(values: Union[str, Iterable[str]]) -> Iterable[str]:
    if values and isinstance(values, str):
        return [values]
    return values


@contextmanager
def setup_go_project(
    *, current_version: str, tags: Union[str, Iterable[str], None] = None
) -> Iterator[Path]:
    with temp_git_repository() as tmp_git:
        git = Git(tmp_git)

        git.config("commit.gpgSign", "false", scope=ConfigScope.LOCAL)
        git.config("tag.gpgSign", "false", scope=ConfigScope.LOCAL)
        git.config("tag.sort", "refname", scope=ConfigScope.LOCAL)

        git.add_remote("origin", "http://foo/bar.git")

        go = GoVersionCommand(PEP440VersioningScheme)
        go.project_file_path.touch()
        update = go.update_version(new_version=PEP440Version(current_version))

        git.add(update.changed_files)
        git.add(go.project_file_path)
        git.commit("Create initial release")

        if tags:
            for tag in str_or_list(tags):
                git.tag(f"v{tag}")

        yield tmp_git


class ReleaseInformationTestCase(unittest.TestCase):
    def test_release_info(self):
        release_info = ReleaseInformation(
            last_release_version=PEP440Version.from_string("1.2.3"),
            release_version=PEP440Version.from_string("2.0.0"),
            git_release_tag="v2.0.0",
            next_version=PEP440Version.from_string("2.0.1.dev1"),
        )

        self.assertEqual(
            release_info.last_release_version,
            PEP440Version.from_string("1.2.3"),
        )
        self.assertEqual(
            release_info.release_version, PEP440Version.from_string("2.0.0")
        )
        self.assertEqual(release_info.git_release_tag, "v2.0.0")
        self.assertEqual(
            release_info.next_version, PEP440Version.from_string("2.0.1.dev1")
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_no_github_output(self):
        release_info = ReleaseInformation(
            last_release_version=PEP440Version.from_string("1.2.3"),
            release_version=PEP440Version.from_string("2.0.0"),
            git_release_tag="v2.0.0",
            next_version=PEP440Version.from_string("2.0.1.dev1"),
        )

        with self.assertRaisesRegex(
            GitHubActionsError,
            "GITHUB_OUTPUT environment variable not set. Can't write "
            "action output.",
        ):
            release_info.write_github_output()

    def test_github_output(self):
        expected = """last-release-version=1.2.3
release-version=2.0.0
git-release-tag=v2.0.0
next-version=2.0.1.dev1
"""
        with temp_directory() as temp_dir:
            out_file = temp_dir / "out.txt"
            with patch.dict(
                "os.environ", {"GITHUB_OUTPUT": str(out_file.absolute())}
            ):
                release_info = ReleaseInformation(
                    last_release_version=PEP440Version.from_string("1.2.3"),
                    release_version=PEP440Version.from_string("2.0.0"),
                    git_release_tag="v2.0.0",
                    next_version=PEP440Version.from_string("2.0.1.dev1"),
                )

                release_info.write_github_output()

            self.assertTrue(out_file.exists())
            actual = out_file.read_text(encoding="utf8")
            self.assertEqual(actual, expected)


@patch.dict(
    "os.environ",
    {
        "GITHUB_TOKEN": "foo",
        "GITHUB_USER": "user",
        "GPG_SIGNING_KEY": "1234",
    },
)
class CreateReleaseTestCase(unittest.TestCase):
    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_version(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.0.2")
        next_version = PEP440Version("1.0.0.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-version",
                "0.0.2",
                "--next-version",
                "1.0.0.dev1",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ]
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.0.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="1234", message="Automatic release to 0.0.2"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_with_repository(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.0.2")
        next_version = PEP440Version("1.0.0.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "foo/bar",
                "--release-version",
                "0.0.2",
                "--next-version",
                "1.0.0.dev1",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ]
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.0.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="1234", message="Automatic release to 0.0.2"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_initial_release_version(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("1.0.0")
        next_version = PEP440Version("1.0.1.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = None
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-version",
                "1.0.0",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ]
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 1.0.0",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.1.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v1.0.0", gpg_key_id="1234", message="Automatic release to 1.0.0"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_patch(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.0.2")
        next_version = PEP440Version("1.0.0.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "patch",
                "--next-version",
                "1.0.0.dev1",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        get_last_release_version_mock.assert_called_once_with(
            parse_version=PEP440VersioningScheme.parse_version,
            git_tag_prefix="v",
            tag_name=None,
            ignore_pre_releases=True,
        )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.0.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="1234", message="Automatic release to 0.0.2"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_calendar(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        today = datetime.today()
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version(f"{today.year % 100}.{today.month}.0")
        next_version = PEP440Version(f"{today.year % 100}.{today.month}.1.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "calendar",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        get_last_release_version_mock.assert_called_once_with(
            parse_version=PEP440VersioningScheme.parse_version,
            git_tag_prefix="v",
            tag_name=None,
            ignore_pre_releases=True,
        )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ]
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    f"Automatic release to {release_version}",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    f"* Update to version {next_version}\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            f"v{release_version}",
            gpg_key_id="1234",
            message=f"Automatic release to {release_version}",
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_minor(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.1.0")
        next_version = PEP440Version("0.1.1.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "minor",
                "--next-version",
                "0.1.1.dev1",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        get_last_release_version_mock.assert_called_once_with(
            parse_version=PEP440VersioningScheme.parse_version,
            git_tag_prefix="v",
            tag_name=None,
            ignore_pre_releases=True,
        )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.1.0",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 0.1.1.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.1.0", gpg_key_id="1234", message="Automatic release to 0.1.0"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_major(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("1.0.0")
        next_version = PEP440Version("1.0.1.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "major",
                "--next-version",
                "1.0.1.dev1",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        get_last_release_version_mock.assert_called_once_with(
            parse_version=PEP440VersioningScheme.parse_version,
            git_tag_prefix="v",
            tag_name=None,
            ignore_pre_releases=True,
        )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 1.0.0",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.1.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v1.0.0", gpg_key_id="1234", message="Automatic release to 1.0.0"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_alpha(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.0.2a1")
        next_version = PEP440Version("0.0.2a2.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "alpha",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        get_last_release_version_mock.assert_called_once_with(
            parse_version=PEP440VersioningScheme.parse_version,
            git_tag_prefix="v",
            tag_name=None,
            ignore_pre_releases=False,
        )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2a1",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 0.0.2a2.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2a1",
            gpg_key_id="1234",
            message="Automatic release to 0.0.2a1",
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_beta(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.0.2b1")
        next_version = PEP440Version("0.0.2b2.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "beta",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        get_last_release_version_mock.assert_called_once_with(
            parse_version=PEP440VersioningScheme.parse_version,
            git_tag_prefix="v",
            tag_name=None,
            ignore_pre_releases=False,
        )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2b1",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 0.0.2b2.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2b1",
            gpg_key_id="1234",
            message="Automatic release to 0.0.2b1",
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_release_candidate(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.0.2rc1")
        next_version = PEP440Version("0.0.2rc2.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "release-candidate",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        get_last_release_version_mock.assert_called_once_with(
            parse_version=PEP440VersioningScheme.parse_version,
            git_tag_prefix="v",
            tag_name=None,
            ignore_pre_releases=False,
        )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2rc1",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 0.0.2rc2.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2rc1",
            gpg_key_id="1234",
            message="Automatic release to 0.0.2rc1",
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    def test_no_token(
        self,
    ):
        _, _, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-version",
                "0.0.1",
            ]
        )

        released = create_release(
            terminal=mock_terminal(),
            error_terminal=mock_terminal(),
            args=args,
            token=None,
        )

        self.assertEqual(released, CreateReleaseReturnValue.TOKEN_MISSING)

    def test_invalid_repository(
        self,
    ):
        _, _, args = parse_args(
            [
                "release",
                "--repository",
                "foo/bar",
                "--release-version",
                "0.0.1",
            ]
        )

        setattr(args, "repository", "foo/bar/baz")

        released = create_release(
            terminal=mock_terminal(),
            error_terminal=mock_terminal(),
            args=args,
            token="token",
        )

        self.assertEqual(released, CreateReleaseReturnValue.INVALID_REPOSITORY)

        _, _, args = parse_args(
            [
                "release",
                "--repository",
                "foo/bar",
                "--release-version",
                "0.0.1",
            ]
        )

        setattr(args, "repository", "foo_bar_baz")

        released = create_release(
            terminal=mock_terminal(),
            error_terminal=mock_terminal(),
            args=args,
            token="token",
        )

        self.assertEqual(released, CreateReleaseReturnValue.INVALID_REPOSITORY)

    @patch("pontos.release.create.get_last_release_version", autospec=True)
    def test_no_project_settings(
        self,
        get_last_release_version_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        get_last_release_version_mock.return_value = current_version

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-version",
                "0.0.1",
            ]
        )
        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        self.assertEqual(
            released, CreateReleaseReturnValue.PROJECT_SETTINGS_NOT_FOUND
        )

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project", autospec=True)
    def test_no_update_project(
        self,
        project_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.0.2")
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = []

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-version",
                "0.0.2",
                "--next-version",
                "1.0.0.dev1",
                "--no-update-project",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_not_called()
        git_instance_mock.commit.assert_not_called()
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="1234", message="Automatic release to 0.0.2"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

        project_mock.assert_not_called()

    def test_last_release_version_error(self):
        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "major",
            ]
        )
        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,
            )

        self.assertEqual(
            released, CreateReleaseReturnValue.NO_LAST_RELEASE_VERSION
        )

    @patch("pontos.release.create.get_last_release_version", autospec=True)
    def test_no_last_release_version(
        self,
        get_last_release_version_mock: MagicMock,
    ):
        get_last_release_version_mock.return_value = None
        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "minor",
            ]
        )
        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        self.assertEqual(
            released, CreateReleaseReturnValue.NO_LAST_RELEASE_VERSION
        )

    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.get_next_release_version",
        autospec=True,
    )
    def test_no_release_error(
        self,
        get_next_release_version_mock: MagicMock,
        get_last_release_version_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        get_next_release_version_mock.side_effect = VersionError("An error")
        get_last_release_version_mock.return_value = current_version

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--git-signing-key",
                "123",
                "--release-type",
                "patch",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        self.assertEqual(released, CreateReleaseReturnValue.NO_RELEASE_VERSION)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.version.helper.Git", autospec=True)
    def test_has_tag(
        self,
        git_mock1: MagicMock,
        git_mock2: MagicMock,
    ):
        tags = ["v1.0.0", "v1.0.1"]
        git_mock1.return_value.list_tags.return_value = tags
        git_mock2.return_value.list_tags.return_value = tags

        _, token, args = parse_args(
            [
                "release",
                "--release-version",
                "1.0.1",
                "--repository",
                "greenbone/bla",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                token=token,  # type: ignore[arg-type]
                args=args,
            )

            self.assertEqual(released, CreateReleaseReturnValue.ALREADY_TAKEN)

        git_mock1.return_value.list_tags.assert_called_once()
        git_mock2.return_value.list_tags.assert_called_once()

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_update_version_error(
        self,
        gather_commands_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        command_mock.update_version.side_effect = VersionError("An error")
        current_version = PEP440Version("0.0.1rc1")
        get_last_release_version_mock.return_value = current_version

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_mock.return_value.push.assert_not_called()

        command_mock.update_version.assert_called_once_with(
            PEP440Version("0.0.1"), force=False
        )

        create_release_mock.assert_not_awaited()

        git_mock.return_value.add.assert_not_called()
        git_mock.return_value.commit.assert_not_called()
        git_mock.return_value.tag.assert_not_called()

        self.assertEqual(
            released, CreateReleaseReturnValue.UPDATE_VERSION_ERROR
        )

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_github_create_release_failure(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.0")
        release_version = PEP440Version("0.0.1")
        next_version = PEP440Version("0.0.2.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"
        create_release_mock.side_effect = HTTPStatusError(
            "Error during a request",
            request=MagicMock(spec=Request),
            response=MagicMock(spec=Response),
        )
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        self.assertEqual(
            released, CreateReleaseReturnValue.CREATE_RELEASE_ERROR
        )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call("v0.0.1", delete=True, remote=None),
                call(force=True, remote=None),
            ]
        )
        git_instance_mock.reset.assert_called_once_with(
            "HEAD^", mode=ResetMode.HARD
        )
        git_instance_mock.delete_tag.assert_called_once_with("v0.0.1")
        git_instance_mock.add.assert_called_once_with(Path("MyProject.conf"))
        git_instance_mock.commit.assert_called_once_with(
            "Automatic release to 0.0.1", verify=False, gpg_signing_key="1234"
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="1234", message="Automatic release to 0.0.1"
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_update_version_after_release_error(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.0")
        release_version = PEP440Version("0.0.1")
        next_version = PEP440Version("0.0.2.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionError("An error"),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_called_once_with(
            follow_tags=True, remote=None
        )

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ]
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_called_once_with(Path("MyProject.conf"))
        git_instance_mock.commit.assert_called_once_with(
            "Automatic release to 0.0.1", verify=False, gpg_signing_key="1234"
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="1234", message="Automatic release to 0.0.1"
        )

        self.assertEqual(
            released,
            CreateReleaseReturnValue.UPDATE_VERSION_AFTER_RELEASE_ERROR,
        )

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_to_specific_git_remote(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock,
    ):
        current_version = PEP440Version("0.0.0")
        release_version = PEP440Version("0.0.1")
        next_version = PEP440Version("0.0.2.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
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
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote="upstream"),
                call(follow_tags=True, remote="upstream"),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        git_instance_mock.add.assert_called_with(Path("MyProject.conf"))
        git_instance_mock.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="1234", message="Automatic release to 0.0.1"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_without_git_prefix(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock,
    ):
        current_version = PEP440Version("0.0.0")
        release_version = PEP440Version("0.0.1")
        next_version = PEP440Version("0.0.2.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
                "--git-tag-prefix",
                "",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        git_instance_mock.add.assert_called_with(Path("MyProject.conf"))
        git_instance_mock.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_instance_mock.tag.assert_called_once_with(
            "0.0.1", gpg_key_id="1234", message="Automatic release to 0.0.1"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch("pontos.release.create.GitHubAsyncRESTApi", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_github_api(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        github_api_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock,
    ):
        current_version = PEP440Version("0.0.0")
        release_version = PEP440Version("0.0.1")
        next_version = PEP440Version("0.0.2.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"
        create_api_mock = AsyncMock()
        github_api_mock.return_value.releases.create = create_api_mock
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "bar/foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
                "--git-remote-name",
                "upstream",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_has_calls(
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

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        git_instance_mock.add.assert_called_with(Path("MyProject.conf"))
        git_instance_mock.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="1234", message="Automatic release to 0.0.1"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch("pontos.release.create.GitHubAsyncRESTApi", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_github_api_pre_release(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        github_api_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock,
    ):
        current_version = PEP440Version("0.0.0")
        release_version = PEP440Version("0.0.1a1")
        next_version = PEP440Version("0.0.1a1+dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"
        create_api_mock = AsyncMock()
        github_api_mock.return_value.releases.create = create_api_mock
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "bar/foo",
                "--release-version",
                "0.0.1a1",
                "--next-version",
                "0.0.1a1+dev1",
                "--git-remote-name",
                "upstream",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_has_calls(
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

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        git_instance_mock.add.assert_called_with(Path("MyProject.conf"))
        git_instance_mock.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.1a1+dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.1a1",
            gpg_key_id="1234",
            message="Automatic release to 0.0.1a1",
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    def test_release_with_go_project(
        self,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        git_mock,
    ):
        release_version = PEP440Version("0.0.2")

        create_changelog_mock.return_value = "A Changelog"

        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry(f"M  {GoVersionCommand.version_file_path}")
        ]

        _, token, args = parse_args(
            ["release", "--repository", "foo/bar", "--release-type", "patch"]
        )

        with setup_go_project(current_version="0.0.1", tags=["0.0.1"]):
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

        git_instance_mock.push.assert_called_with(follow_tags=True, remote=None)
        git_instance_mock.add.assert_called_with(
            GoVersionCommand.version_file_path
        )
        git_instance_mock.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.3.dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="1234", message="Automatic release to 0.0.2"
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch("pontos.changelog.conventional_commits.Git", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_with_changelog(
        self,
        gather_commands_mock: MagicMock,
        create_release_mock: AsyncMock,
        cc_git_mock: MagicMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.0.2")
        next_version = PEP440Version("1.0.0.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("project.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("project.conf"), Path("version.lang")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [StatusEntry("M  project.conf")]
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
                "--repository",
                "greenbone/foo",
                "--release-version",
                "0.0.2",
                "--next-version",
                "1.0.0.dev1",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.list_tags.assert_called_once_with()

        cc_git_mock.return_value.log.assert_called_once_with(
            "v0.0.1..HEAD", oneline=True
        )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ]
        )

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ]
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", expected_changelog, False),
        )

        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="1234", message="Automatic release to 0.0.2"
        )
        git_instance_mock.add.assert_has_calls(
            [
                call(Path("project.conf")),
                call(Path("project.conf")),
                call(Path("version.lang")),
            ]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.0.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_local(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock,
    ):
        current_version = PEP440Version("0.0.0")
        release_version = PEP440Version("0.0.1")
        next_version = PEP440Version("0.0.2.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        create_changelog_mock.return_value = "A Changelog"
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-version",
                "0.0.1",
                "--next-version",
                "0.0.2.dev1",
                "--local",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_not_called()

        create_release_mock.assert_not_awaited()

        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ]
        )

        git_instance_mock.add.assert_called_with(Path("MyProject.conf"))
        git_instance_mock.commit.assert_called_with(
            "Automatic adjustments after release\n\n"
            "* Update to version 0.0.2.dev1\n",
            verify=False,
            gpg_signing_key="1234",
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.1", gpg_key_id="1234", message="Automatic release to 0.0.1"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_enforce_github_release(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.0.2")
        next_version = PEP440Version("1.0.0.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "patch",
                "--next-version",
                "1.0.0.dev1",
                "--github-pre-release",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
                call(follow_tags=True, remote=None),
            ],
        )
        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
                call(next_version, force=False),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", True),
        )

        git_instance_mock.add.assert_has_calls(
            [call(Path("MyProject.conf")), call(Path("MyProject.conf"))]
        )
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2",
                    verify=False,
                    gpg_signing_key="1234",
                ),
                call(
                    "Automatic adjustments after release\n\n"
                    "* Update to version 1.0.0.dev1\n",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="1234", message="Automatic release to 0.0.2"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)

    @patch("pontos.release.create.Git", autospec=True)
    @patch("pontos.release.create.get_last_release_version", autospec=True)
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_release",
        autospec=True,
    )
    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Project._gather_commands", autospec=True)
    def test_release_no_next_release(
        self,
        gather_commands_mock: MagicMock,
        create_changelog_mock: MagicMock,
        create_release_mock: AsyncMock,
        get_last_release_version_mock: MagicMock,
        git_mock: MagicMock,
    ):
        current_version = PEP440Version("0.0.1")
        release_version = PEP440Version("0.0.2")
        next_version = PEP440Version("1.0.0.dev1")
        command_mock = MagicMock(spec=GoVersionCommand)
        gather_commands_mock.return_value = [command_mock]
        create_changelog_mock.return_value = "A Changelog"
        get_last_release_version_mock.return_value = current_version
        command_mock.update_version.side_effect = [
            VersionUpdate(
                previous=current_version,
                new=release_version,
                changed_files=[Path("MyProject.conf")],
            ),
            VersionUpdate(
                previous=release_version,
                new=next_version,
                changed_files=[Path("MyProject.conf")],
            ),
        ]
        git_instance_mock: MagicMock = git_mock.return_value
        git_instance_mock.status.return_value = [
            StatusEntry("M  MyProject.conf")
        ]

        _, token, args = parse_args(
            [
                "release",
                "--repository",
                "greenbone/foo",
                "--release-type",
                "patch",
                "--no-next-version",
            ]
        )

        with temp_git_repository():
            released = create_release(
                terminal=mock_terminal(),
                error_terminal=mock_terminal(),
                args=args,
                token=token,  # type: ignore[arg-type]
            )

        git_instance_mock.push.assert_has_calls(
            [
                call(follow_tags=True, remote=None),
            ],
        )
        command_mock.update_version.assert_has_calls(
            [
                call(release_version, force=False),
            ],
        )

        self.assertEqual(
            create_release_mock.await_args.args[1:],  # type: ignore[union-attr]
            (release_version, "foo", "A Changelog", False),
        )

        git_instance_mock.add.assert_has_calls([call(Path("MyProject.conf"))])
        git_instance_mock.commit.assert_has_calls(
            [
                call(
                    "Automatic release to 0.0.2",
                    verify=False,
                    gpg_signing_key="1234",
                ),
            ]
        )
        git_instance_mock.tag.assert_called_once_with(
            "v0.0.2", gpg_key_id="1234", message="Automatic release to 0.0.2"
        )

        self.assertEqual(released, CreateReleaseReturnValue.SUCCESS)


@dataclass
class Release:
    release_type: str
    current_version: str
    expected_release_version: str
    tags: Union[str, list[str]]
    expected_last_release_version: Optional[str] = None
    release_series: Optional[str] = None


@patch.dict(
    "os.environ",
    {"GITHUB_TOKEN": "foo", "GITHUB_USER": "user", "GPG_SIGNING_KEY": ""},
)
class ReleaseGoProjectTestCase(unittest.TestCase):
    @patch("pontos.release.create.Git.push", autospec=True)
    @patch(
        "pontos.release.create.GitHubAsyncRESTApi",
        autospec=True,
    )
    def test_release(
        self, github_api_mock: AsyncMock, _git_push_mock: MagicMock
    ):
        create_api_mock = AsyncMock()
        github_api_mock.return_value.releases.create = create_api_mock

        releases = [
            Release(
                release_type="major",
                current_version="1.0.0",
                expected_release_version="2.0.0",
                tags="1.0.0",
            ),
            Release(
                release_type="minor",
                current_version="1.0.0",
                expected_release_version="1.1.0",
                tags="1.0.0",
            ),
            Release(
                release_type="patch",
                current_version="1.0.0",
                expected_release_version="1.0.1",
                tags="1.0.0",
            ),
            Release(
                release_type="patch",
                current_version="1.0.5",
                expected_release_version="1.0.6",
                tags="1.0.5",
            ),
            Release(
                release_type="alpha",
                current_version="1.0.0",
                expected_release_version="1.0.1a1",
                tags="1.0.0",
            ),
            Release(
                release_type="alpha",
                current_version="1.0.0a3",
                expected_release_version="1.0.0a4",
                tags="1.0.0a3",
            ),
            Release(
                release_type="beta",
                current_version="1.0.0",
                expected_release_version="1.0.1b1",
                tags="1.0.0",
            ),
            Release(
                release_type="beta",
                current_version="1.0.0b2",
                expected_release_version="1.0.0b3",
                tags="1.0.0b2",
            ),
            Release(
                release_type="release-candidate",
                current_version="1.0.0",
                expected_release_version="1.0.1rc1",
                tags="1.0.0",
            ),
            Release(
                release_type="release-candidate",
                current_version="1.0.0rc1",
                expected_release_version="1.0.0rc2",
                tags="1.0.0rc1",
            ),
        ]

        for r in releases:
            with setup_go_project(
                current_version=r.current_version, tags=r.tags
            ):
                _, token, args = parse_args(
                    [
                        "release",
                        "--repository",
                        "foo/bar",
                        "--release-type",
                        r.release_type,
                    ]
                )
                released = create_release(
                    terminal=mock_terminal(),
                    error_terminal=mock_terminal(),
                    args=args,
                    token=token,  # type: ignore[arg-type]
                )

            self.assertEqual(
                released,
                CreateReleaseReturnValue.SUCCESS,
                f"v{r.expected_release_version}",
            )
            self.assertEqual(
                create_api_mock.call_args.args[1],
                f"v{r.expected_release_version}",
            )

            create_api_mock.reset_mock()

    @patch(
        "pontos.release.create.CreateReleaseCommand._create_changelog",
        autospec=True,
    )
    @patch("pontos.release.create.Git.push", autospec=True)
    @patch(
        "pontos.release.create.GitHubAsyncRESTApi",
        autospec=True,
    )
    def test_release_series(
        self,
        github_api_mock: AsyncMock,
        _git_push_mock: MagicMock,
        create_changelog_mock: MagicMock,
    ):
        create_api_mock = AsyncMock()
        github_api_mock.return_value.releases.create = create_api_mock

        create_changelog_mock.return_value = "A Changelog"

        releases = [
            Release(
                release_type="major",
                current_version="1.0.0",
                expected_release_version="2.0.0",
                expected_last_release_version="1.0.0",
                tags=["1.0.0", "3.0.0"],
                release_series="1",
            ),
            Release(
                release_type="major",
                current_version="1.0.0rc1",
                expected_release_version="1.0.0",
                expected_last_release_version="0.9.0",
                tags=["0.9.0", "0.8.1", "0.5.0"],
            ),
            Release(
                release_type="minor",
                current_version="1.0.0",
                expected_release_version="2.1.0",
                expected_last_release_version="2.0.0",
                tags=["1.0.0", "2.0.0"],
            ),
            Release(
                release_type="minor",
                current_version="1.0.0",
                expected_release_version="1.1.0",
                expected_last_release_version="1.0.0",
                tags=["1.0.0", "2.0.0"],
                release_series="1",
            ),
            Release(
                release_type="minor",
                current_version="1.1.0",
                expected_release_version="1.2.0",
                expected_last_release_version="1.1.0",
                tags=["1.0.0", "1.1.0", "2.0.0"],
                release_series="1.1",
            ),
            Release(
                release_type="patch",
                current_version="1.0.0",
                expected_release_version="1.0.1",
                expected_last_release_version="1.0.0",
                tags=["1.0.0", "1.1.0", "2.0.0"],
                release_series="1.0",
            ),
            Release(
                release_type="patch",
                current_version="1.0.5",
                expected_release_version="1.0.6",
                expected_last_release_version="1.0.5",
                tags=["1.0.5", "1.1.0", "2.0.0"],
                release_series="1.0",
            ),
            Release(
                release_type="patch",
                current_version="1.0.5",
                expected_release_version="1.1.1",
                expected_last_release_version="1.1.0",
                tags=["1.0.5", "1.1.0", "2.0.0"],
                release_series="1.1",
            ),
            Release(
                release_type="patch",
                current_version="1.1.0rc1",
                expected_release_version="1.1.0",
                expected_last_release_version="1.1.0b1",
                tags=["1.0.0", "1.1.0b1", "1.2.0", "2.0.0"],
                release_series="1.1",
            ),
            Release(
                release_type="alpha",
                current_version="1.0.0",
                expected_release_version="1.0.1a1",
                expected_last_release_version="1.0.0",
                tags=["1.0.0", "2.0.0", "1.1.0"],
                release_series="1.0",
            ),
            Release(
                release_type="alpha",
                current_version="1.0.0a3",
                expected_release_version="1.0.0a4",
                expected_last_release_version="1.0.0a3",
                tags=["1.0.0a3", "2.0.0", "1.1.0"],
                release_series="1.0",
            ),
            Release(
                release_type="beta",
                current_version="1.0.0",
                expected_release_version="1.0.1b1",
                expected_last_release_version="1.0.0",
                tags=["1.0.0", "2.0.0", "1.1.0"],
                release_series="1.0",
            ),
            Release(
                release_type="beta",
                current_version="1.0.0b2",
                expected_release_version="1.0.0b3",
                expected_last_release_version="1.0.0b2",
                tags=["1.0.0b2", "2.0.0", "1.1.0"],
                release_series="1.0",
            ),
            Release(
                release_type="release-candidate",
                current_version="1.0.0",
                expected_release_version="1.0.1rc1",
                expected_last_release_version="1.0.0",
                tags=["1.0.0", "2.0.0", "1.1.0"],
                release_series="1.0",
            ),
            Release(
                release_type="release-candidate",
                current_version="1.0.0rc1",
                expected_release_version="1.0.0rc2",
                expected_last_release_version="1.0.0rc1",
                tags=["1.0.0rc1", "2.0.0", "1.1.0"],
                release_series="1.0",
            ),
        ]

        for r in releases:
            with setup_go_project(
                current_version=r.current_version, tags=r.tags
            ):
                input_args = [
                    "release",
                    "--repository",
                    "foo/bar",
                    "--release-type",
                    r.release_type,
                ]
                if r.release_series:
                    input_args.extend(["--release-series", r.release_series])

                _, token, args = parse_args(input_args)
                released = create_release(
                    terminal=mock_terminal(),
                    error_terminal=mock_terminal(),
                    args=args,
                    token=token,  # type: ignore[arg-type]
                )

            self.assertEqual(
                released,
                CreateReleaseReturnValue.SUCCESS,
                f"Invalid return value for {r}",
            )
            self.assertEqual(
                create_api_mock.call_args.args[1],
                f"v{r.expected_release_version}",
                f"Unexpected current release version {r}",
            )

            self.assertEqual(
                create_changelog_mock.call_args.args[1],
                PEP440Version.from_string(r.expected_release_version),
                f"Unexpected current release version {r}",
            )

            if r.expected_last_release_version is None:
                self.assertIsNone(create_changelog_mock.call_args.args[2])
            else:
                self.assertEqual(
                    create_changelog_mock.call_args.args[2],
                    PEP440Version.from_string(r.expected_last_release_version),
                    f"Unexpected last release version for {r}",
                )

            create_api_mock.reset_mock()
            create_changelog_mock.reset_mock()
