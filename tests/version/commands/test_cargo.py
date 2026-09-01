# SPDX-FileCopyrightText: 2023-2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import tomlkit
from tomlkit.items import Array

from pontos.testing import temp_directory, temp_file
from pontos.version import VersionError
from pontos.version.commands._cargo import CargoVersionCommand
from pontos.version.schemes import SemanticVersioningScheme

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


class CargoFileCommandTestCase(unittest.TestCase):
    def test_cargo_toml_requires_project_file(self):
        with temp_directory(change_into=True):
            command = CargoVersionCommand(SemanticVersioningScheme)

            with self.assertRaisesRegex(
                VersionError, "Cargo.toml file not found"
            ):
                command.get_current_version()

    def test_cargo_toml_requires_version(self):
        with temp_file(
            '[package]\nname = "example"',
            name="Cargo.toml",
            change_into=True,
        ):
            command = CargoVersionCommand(SemanticVersioningScheme)

            with self.assertRaisesRegex(VersionError, "No version information"):
                command.get_current_version()

    def test_update_creates_package_section(self):
        with temp_file(
            "[workspace]\nmembers = []",
            name="Cargo.toml",
            change_into=True,
        ):
            command = CargoVersionCommand(SemanticVersioningScheme)
            new_version = SemanticVersioningScheme.parse_version("2.0.0")

            command._update_cargo_toml_file(new_version)

            cargo_toml = tomlkit.parse(
                command.project_file_path.read_text(encoding="utf-8")
            )
            self.assertEqual(cargo_toml["package"]["version"], "2.0.0")

    def test_update_workspace_package_version(self):
        with temp_file(
            WORKSPACE_EXAMPLE_2,
            name="Cargo.toml",
            change_into=True,
        ):
            command = CargoVersionCommand(SemanticVersioningScheme)
            new_version = SemanticVersioningScheme.parse_version("2.0.0")

            command._update_cargo_toml_file(new_version)

            cargo_toml = tomlkit.parse(
                command.project_file_path.read_text(encoding="utf-8")
            )
            self.assertEqual(
                cargo_toml["workspace"]["package"]["version"], "2.0.0"
            )

    def test_lock_file_requires_lock_file(self):
        with temp_file(
            '[package]\nname = "example"\nversion = "1.0.0"',
            name="Cargo.toml",
        ):
            command = CargoVersionCommand(SemanticVersioningScheme)
            new_version = SemanticVersioningScheme.parse_version("2.0.0")

            with self.assertRaisesRegex(
                VersionError, "Cargo.lock file not found"
            ):
                command._update_cargo_lock_file(new_version)

    def test_lock_file_requires_package_entries(self):
        with temp_file(
            '[package]\nname = "example"\nversion = "1.0.0"',
            name="Cargo.toml",
            change_into=True,
        ):
            Path("Cargo.lock").write_text("[metadata]\n")
            command = CargoVersionCommand(SemanticVersioningScheme)
            new_version = SemanticVersioningScheme.parse_version("2.0.0")

            with self.assertRaisesRegex(VersionError, r"\[\[package\]\]"):
                command._update_cargo_lock_file(new_version)

    def test_update_version_updates_virtual_workspace_members_in_lock_file(
        self,
    ):
        with temp_directory(change_into=True) as temp_dir:
            Path("Cargo.toml").write_text(
                '[workspace]\nmembers = ["client", "server"]\n\n'
                '[workspace.package]\nversion = "1.0.0"\n'
            )
            for member in ("client", "server"):
                Path(member).mkdir()
                (Path(member) / "Cargo.toml").write_text(
                    f'[package]\nname = "{member}"\nversion.workspace = true\n'
                )
            Path("Cargo.lock").write_text(
                '[[package]]\nname = "other"\nversion = "9.9.9"\n\n'
                '[[package]]\nname = "client"\nversion = "1.0.0"\n\n'
                '[[package]]\nname = "server"\nversion = "1.0.0"\n'
            )
            command = CargoVersionCommand(SemanticVersioningScheme)
            new_version = SemanticVersioningScheme.parse_version("2.0.0")

            updated = command.update_version(new_version)

            cargo_toml = tomlkit.parse(Path("Cargo.toml").read_text())
            lock = tomlkit.parse(Path("Cargo.lock").read_text())
            self.assertEqual(
                cargo_toml["workspace"]["package"]["version"], "2.0.0"
            )
            self.assertEqual(lock["package"][0]["version"], "9.9.9")
            self.assertEqual(lock["package"][1]["version"], "2.0.0")
            self.assertEqual(lock["package"][2]["version"], "2.0.0")
            self.assertEqual(
                updated.changed_files,
                [
                    (temp_dir / "Cargo.toml").resolve(),
                    (temp_dir / "Cargo.lock").resolve(),
                ],
            )

    def test_lock_file_updates_matching_package_only(self):
        with temp_file(
            '[package]\nname = "example"\nversion = "1.0.0"',
            name="Cargo.toml",
            change_into=True,
        ):
            Path("Cargo.lock").write_text(
                '[[package]]\nname = "other"\nversion = "9.9.9"\n\n'
                '[[package]]\nname = "example"\nversion = "1.0.0"'
            )
            command = CargoVersionCommand(SemanticVersioningScheme)
            new_version = SemanticVersioningScheme.parse_version("2.0.0")

            command._update_cargo_lock_file(new_version)

            lock = tomlkit.parse(
                command.cargo_lock_file_path.read_text(encoding="utf-8")
            )
            self.assertEqual(lock["package"][0]["version"], "9.9.9")
            self.assertEqual(lock["package"][1]["version"], "2.0.0")

    def test_update_version_wraps_cargo_toml_os_error(self):
        with temp_file(
            '[package]\nname = "example"\nversion = "1.0.0"',
            name="Cargo.toml",
            change_into=True,
        ):
            command = CargoVersionCommand(SemanticVersioningScheme)
            new_version = SemanticVersioningScheme.parse_version("2.0.0")

            with (
                patch.object(
                    command,
                    "_update_cargo_toml_file",
                    side_effect=OSError("write"),
                ),
                self.assertRaisesRegex(VersionError, "Cargo.toml"),
            ):
                command.update_version(new_version)

    def test_update_version_wraps_cargo_lock_os_error(self):
        with temp_file(
            '[package]\nname = "example"\nversion = "1.0.0"',
            name="Cargo.toml",
            change_into=True,
        ):
            Path("Cargo.lock").write_text(
                '[[package]]\nname = "example"\nversion = "1.0.0"'
            )
            command = CargoVersionCommand(SemanticVersioningScheme)
            new_version = SemanticVersioningScheme.parse_version("2.0.0")

            with (
                patch.object(command, "_update_cargo_toml_file"),
                patch.object(
                    command,
                    "_update_cargo_lock_file",
                    side_effect=OSError("write"),
                ),
                self.assertRaisesRegex(VersionError, "Cargo.lock"),
            ):
                command.update_version(new_version)


