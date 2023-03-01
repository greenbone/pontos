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
# pylint: disable=C0413,W0108

import unittest
from asyncio.subprocess import Process
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, call, patch

import httpx

from pontos.release.main import parse_args
from pontos.release.sign import SignReturnValue, sign
from pontos.terminal.rich import RichTerminal
from pontos.testing import AsyncIteratorMock, temp_directory


def mock_terminal() -> MagicMock:
    return MagicMock(spec=RichTerminal)


@patch.dict("os.environ", {"GITHUB_TOKEN": "foo"})
class SignTestCase(unittest.TestCase):
    @patch.dict("os.environ", {"GITHUB_TOKEN": ""})
    def test_no_token(self):
        _, token, args = parse_args(
            [
                "sign",
                "--project",
                "foo",
                "--release-version",
                "0.0.1",
            ]
        )

        result = sign(
            terminal=mock_terminal(),
            args=args,
            token=token,
        )

        self.assertEqual(result, SignReturnValue.TOKEN_MISSING)

    def test_no_project(self):
        with temp_directory(change_into=True):
            _, token, args = parse_args(
                [
                    "sign",
                ]
            )

            result = sign(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

            self.assertEqual(result, SignReturnValue.NO_PROJECT)

    def test_no_release_error(self):
        with temp_directory(change_into=True):
            _, token, args = parse_args(
                [
                    "sign",
                    "--project",
                    "foo",
                ]
            )

            result = sign(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

            self.assertEqual(result, SignReturnValue.NO_RELEASE_VERSION)

    @patch("pontos.release.sign.get_last_release_version", autospec=True)
    def test_no_release_version(self, get_last_release_version_mock: MagicMock):
        get_last_release_version_mock.return_value = None

        with temp_directory(change_into=True):
            _, token, args = parse_args(
                [
                    "sign",
                    "--project",
                    "foo",
                ]
            )

            result = sign(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

            self.assertEqual(result, SignReturnValue.NO_RELEASE_VERSION)

    @patch("pontos.release.sign.GitHubAsyncRESTApi.releases", autospec=True)
    def test_release_does_not_exist(self, github_mock: AsyncMock):
        github_mock.exists = AsyncMock(return_value=False)

        with temp_directory(change_into=True):
            _, token, args = parse_args(
                [
                    "sign",
                    "--project",
                    "foo",
                    "--release",
                    "1.2.3",
                ]
            )

            result = sign(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

            self.assertEqual(result, SignReturnValue.NO_RELEASE)

    @patch("pontos.release.sign.cmd_runner", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_asset", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_tar", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_zip", autospec=True)
    @patch("pontos.release.sign.GitHubAsyncRESTApi.releases", autospec=True)
    def test_sign_success(
        self,
        github_releases_mock: AsyncMock,
        download_zip_mock: AsyncMock,
        download_tar_mock: AsyncMock,
        download_asset_mock: AsyncMock,
        cmd_runner_mock: AsyncMock,
    ):
        tar_file = Path("file.tar")
        zip_file = Path("file.zip")
        some_asset = Path("file1")
        other_asset = Path("file2")
        download_tar_mock.return_value = tar_file
        download_zip_mock.return_value = zip_file
        download_asset_mock.side_effect = [some_asset, other_asset]
        github_releases_mock.exists = AsyncMock(return_value=True)
        github_releases_mock.download_release_assets.return_value = (
            AsyncIteratorMock(
                [
                    (
                        "foo",
                        MagicMock(),
                    ),
                    ("bar", MagicMock()),
                ]
            )
        )
        process = AsyncMock(spec=Process, returncode=0)
        process.communicate.return_value = ("", "")
        cmd_runner_mock.return_value = process

        with temp_directory(change_into=True):
            _, token, args = parse_args(
                [
                    "sign",
                    "--project",
                    "foo",
                    "--release-version",
                    "1.2.3",
                ]
            )

            result = sign(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

            self.assertEqual(result, SignReturnValue.SUCCESS)

            cmd_runner_mock.assert_has_calls(
                [
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        zip_file,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        tar_file,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        some_asset,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        other_asset,
                    ),
                ]
            )

            github_releases_mock.upload_release_assets.assert_called_once_with(
                "greenbone/foo",
                "v1.2.3",
                [
                    (Path("file.zip.asc"), "application/pgp-signature"),
                    (Path("file.tar.asc"), "application/pgp-signature"),
                    (Path("file1.asc"), "application/pgp-signature"),
                    (Path("file2.asc"), "application/pgp-signature"),
                ],
            )

    @patch("pontos.version.helper.Git", autospec=True)
    @patch("pontos.release.sign.cmd_runner", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_asset", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_tar", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_zip", autospec=True)
    @patch("pontos.release.sign.GitHubAsyncRESTApi.releases", autospec=True)
    def test_sign_success_determine_release_version(
        self,
        github_releases_mock: AsyncMock,
        download_zip_mock: AsyncMock,
        download_tar_mock: AsyncMock,
        download_asset_mock: AsyncMock,
        cmd_runner_mock: AsyncMock,
        git_mock: MagicMock,
    ):
        tar_file = Path("file.tar")
        zip_file = Path("file.zip")
        some_asset = Path("file1")
        other_asset = Path("file2")
        download_tar_mock.return_value = tar_file
        download_zip_mock.return_value = zip_file
        download_asset_mock.side_effect = [some_asset, other_asset]
        github_releases_mock.exists = AsyncMock(return_value=True)
        github_releases_mock.download_release_assets.return_value = (
            AsyncIteratorMock(
                [
                    (
                        "foo",
                        MagicMock(),
                    ),
                    ("bar", MagicMock()),
                ]
            )
        )
        process = AsyncMock(spec=Process, returncode=0)
        process.communicate.return_value = ("", "")
        cmd_runner_mock.return_value = process
        git_mock.return_value.list_tags.return_value = ["v1.0.0", "v1.2.3"]

        with temp_directory(change_into=True):
            _, token, args = parse_args(
                [
                    "sign",
                    "--project",
                    "foo",
                ]
            )

            result = sign(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

            self.assertEqual(result, SignReturnValue.SUCCESS)

            cmd_runner_mock.assert_has_calls(
                [
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        zip_file,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        tar_file,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        some_asset,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        other_asset,
                    ),
                ]
            )

            github_releases_mock.upload_release_assets.assert_called_once_with(
                "greenbone/foo",
                "v1.2.3",
                [
                    (Path("file.zip.asc"), "application/pgp-signature"),
                    (Path("file.tar.asc"), "application/pgp-signature"),
                    (Path("file1.asc"), "application/pgp-signature"),
                    (Path("file2.asc"), "application/pgp-signature"),
                ],
            )

    @patch("pontos.release.sign.cmd_runner", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_asset", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_tar", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_zip", autospec=True)
    @patch("pontos.release.sign.GitHubAsyncRESTApi.releases", autospec=True)
    def test_sign_success_dry_run(
        self,
        github_releases_mock: AsyncMock,
        download_zip_mock: AsyncMock,
        download_tar_mock: AsyncMock,
        download_asset_mock: AsyncMock,
        cmd_runner_mock: MagicMock,
    ):
        tar_file = Path("file.tar")
        zip_file = Path("file.zip")
        some_asset = Path("file1")
        other_asset = Path("file2")
        download_tar_mock.return_value = tar_file
        download_zip_mock.return_value = zip_file
        download_asset_mock.side_effect = [some_asset, other_asset]
        github_releases_mock.exists = AsyncMock(return_value=True)
        github_releases_mock.download_release_assets.return_value = (
            AsyncIteratorMock(
                [
                    (
                        "foo",
                        MagicMock(),
                    ),
                    ("bar", MagicMock()),
                ]
            )
        )
        process = AsyncMock(spec=Process, returncode=0)
        process.communicate.return_value = ("", "")
        cmd_runner_mock.return_value = process

        with temp_directory(change_into=True):
            _, token, args = parse_args(
                [
                    "sign",
                    "--project",
                    "foo",
                    "--release-version",
                    "1.2.3",
                    "--dry-run",
                ]
            )

            result = sign(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

            self.assertEqual(result, SignReturnValue.SUCCESS)

            cmd_runner_mock.assert_has_calls(
                [
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        zip_file,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        tar_file,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        some_asset,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        other_asset,
                    ),
                ]
            )

            github_releases_mock.upload_release_assets.assert_not_called()

    @patch("pontos.release.sign.cmd_runner", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_asset", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_tar", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_zip", autospec=True)
    @patch("pontos.release.sign.GitHubAsyncRESTApi.releases", autospec=True)
    def test_sign_signature_failure(
        self,
        github_releases_mock: AsyncMock,
        download_zip_mock: AsyncMock,
        download_tar_mock: AsyncMock,
        download_asset_mock: AsyncMock,
        cmd_runner_mock: MagicMock,
    ):
        tar_file = Path("file.tar")
        zip_file = Path("file.zip")
        some_asset = Path("file1")
        other_asset = Path("file2")
        download_tar_mock.return_value = tar_file
        download_zip_mock.return_value = zip_file
        download_asset_mock.side_effect = [some_asset, other_asset]
        github_releases_mock.exists = AsyncMock(return_value=True)
        github_releases_mock.download_release_assets.return_value = (
            AsyncIteratorMock(
                [
                    (
                        "foo",
                        MagicMock(),
                    ),
                    ("bar", MagicMock()),
                ]
            )
        )
        process = AsyncMock(spec=Process, returncode=2)
        process.communicate.return_value = ("", b"An Error")
        cmd_runner_mock.return_value = process

        with temp_directory(change_into=True):
            _, token, args = parse_args(
                [
                    "sign",
                    "--project",
                    "foo",
                    "--release-version",
                    "1.2.3",
                ]
            )

            result = sign(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

            self.assertEqual(
                result, SignReturnValue.SIGNATURE_GENERATION_FAILED
            )

            cmd_runner_mock.assert_has_calls(
                [
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        zip_file,
                    ),
                ]
            )

            github_releases_mock.upload_release_assets.assert_not_called()

    @patch("pontos.release.sign.cmd_runner", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_asset", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_tar", autospec=True)
    @patch("pontos.release.sign.SignCommand.download_zip", autospec=True)
    @patch("pontos.release.sign.GitHubAsyncRESTApi.releases", autospec=True)
    def test_sign_upload_failure(
        self,
        github_releases_mock: AsyncMock,
        download_zip_mock: AsyncMock,
        download_tar_mock: AsyncMock,
        download_asset_mock: AsyncMock,
        cmd_runner_mock: MagicMock,
    ):
        tar_file = Path("file.tar")
        zip_file = Path("file.zip")
        some_asset = Path("file1")
        other_asset = Path("file2")
        download_tar_mock.return_value = tar_file
        download_zip_mock.return_value = zip_file
        download_asset_mock.side_effect = [some_asset, other_asset]
        github_releases_mock.exists = AsyncMock(return_value=True)
        github_releases_mock.download_release_assets.return_value = (
            AsyncIteratorMock(
                [
                    (
                        "foo",
                        MagicMock(),
                    ),
                    ("bar", MagicMock()),
                ]
            )
        )
        github_releases_mock.upload_release_assets.side_effect = (
            httpx.HTTPStatusError(
                "An error",
                request=MagicMock(spec=httpx.Request),
                response=MagicMock(spec=httpx.Response),
            )
        )
        process = AsyncMock(spec=Process, returncode=0)
        process.communicate.return_value = ("", "")
        cmd_runner_mock.return_value = process

        with temp_directory(change_into=True):
            _, token, args = parse_args(
                [
                    "sign",
                    "--project",
                    "foo",
                    "--release-version",
                    "1.2.3",
                ]
            )

            result = sign(
                terminal=mock_terminal(),
                args=args,
                token=token,
            )

            self.assertEqual(result, SignReturnValue.UPLOAD_ASSET_ERROR)

            cmd_runner_mock.assert_has_calls(
                [
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        zip_file,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        tar_file,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        some_asset,
                    ),
                    call(
                        "gpg",
                        "--default-key",
                        "0ED1E580",
                        "--yes",
                        "--detach-sign",
                        "--armor",
                        other_asset,
                    ),
                ]
            )

            github_releases_mock.upload_release_assets.assert_called_once_with(
                "greenbone/foo",
                "v1.2.3",
                [
                    (Path("file.zip.asc"), "application/pgp-signature"),
                    (Path("file.tar.asc"), "application/pgp-signature"),
                    (Path("file1.asc"), "application/pgp-signature"),
                    (Path("file2.asc"), "application/pgp-signature"),
                ],
            )
