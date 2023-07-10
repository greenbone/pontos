# Copyright (C) 2023 Greenbone AG
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
# ruff: noqa: E501

import unittest
from pathlib import Path

from lxml import etree

from pontos.testing import temp_directory, temp_file
from pontos.version import VersionError
from pontos.version.commands import JavaVersionCommand
from pontos.version.commands._java import find_file, replace_string_in_file
from pontos.version.schemes import PEP440VersioningScheme


class TestFindFile(unittest.TestCase):
    def test_file_found(self):
        with temp_directory() as temp_dir:
            deep_path = Path(temp_dir / "foo/bat/config/swagger/")
            deep_path.mkdir(parents=True)
            Path(deep_path / "SwaggerConfig.java").touch()
            self.assertTrue(
                Path(
                    temp_dir / "foo/bat/config/swagger/SwaggerConfig.java"
                ).exists()
            )
            filename = Path("SwaggerConfig.java")
            search_path = temp_dir  # Assuming 'config/swagger' is two levels up
            search_glob = "**/config/swagger/*"

            result = find_file(filename, search_path, search_glob)

            self.assertIsNotNone(result)
            self.assertEqual(result.name, filename.name)

    def test_file_not_found(self):
        with temp_directory() as temp_dir:
            Path(
                temp_dir / "foo/bat/config/swagger/SwaggerConfig.java",
                parents=True,
            )
            filename = Path("NonExistentFile.java")
            search_path = temp_dir
            search_glob = "**/config/swagger/*"

            result = find_file(filename, search_path, search_glob)

            self.assertIsNone(result)


class TestReplaceString(unittest.TestCase):
    def test_replace_string_in_file(self):
        # Define the test parameters
        content = """
        Foo, bar
        baz
            .version("1.2.3")
        glubb
        """
        pattern = r'\.version\("([0-9]+\.[0-9]+\.[0-9]+)"\)'
        replacement = "1.2.4"

        with temp_file(content=content) as tmp:
            replace_string_in_file(tmp, pattern, replacement)

            updated_content = tmp.read_text(encoding="utf-8")

            # Verify the replacement was performed correctly
            self.assertNotRegex(
                updated_content, "1.2.3"
            )  # Pattern should not be present
            self.assertIn(
                replacement, updated_content
            )  # Replacement should be present

    def test_replace_string_in_file_no_match(self):
        # Define the test parameters
        content = """
        Foo, bar
        baz
            .versio("1.2.3")
        glubb
        """
        pattern = r'\.version\("([0-9]+\.[0-9]+\.[0-9]+)"\)'
        replacement = "1.2.4"

        with temp_file(content=content) as tmp:
            # Call the function under test
            replace_string_in_file(tmp, pattern, replacement)

            # Read the content of the unmodified file
            updated_content = tmp.read_text(encoding="utf-8")

            # Verify the content remains unchanged
            self.assertNotRegex(updated_content, replacement)
            self.assertEqual(updated_content, content)


