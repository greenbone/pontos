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

import unittest

from lxml import etree

from pontos.testing import temp_directory, temp_file
from pontos.version import VersionError
from pontos.version.commands import JavaVersionCommand
from pontos.version.schemes import PEP440VersioningScheme


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