class VerifyCargoUpdateCommandTestCase(unittest.TestCase):
    @contextmanager
    def __create_cargo_layout(
        self, *, workspace_toml, member_toml
    ) -> Iterator[Path]:
        with temp_directory(change_into=True) as temp_dir:
            cargo_toml = temp_dir / "Cargo.toml"
            cargo_toml.write_text(workspace_toml)
            workspace_toml_file = tomlkit.parse(workspace_toml)
            package = workspace_toml_file.get("package", {})
            if package_name := package.get("name"):
                (temp_dir / "Cargo.lock").write_text(
                    "[[package]]\n"
                    'name = "other"\n'
                    'version = "9.9.9"\n\n'
                    "[[package]]\n"
                    f'name = "{package_name}"\n'
                    f'version = "{package.get("version")}"\n'
                )
            members = workspace_toml_file["workspace"]["members"]  # type: ignore[index, arg-type]
            if isinstance(members, Array):
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
            ("0.2.0", WORKSPACE_EXAMPLE_3, PACKAGE_EXAMPLE_3),
        ]
        for version, cargo_toml, member_cargo_toml in examples:
            with (
                self.subTest(
                    version=version,
                    cargo_toml=cargo_toml,
                    member_cargo_toml=member_cargo_toml,
                ),
                self.__create_cargo_layout(
                    workspace_toml=cargo_toml,
                    member_toml=member_cargo_toml,
                ) as temp_dir,
            ):
                cargo = CargoVersionCommand(SemanticVersioningScheme)
                previous = SemanticVersioningScheme.parse_version(version)
                new_version = SemanticVersioningScheme.parse_version("23.4.1")
                updated = cargo.update_version(new_version)
                self.assertEqual(updated.previous, previous)
                self.assertEqual(updated.new, new_version)
                self.assertEqual(
                    updated.changed_files,
                    [
                        (temp_dir / "Cargo.toml").resolve(),
                        (temp_dir / "Cargo.lock").resolve(),
                    ],
                )
                lock = tomlkit.parse((temp_dir / "Cargo.lock").read_text())
                self.assertEqual(lock["package"][0]["version"], "9.9.9")
                self.assertEqual(lock["package"][1]["version"], "23.4.1")

    def test_failure(self):
        examples = [
            ("0.1.0", WORKSPACE_EXAMPLE_1, PACKAGE_EXAMPLE_1),
            ("0.1.0", WORKSPACE_EXAMPLE_2, PACKAGE_EXAMPLE_2),
            ("0.2.0", WORKSPACE_EXAMPLE_3, PACKAGE_EXAMPLE_3),
        ]
        for version, cargo_toml, member_cargo_toml in examples:
            with (
                self.subTest(
                    version=version,
                    cargo_toml=cargo_toml,
                    member_cargo_toml=member_cargo_toml,
                ),
                self.__create_cargo_layout(
                    workspace_toml=cargo_toml,
                    member_toml=member_cargo_toml,
                ),
            ):
                cargo = CargoVersionCommand(SemanticVersioningScheme)
                previous = SemanticVersioningScheme.parse_version(version)
                new_version = SemanticVersioningScheme.parse_version(version)
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
            with (
                self.subTest(version=version, cargo_toml=cargo_toml),
                temp_file(
                    cargo_toml,
                    name="Cargo.toml",
                    change_into=True,
                ),
            ):
                semantic_version = SemanticVersioningScheme.parse_version(
                    version
                )
                cargo = CargoVersionCommand(SemanticVersioningScheme)
                cargo.verify_version(semantic_version)

    def test_verify_failure(self):
        examples = [
            ("0.1.0", WORKSPACE_EXAMPLE_1),
            ("0.1.0", WORKSPACE_EXAMPLE_2),
            ("0.2.0", WORKSPACE_EXAMPLE_3),
        ]
        for version, cargo_toml in examples:
            with (
                self.subTest(version=version, cargo_toml=cargo_toml),
                temp_file(
                    cargo_toml,
                    name="Cargo.toml",
                    change_into=True,
                ),
            ):
                semantic_version = SemanticVersioningScheme.parse_version(
                    "2.3.4"
                )
                cargo = CargoVersionCommand(SemanticVersioningScheme)
                with self.assertRaisesRegex(
                    VersionError,
                    "Provided version 2.3.4 does not match the "
                    f"current version {version}.",
                ):
                    cargo.verify_version(semantic_version)