class GetCurrentJavaVersionCommandTestCase(unittest.TestCase):
    def test_get_current_version(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion><groupId>net.greenbone.umbrella</groupId>
        <artifactId>msspadminservice</artifactId><version>2023.5.3</version></project>"""
        with temp_file(content, name="pom.xml", change_into=True):
            cmd = JavaVersionCommand(PEP440VersioningScheme)
            version = cmd.get_current_version()

            self.assertEqual(
                version, PEP440VersioningScheme.parse_version("2023.5.3")
            )

    def test_no_project_file(self):
        with temp_directory(change_into=True), self.assertRaisesRegex(
            VersionError, ".* file not found."
        ):
            cmd = JavaVersionCommand(PEP440VersioningScheme)
            cmd.get_current_version()

    def test_no_package_version(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
            <modelVersion>4.0.0</modelVersion><groupId>net.greenbone.umbrella</groupId>
            <artifactId>msspadminservice</artifactId></project>"""
        with temp_file(
            content, name="pom.xml", change_into=True
        ), self.assertRaisesRegex(VersionError, "Version tag missing in"):
            cmd = JavaVersionCommand(PEP440VersioningScheme)
            cmd.get_current_version()

    def test_no_valid_xml_in_pom(self):
        content = "<"
        with temp_file(
            content, name="pom.xml", change_into=True
        ), self.assertRaisesRegex(
            VersionError, "StartTag: invalid element name,"
        ):
            cmd = JavaVersionCommand(PEP440VersioningScheme)
            cmd.get_current_version()

        content = "<foo><bar/>"
        with temp_file(
            content, name="pom.xml", change_into=True
        ), self.assertRaisesRegex(
            VersionError, "Premature end of data in tag foo"
        ):
            cmd = JavaVersionCommand(PEP440VersioningScheme)
            cmd.get_current_version()


class UpdateJavaVersionCommandTestCase(unittest.TestCase):
    def test_update_version_file(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion><groupId>net.greenbone.umbrella</groupId>
        <artifactId>msspadminservice</artifactId><version>2023.5.3</version></project>"""

        with temp_file(content, name="pom.xml", change_into=True) as temp:
            cmd = JavaVersionCommand(PEP440VersioningScheme)
            cmd.get_current_version()
            updated = cmd.update_version(
                PEP440VersioningScheme.parse_version("2023.6.0")
            )

            self.assertEqual(
                updated.previous,
                PEP440VersioningScheme.parse_version("2023.5.3"),
            )
            self.assertEqual(
                updated.new, PEP440VersioningScheme.parse_version("2023.6.0")
            )
            self.assertEqual(updated.changed_files, [temp.resolve()])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_pom = etree.parse(fp).getroot()

            self.assertEqual(fake_pom.find("{*}version").text, "2023.6.0")

    def test_update_version_develop(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion><groupId>net.greenbone.umbrella</groupId>
        <artifactId>msspadminservice</artifactId><version>2023.5.3</version></project>"""

        with temp_file(content, name="pom.xml", change_into=True) as temp:
            cmd = JavaVersionCommand(PEP440VersioningScheme)
            new_version = PEP440VersioningScheme.parse_version("2023.6.0.dev1")
            updated = cmd.update_version(new_version)

            self.assertEqual(
                updated.previous,
                PEP440VersioningScheme.parse_version("2023.5.3"),
            )
            self.assertEqual(
                updated.new,
                PEP440VersioningScheme.parse_version("2023.6.0.dev1"),
            )
            self.assertEqual(updated.changed_files, [temp.resolve()])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_pom = etree.parse(fp).getroot()

            self.assertEqual(fake_pom.find("{*}version").text, "2023.6.0.dev1")

    def test_no_update(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion><groupId>net.greenbone.umbrella</groupId>
        <artifactId>msspadminservice</artifactId><version>2023.5.3</version></project>"""

        with temp_file(content, name="pom.xml", change_into=True) as temp:
            cmd = JavaVersionCommand(PEP440VersioningScheme)
            updated = cmd.update_version(
                PEP440VersioningScheme.parse_version("2023.5.3")
            )

            self.assertEqual(
                updated.previous,
                PEP440VersioningScheme.parse_version("2023.5.3"),
            )
            self.assertEqual(
                updated.new, PEP440VersioningScheme.parse_version("2023.5.3")
            )
            self.assertEqual(updated.changed_files, [])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_pom = etree.parse(fp).getroot()

            self.assertEqual(fake_pom.find("{*}version").text, "2023.5.3")

    def test_forced_update(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion><groupId>net.greenbone.umbrella</groupId>
        <artifactId>msspadminservice</artifactId><version>2023.5.3</version></project>"""

        with temp_file(content, name="pom.xml", change_into=True) as temp:
            cmd = JavaVersionCommand(PEP440VersioningScheme)
            updated = cmd.update_version(
                PEP440VersioningScheme.parse_version("2023.5.3"), force=True
            )

            self.assertEqual(
                updated.previous,
                PEP440VersioningScheme.parse_version("2023.5.3"),
            )
            self.assertEqual(
                updated.new, PEP440VersioningScheme.parse_version("2023.5.3")
            )
            self.assertEqual(updated.changed_files, [temp.resolve()])

            with temp.open(mode="r", encoding="utf-8") as fp:
                fake_pom = etree.parse(fp).getroot()

            self.assertEqual(fake_pom.find("{*}version").text, "2023.5.3")
