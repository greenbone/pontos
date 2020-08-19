from datetime import date
from pathlib import Path
import unittest

from pontos import changelog


class ChangelogUpdateTestCase(unittest.TestCase):
    def test_markdown_based_on_example(self):
        own_path = Path(__file__).absolute()
        test_directory = own_path.__str__()[0 : (len(own_path.name) * -1)]
        path = test_directory + 'unreleased_changelog_example.md'
        expeced_changelog = Path(
            test_directory + 'expected_changelog.md'
        ).read_text()
        expeced_release_notes = Path(
            test_directory + 'expected_release_notes.md'
        ).read_text()
        expeced_changelog = expeced_changelog.format(date.today().isoformat())
        expeced_release_notes = expeced_release_notes.format(
            date.today().isoformat()
        )

        test_md = Path(path).read_text()
        updated, release_notes = changelog.update(test_md, '1.2.3', 'hidden')
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
        updated, release_notes = changelog.update(test_md, '1.2.3', 'hidden')
        self.assertIs('', updated)
        self.assertIs('', release_notes)

    def test_update_markdown_return_changelog_when_only_unreleased(self):
        released = """
## [1.2.3] - {}
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
[1.2.3]: https://github.com/greenbone/pontos/compare/v1.0.0...v1.2.3""".format(
            date.today().isoformat()
        )

        unreleased = """
## [Unreleased]
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...master"""

        test_md = unreleased
        released_md = released
        updated, release_notes = changelog.update(test_md, '1.2.3')
        self.assertEqual(released_md.strip(), updated.strip())
        self.assertEqual(released.strip(), release_notes.strip())

    def test_update_markdown_return_changelog(self):
        released = """
## [1.2.3] - {}
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
[1.2.3]: https://github.com/greenbone/pontos/compare/v1.0.0...v1.2.3""".format(
            date.today().isoformat()
        )

        unreleased = """
## [Unreleased]
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...master"""
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
        updated, release_notes = changelog.update(test_md, '1.2.3')
        self.assertEqual(released_md.strip(), updated.strip())
        self.assertEqual(released.strip(), release_notes.strip())

    def test_identify_heading_abort_condition_correctly(self):
        released = """
## [1.2.3] - {}
### fixed
so much
### added
so little
* Added support for GMP 20.08 [#254](https://github.com/greenbone/python-gvm/pull/254)
### changed
I don't recognize it anymore
[1.2.3]: https://github.com/greenbone/pontos/compare/v1.0.0...v1.2.3""".format(
            date.today().isoformat()
        )

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
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...master"""
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
        updated, release_notes = changelog.update(test_md, '1.2.3')
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
        released = """
## [1.2.3] - {}
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
### security
[1.2.3]: https://github.com/greenbone/pontos/compare/v1.0.0...v1.2.3""".format(
            date.today().isoformat()
        )

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
        updated = changelog.add_skeleton(test_md, '1.2.3', 'hidden')
        self.assertEqual(released_md.strip(), updated.strip())
