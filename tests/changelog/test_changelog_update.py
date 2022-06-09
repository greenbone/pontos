# -*- coding: utf-8 -*-
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

import unittest
from datetime import date
from pathlib import Path

from pontos import changelog


class ChangelogUpdateTestCase(unittest.TestCase):
    def test_markdown_based_on_example(self):
        own_path = Path(__file__).absolute()
        test_directory = own_path.__str__()[0 : (len(own_path.name) * -1)]
        path = test_directory + "unreleased_changelog_example.md"
        expeced_changelog = Path(
            test_directory + "expected_changelog.md"
        ).read_text(encoding="utf-8")
        expeced_release_notes = Path(
            test_directory + "expected_release_notes.md"
        ).read_text(encoding="utf-8")
        expeced_changelog = expeced_changelog.format(date.today().isoformat())
        expeced_release_notes = expeced_release_notes.format(
            date.today().isoformat()
        )

        test_md = Path(path).read_text(encoding="utf-8")
        updated, release_notes = changelog.update(test_md, "1.2.3", "hidden")
        self.assertEqual(expeced_changelog, updated)
        self.assertEqual(expeced_release_notes, release_notes)

    def test_markdown_empty_updated_and_changelog_on_no_unreleased(self):
        test_md = """
# Changelog
something, somehing
- unreleased
- not unreleased
## 1.0.0
### added
- cool stuff 1
- cool stuff 2
"""
        updated, release_notes = changelog.update(test_md, "1.2.3", "hidden")
        self.assertIs("", updated)
        self.assertIs("", release_notes)

    def test_update_markdown_return_changelog_when_only_unreleased(self):
        released = f"""
## [1.2.3] - {date.today().isoformat()}
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
[1.2.3]: https://github.com/greenbone/pontos/compare/v1.0.0...v1.2.3"""

        unreleased = """
## [Unreleased]
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...main"""

        test_md = unreleased
        released_md = released
        updated, release_notes = changelog.update(test_md, "1.2.3")
        self.assertEqual(released_md.strip(), updated.strip())
        self.assertEqual(released.strip(), release_notes.strip())

    def test_update_markdown_different_unreleased_sections(self):
        released_md = f"""
## [1.2.4] (Unreleased)
### fixed
not so much
### added
so little
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...main

## [1.2.3] - {date.today().isoformat()}
### fixed
so much wow
### added
so little
### changed
I don't recognize it anymore
[1.2.3]: https://github.com/greenbone/pontos/compare/v1.0.0...v1.2.3
"""

        unreleased = """
## [1.2.4] (Unreleased)
### fixed
not so much
### added
so little
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...main

## [1.2.3] (Unreleased)
### fixed
so much wow
### added
so little
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...main
"""

        released = f"""
## [1.2.3] - {date.today().isoformat()}
### fixed
so much wow
### added
so little
### changed
I don't recognize it anymore
[1.2.3]: https://github.com/greenbone/pontos/compare/v1.0.0...v1.2.3
"""

        test_md = unreleased
        updated, release_notes = changelog.update(
            test_md, "1.2.3", containing_version="1.2.3"
        )
        self.assertEqual(released_md.strip(), updated.strip())
        self.assertEqual(released.strip(), release_notes.strip())

    def test_update_markdown_return_changelog(self):
        released = f"""
## [1.2.3] - {date.today().isoformat()}
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
[1.2.3]: https://github.com/greenbone/pontos/compare/v1.0.0...v1.2.3"""

        unreleased = """
## [Unreleased]
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...main"""
        test_md_template = """# Changelog
something, somehing
- unreleased
- not unreleased
{}

## 1.0.0
### added
- cool stuff 1
- cool stuff 2"""
        test_md = test_md_template.format(unreleased)
        released_md = test_md_template.format(released)
        updated, release_notes = changelog.update(test_md, "1.2.3")
        self.assertEqual(released_md.strip(), updated.strip())
        self.assertEqual(released.strip(), release_notes.strip())

    def test_identify_heading_abort_condition_correctly(self):
        released = f"""
## [1.2.3] - {date.today().isoformat()}
### fixed
so much
### added
so little
* Added support for GMP 20.08 [#254](https://github.com/greenbone/python-gvm/pull/254)
### changed
I don't recognize it anymore
[1.2.3]: https://github.com/greenbone/pontos/compare/v1.0.0...v1.2.3"""

        unreleased = """
## [Unreleased]
### fixed
so much
### added
so little
* Added support for GMP 20.08 [#254](https://github.com/greenbone/python-gvm/pull/254)
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...HEAD"""
        test_md_template = """# Changelog
something, somehing
- unreleased
- not unreleased
{}

## 1.0.0
### added
- cool stuff 1
- cool stuff 2"""
        test_md = test_md_template.format(unreleased)
        released_md = test_md_template.format(released)
        updated, release_notes = changelog.update(test_md, "1.2.3")
        self.assertEqual(released_md.strip(), updated.strip())
        self.assertEqual(released.strip(), release_notes.strip())

    def test_add_skeleton_adds_keep_a_changelog_skeleton_before_version(self):
        keep_a_changelog_skeleton = """
## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed

[Unreleased]: https://github.com/greenbone/hidden/compare/v1.2.3...HEAD

"""
        released = f"""
## [1.2.3] - {date.today().isoformat()}
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
### security
[1.2.3]: https://github.com/greenbone/pontos/compare/v1.0.0...v1.2.3"""

        test_md_template = """# Changelog
something, somehing
- unreleased
- not unreleased
{}
## 1.0.0
### added
- cool stuff 1
- cool stuff 2"""
        test_md = test_md_template.format(released)
        released_md = test_md_template.format(
            keep_a_changelog_skeleton + released
        )
        updated = changelog.add_skeleton(test_md, "1.2.3", "hidden")
        self.assertEqual(released_md.strip(), updated.strip())
