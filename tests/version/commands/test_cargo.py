import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import tomlkit

from pontos.testing import temp_directory, temp_file
from pontos.version import VersionError
from pontos.version.commands._cargo import CargoVersionCommand
from pontos.version.schemes import PEP440VersioningScheme

VERSION_EXAMPLE = """
[package]
name = "nasl-syntax"
version = "0.1.0"
edition = "2021"
license = "GPL-2.0-or-later"
"""
WORKSPACE_EXAMPLE = """
[workspace]
members = [
  "nasl-syntax",
  "nasl-interpreter",
  "nasl-cli",
  "storage",
  "redis-storage",
  "json-storage",
  "feed",
  "feed-verifier",
]
"""


class VerifyCargoUpdateCommandTestCase(unittest.TestCase):
    @contextmanager
    def __create_cargo_layout(self) -> Iterator[Path]:
        with temp_directory(change_into=True) as temporary_dir:
            workspace = temporary_dir / "Cargo.toml"
            workspace.write_text(WORKSPACE_EXAMPLE)
            members = tomlkit.parse(WORKSPACE_EXAMPLE)["workspace"]["members"]
            for cargo_workspace_member in members:
                npath = temporary_dir / f"{cargo_workspace_member}"
                npath.mkdir()
                pf = npath / "Cargo.toml"
                pf.write_text(
                    VERSION_EXAMPLE.replace(
                        "nasl-syntax", cargo_workspace_member
                    )
                )
            yield temporary_dir
        return None

    def test_update(self):
        def expected_changed_files(temporary_dir_with_cargo_toml):
            members = tomlkit.parse(WORKSPACE_EXAMPLE)["workspace"]["members"]
            return [
                (temporary_dir_with_cargo_toml / m / "Cargo.toml").resolve()
                for m in members
            ]

        with self.__create_cargo_layout() as temporary_dir_with_cargo_toml:
            cargo = CargoVersionCommand(PEP440VersioningScheme)
            previous = PEP440VersioningScheme.parse_version("0.1.0")
            new_version = PEP440VersioningScheme.parse_version("23.4.1")
            updated = cargo.update_version(new_version)
            self.assertEqual(updated.previous, previous)
            self.assertEqual(updated.new, new_version)
            self.assertEqual(
                updated.changed_files,
                expected_changed_files(temporary_dir_with_cargo_toml),
            )

    def test_update_fail(self):
        with self.__create_cargo_layout():
            cargo = CargoVersionCommand(PEP440VersioningScheme)
            previous = PEP440VersioningScheme.parse_version("0.1.0")
            new_version = PEP440VersioningScheme.parse_version("0.1.0")
            updated = cargo.update_version(new_version)
            self.assertEqual(updated.previous, previous)
            self.assertEqual(updated.new, new_version)
            self.assertEqual(
                updated.changed_files,
                [],
            )


class VerifyCargoVersionCommandTestCase(unittest.TestCase):
    def test_verify_failure(self):
        with temp_file(
            VERSION_EXAMPLE,
            name="Cargo.toml",
            change_into=True,
        ):
            version = PEP440VersioningScheme.parse_version("2.3.4")
            cargo = CargoVersionCommand(PEP440VersioningScheme)

            with self.assertRaisesRegex(
                VersionError,
                "Provided version 2.3.4 does not match the "
                "current version 0.1.0.",
            ):
                cargo.verify_version(version)

    def test_success(self):
        with temp_file(
            VERSION_EXAMPLE,
            name="Cargo.toml",
            change_into=True,
        ):
            version = PEP440VersioningScheme.parse_version("0.1.0")
            cargo = CargoVersionCommand(PEP440VersioningScheme)
            cargo.verify_version(version)
