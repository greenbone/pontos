# SPDX-FileCopyrightText: 2023-2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import tomlkit

from pontos.testing import temp_directory, temp_file
from pontos.version import VersionError
from pontos.version.commands._cargo import CargoVersionCommand
from pontos.version.schemes import PEP440VersioningScheme

"""
This modules verifies different Cargo.toml configuration scenarios.

EXAMPLE 1:
    The root Cargo.toml configures a package that has also a workspace and members
    with independent versions in its members Cargo.toml files. Pontos will only 
    update the version of the root Cargo.toml ([package.version]).
EXAMPLE 2:
    The root Cargo.toml configures a workspace only, members and a version for those
    members. The Cargo.toml files of the members are configured to use the version
    configured in the workspace table of the root Cargo.toml. Pontos will only update
    the version of the root Cargo.toml ([workspace.package.version]).
EXAMPLE 3:
    Combines EXAMPLE_1 and EXAMPLE_2. Pontos will only update the version of the
    root Cargo.toml ([package.version]).
"""

PACKAGE_EXAMPLE_1 = """
[package]
name = "nasl-syntax"
version = "0.1.0"
edition = "2021"
license = "GPL-2.0-or-later"
"""

WORKSPACE_EXAMPLE_1 = """
[package]
name = "main"
version = "0.1.0"
edition = "2021"
license = "GPL-2.0-or-later"

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

PACKAGE_EXAMPLE_2 = """
[package]
name = "nasl-syntax"
version.workspace = true
"""

WORKSPACE_EXAMPLE_2 = """
[workspace.package]
version = "0.1.0"
edition = "2025"
license = "GPL-2.0-or-later"

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

PACKAGE_EXAMPLE_3 = """
[package]
name = "nasl-syntax"
version.workspace = true
"""

WORKSPACE_EXAMPLE_3 = """
[package]
name = "main"
version = "0.2.0"
edition = "2021"
license = "GPL-2.0-or-later"

[workspace.package]
version = "0.1.0"
edition = "2025"
license = "GPL-2.0-or-later"

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
    def __create_cargo_layout(
        self, *, workspace_toml, member_toml
    ) -> Iterator[Path]:
        with temp_directory(change_into=True) as temp_dir:
            cargo_toml = temp_dir / "Cargo.toml"
            cargo_toml.write_text(workspace_toml)
            workspace_toml_file = tomlkit.parse(workspace_toml)
            members = workspace_toml_file["workspace"]["members"]  # type: ignore[index, arg-type]
            if isinstance(members, tomlkit.items.Array):
                for member in members:
                    npath = temp_dir / f"{member}"
                    npath.mkdir()
                    pf = npath / "Cargo.toml"
                    pf.write_text(member_toml.replace("nasl-syntax", member))
            yield temp_dir
        return None

    def test_success(self):
        examples = [
            ("0.1.0", WORKSPACE_EXAMPLE_1, PACKAGE_EXAMPLE_1),
            ("0.1.0", WORKSPACE_EXAMPLE_2, PACKAGE_EXAMPLE_2),
            ("0.2.0", WORKSPACE_EXAMPLE_3, PACKAGE_EXAMPLE_3),
        ]
        for version, cargo_toml, member_cargo_toml in examples:
            with self.subTest(
                version=version,
                cargo_toml=cargo_toml,
                member_cargo_toml=member_cargo_toml,
            ):
                with self.__create_cargo_layout(
                    workspace_toml=cargo_toml,
                    member_toml=member_cargo_toml,
                ) as temp_dir:
                    cargo = CargoVersionCommand(PEP440VersioningScheme)
                    previous = PEP440VersioningScheme.parse_version(version)
                    new_version = PEP440VersioningScheme.parse_version("23.4.1")
                    updated = cargo.update_version(new_version)
                    self.assertEqual(updated.previous, previous)
                    self.assertEqual(updated.new, new_version)
                    self.assertEqual(
                        updated.changed_files,
                        [(temp_dir / "Cargo.toml").resolve()],
                    )

    def test_failure(self):
        examples = [
            ("0.1.0", WORKSPACE_EXAMPLE_1, PACKAGE_EXAMPLE_1),
            ("0.1.0", WORKSPACE_EXAMPLE_2, PACKAGE_EXAMPLE_2),
            ("0.2.0", WORKSPACE_EXAMPLE_3, PACKAGE_EXAMPLE_3),
        ]
        for version, cargo_toml, member_cargo_toml in examples:
            with self.subTest(
                version=version,
                cargo_toml=cargo_toml,
                member_cargo_toml=member_cargo_toml,
            ):
                with self.__create_cargo_layout(
                    workspace_toml=cargo_toml,
                    member_toml=member_cargo_toml,
                ):
                    cargo = CargoVersionCommand(PEP440VersioningScheme)
                    previous = PEP440VersioningScheme.parse_version(version)
                    new_version = PEP440VersioningScheme.parse_version(version)
                    updated = cargo.update_version(new_version)
                    self.assertEqual(updated.previous, previous)
                    self.assertEqual(updated.new, new_version)
                    self.assertEqual(
                        updated.changed_files,
                        [],
                    )


class VerifyCargoVersionCommandTestCase(unittest.TestCase):
    def test_success(self):
        examples = [
            ("0.1.0", WORKSPACE_EXAMPLE_1),
            ("0.1.0", WORKSPACE_EXAMPLE_2),
            ("0.2.0", WORKSPACE_EXAMPLE_3),
        ]
        for version, cargo_toml in examples:
            with self.subTest(version=version, cargo_toml=cargo_toml):
                with temp_file(
                    cargo_toml,
                    name="Cargo.toml",
                    change_into=True,
                ):
                    pep440_version = PEP440VersioningScheme.parse_version(
                        version
                    )
                    cargo = CargoVersionCommand(PEP440VersioningScheme)
                    cargo.verify_version(pep440_version)

    def test_verify_failure(self):
        examples = [
            ("0.1.0", WORKSPACE_EXAMPLE_1),
            ("0.1.0", WORKSPACE_EXAMPLE_2),
            ("0.2.0", WORKSPACE_EXAMPLE_3),
        ]
        for version, cargo_toml in examples:
            with self.subTest(version=version, cargo_toml=cargo_toml):
                with temp_file(
                    cargo_toml,
                    name="Cargo.toml",
                    change_into=True,
                ):
                    pep440_version = PEP440VersioningScheme.parse_version(
                        "2.3.4"
                    )
                    cargo = CargoVersionCommand(PEP440VersioningScheme)
                    with self.assertRaisesRegex(
                        VersionError,
                        "Provided version 2.3.4 does not match the "
                        f"current version {version}.",
                    ):
                        cargo.verify_version(pep440_version)
