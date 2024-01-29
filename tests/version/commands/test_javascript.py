# Copyright (C) 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import json
import unittest
from unittest.mock import MagicMock, patch

from pontos.testing import temp_directory, temp_file
from pontos.version import VersionError
from pontos.version.commands import JavaScriptVersionCommand
from pontos.version.schemes import SemanticVersioningScheme


class GetCurrentJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_get_current_version(self):
        content = '{"name": "foo", "version": "1.2.3"}'
        with temp_file(content, name="package.json", change_into=True):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            version = cmd.get_current_version()

            self.assertEqual(
                version, SemanticVersioningScheme.parse_version("1.2.3")
            )

    def test_no_project_file(self):
        with (
            temp_directory(change_into=True),
            self.assertRaisesRegex(VersionError, ".* file not found."),
        ):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.get_current_version()

    def test_no_package_version(self):
        content = '{"name": "foo"}'
        with (
            temp_file(content, name="package.json", change_into=True),
            self.assertRaisesRegex(VersionError, "Version field missing in"),
        ):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.get_current_version()

    def test_no_valid_json_in_package_version(self):
        content = "{"
        with (
            temp_file(content, name="package.json", change_into=True),
            self.assertRaisesRegex(VersionError, "No valid JSON found."),
        ):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.get_current_version()


class UpdateJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_update_version_file(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.get_current_version()
            updated = cmd.update_version(
                SemanticVersioningScheme.parse_version("22.4.0")
            )

            self.assertEqual(
                updated.previous,
                SemanticVersioningScheme.parse_version("1.2.3"),
            )
            self.assertEqual(
                updated.new, SemanticVersioningScheme.parse_version("22.4.0")
            )
            self.assertEqual(updated.changed_files, [temp.resolve()])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0")

    def test_update_js_version_file(self):
        content = '{"name":"foo", "version":"1.2.3"}'
        js_content = """const foo = "bar";
const VERSION = "1.2.3";
const func = () => ();
"""

        with temp_directory(change_into=True) as temp_dir:
            package_json = temp_dir / "package.json"
            package_json.write_text(content, encoding="utf8")
            js_version_file = (
                temp_dir / JavaScriptVersionCommand.version_file_paths[0]
            )
            js_version_file.parent.mkdir()
            js_version_file.write_text(js_content, encoding="utf8")

            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            updated = cmd.update_version(
                SemanticVersioningScheme.parse_version("22.4.0")
            )

            self.assertEqual(
                updated.previous,
                SemanticVersioningScheme.parse_version("1.2.3"),
            )
            self.assertEqual(
                updated.new, SemanticVersioningScheme.parse_version("22.4.0")
            )
            self.assertEqual(
                updated.changed_files,
                [
                    package_json.resolve(),
                    JavaScriptVersionCommand.version_file_paths[0],
                ],
            )

            with package_json.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0")

            self.assertEqual(
                js_version_file.read_text(encoding="utf8"),
                'const foo = "bar";\nconst VERSION = "22.4.0";\n'
                "const func = () => ();\n",
            )

    def test_update_js_version_file_with_single_quotes(self):
        content = '{"name":"foo", "version":"1.2.3"}'
        js_content = """const foo = "bar";
const VERSION = '1.2.3';
const func = () => ();
"""

        with temp_directory(change_into=True) as temp_dir:
            package_json = temp_dir / "package.json"
            package_json.write_text(content, encoding="utf8")
            js_version_file = (
                temp_dir / JavaScriptVersionCommand.version_file_paths[0]
            )
            js_version_file.parent.mkdir()
            js_version_file.write_text(js_content, encoding="utf8")

            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            updated = cmd.update_version(
                SemanticVersioningScheme.parse_version("22.4.0")
            )

            self.assertEqual(
                updated.previous,
                SemanticVersioningScheme.parse_version("1.2.3"),
            )
            self.assertEqual(
                updated.new, SemanticVersioningScheme.parse_version("22.4.0")
            )
            self.assertEqual(
                updated.changed_files,
                [
                    package_json.resolve(),
                    JavaScriptVersionCommand.version_file_paths[0],
                ],
            )

            with package_json.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0")

            self.assertEqual(
                js_version_file.read_text(encoding="utf8"),
                "const foo = \"bar\";\nconst VERSION = '22.4.0';\n"
                "const func = () => ();\n",
            )

    def test_update_version_files(self):
        content = '{"name":"foo", "version":"1.2.3"}'
        file_content = """const foo = "bar";
const VERSION = "1.2.3";
const func = () => ();
"""

        with temp_directory(change_into=True) as temp_dir:
            package_json = temp_dir / "package.json"
            package_json.write_text(content, encoding="utf8")

            js_version_file = (
                temp_dir / JavaScriptVersionCommand.version_file_paths[0]
            )
            js_version_file.parent.mkdir()
            js_version_file.write_text(file_content, encoding="utf8")

            ts_version_file = (
                temp_dir / JavaScriptVersionCommand.version_file_paths[1]
            )
            ts_version_file.write_text(file_content, encoding="utf8")

            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            updated = cmd.update_version(
                SemanticVersioningScheme.parse_version("22.4.0")
            )

            self.assertEqual(
                updated.previous,
                SemanticVersioningScheme.parse_version("1.2.3"),
            )
            self.assertEqual(
                updated.new, SemanticVersioningScheme.parse_version("22.4.0")
            )
            self.assertEqual(
                updated.changed_files,
                [
                    package_json.resolve(),
                    JavaScriptVersionCommand.version_file_paths[0],
                    JavaScriptVersionCommand.version_file_paths[1],
                ],
            )

            with package_json.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0")

            self.assertEqual(
                js_version_file.read_text(encoding="utf8"),
                'const foo = "bar";\nconst VERSION = "22.4.0";\n'
                "const func = () => ();\n",
            )

    def test_update_version_develop(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            new_version = SemanticVersioningScheme.parse_version("22.4.0-dev1")
            updated = cmd.update_version(new_version)

            self.assertEqual(
                updated.previous,
                SemanticVersioningScheme.parse_version("1.2.3"),
            )
            self.assertEqual(updated.new, new_version)
            self.assertEqual(updated.changed_files, [temp.resolve()])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "22.4.0-dev1")

    def test_no_update(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            updated = cmd.update_version(
                SemanticVersioningScheme.parse_version("1.2.3")
            )

            self.assertEqual(
                updated.previous,
                SemanticVersioningScheme.parse_version("1.2.3"),
            )
            self.assertEqual(
                updated.new, SemanticVersioningScheme.parse_version("1.2.3")
            )
            self.assertEqual(updated.changed_files, [])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "1.2.3")

    def test_forced_update(self):
        content = '{"name":"foo", "version":"1.2.3"}'

        with temp_file(content, name="package.json", change_into=True) as temp:
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            updated = cmd.update_version(
                SemanticVersioningScheme.parse_version("1.2.3"), force=True
            )

            self.assertEqual(
                updated.previous,
                SemanticVersioningScheme.parse_version("1.2.3"),
            )
            self.assertEqual(
                updated.new, SemanticVersioningScheme.parse_version("1.2.3")
            )
            self.assertEqual(updated.changed_files, [temp.resolve()])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_package = json.load(fp)

            self.assertEqual(fake_package["version"], "1.2.3")


class VerifyJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_versions_not_equal(self):
        with (
            patch.object(
                JavaScriptVersionCommand,
                "get_current_version",
                MagicMock(
                    return_value=SemanticVersioningScheme.parse_version("1.2.3")
                ),
            ),
            self.assertRaisesRegex(
                VersionError,
                "Provided version .* does not match the current version .*",
            ),
        ):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.verify_version(SemanticVersioningScheme.parse_version("22.4.0"))

    def test_verify_success(self):
        with patch.object(
            JavaScriptVersionCommand,
            "get_current_version",
            MagicMock(
                return_value=SemanticVersioningScheme.parse_version("22.4.0")
            ),
        ):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.verify_version(SemanticVersioningScheme.parse_version("22.4.0"))

    def test_verify_js_mismatch(self):
        with (
            patch.object(
                JavaScriptVersionCommand,
                "get_current_version",
                MagicMock(
                    return_value=SemanticVersioningScheme.parse_version(
                        "22.4.0"
                    )
                ),
            ),
            patch.object(
                JavaScriptVersionCommand,
                "_get_current_file_version",
                MagicMock(
                    return_value=SemanticVersioningScheme.parse_version(
                        "22.5.0"
                    )
                ),
            ),
            self.assertRaisesRegex(
                VersionError,
                "Provided version 22.4.0 does not match the current version 22.5.0 "
                "in src/version.js.",
            ),
        ):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.verify_version(SemanticVersioningScheme.parse_version("22.4.0"))

    def test_verify_ts_mismatch(self):
        with (
            patch.object(
                JavaScriptVersionCommand,
                "get_current_version",
                MagicMock(
                    return_value=SemanticVersioningScheme.parse_version(
                        "22.4.0"
                    )
                ),
            ),
            patch.object(
                JavaScriptVersionCommand,
                "_get_current_file_version",
                MagicMock(
                    side_effect=[
                        SemanticVersioningScheme.parse_version("22.4.0"),
                        SemanticVersioningScheme.parse_version("22.5.0"),
                    ]
                ),
            ),
            self.assertRaisesRegex(
                VersionError,
                "Provided version 22.4.0 does not match the current version 22.5.0 "
                "in src/version.ts.",
            ),
        ):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.verify_version(SemanticVersioningScheme.parse_version("22.4.0"))

    def test_verify_current(self):
        with patch.object(
            JavaScriptVersionCommand,
            "get_current_version",
            MagicMock(
                return_value=SemanticVersioningScheme.parse_version("22.4.0")
            ),
        ):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.verify_version("current")
            cmd.verify_version(None)

    def test_verify_current_failure(self):
        with temp_directory(change_into=True):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)

            with self.assertRaisesRegex(
                VersionError, "^.*package.json file not found"
            ):
                cmd.verify_version("current")

            with self.assertRaisesRegex(
                VersionError, "^.*package.json file not found"
            ):
                cmd.verify_version(None)

    def test_verify_current_js_version_matches(self):
        content = '{"name":"foo", "version":"1.2.3"}'
        js_content = 'const VERSION = "1.2.3";'

        with temp_directory(change_into=True) as temp_dir:
            package_json = temp_dir / "package.json"
            package_json.write_text(content, encoding="utf8")
            js_version_file = (
                temp_dir / JavaScriptVersionCommand.version_file_paths[0]
            )
            js_version_file.parent.mkdir()
            js_version_file.write_text(js_content, encoding="utf8")

            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.verify_version("current")
            cmd.verify_version(None)

    def test_verify_current_js_mismatch(self):
        content = '{"name":"foo", "version":"1.2.3"}'
        js_content = 'const VERSION = "1.2.4";'

        with (
            temp_directory(change_into=True) as temp_dir,
            self.assertRaisesRegex(
                VersionError,
                "The version 1.2.4 in src/version.js doesn't match the current "
                "version 1.2.3.",
            ),
        ):
            package_json = temp_dir / "package.json"
            package_json.write_text(content, encoding="utf8")
            js_version_file = (
                temp_dir / JavaScriptVersionCommand.version_file_paths[0]
            )
            js_version_file.parent.mkdir()
            js_version_file.write_text(js_content, encoding="utf8")

            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)
            cmd.verify_version("current")
            cmd.verify_version(None)


class ProjectFileJavaScriptVersionCommandTestCase(unittest.TestCase):
    def test_project_file_not_found(self):
        with temp_directory(change_into=True):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)

            self.assertFalse(cmd.project_found())

    def test_project_file_found(self):
        with temp_file(name="package.json", change_into=True):
            cmd = JavaScriptVersionCommand(SemanticVersioningScheme)

            self.assertTrue(cmd.project_found())
