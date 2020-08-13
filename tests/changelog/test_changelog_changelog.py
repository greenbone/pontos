import unittest
from pontos import changelog


class ChangelogTestCase(unittest.TestCase):
    def test_return_none_when_no_unreleased_information_found(self):
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
        _, cl = changelog.update(test_md, '', '')
        self.assertEqual(cl, '')

    def test_find_unreleased_information_before_another_version(self):
        unreleased = """
## Unreleased
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
### security



     



[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...master 
"""
        test_md = """
# Changelog
something, somehing
- unreleased
- not unreleased
{}
## 1.0.0
### added
- cool stuff 1
- cool stuff 2
        """.format(
            unreleased
        )
        changed = """
## Unreleased
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...master 
"""

        _, result = changelog.update(test_md, '', '')
        self.assertEqual(result.strip(), changed.strip())


def test_find_unreleased_information_no_other_version(self):
    unreleased = """
## Unreleased
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...master 
"""
    test_md = """
{}
        """.format(
        unreleased
    )
    _, result = changelog.update(test_md, '', '')
    self.assertEqual(result.strip(), unreleased.strip())


def test_find_unreleased_information_before_after_another_version(self):
    unreleased = """
## Unreleased
### fixed
so much
### added
so little
### changed
I don't recognize it anymore
### security
[Unreleased]: https://github.com/greenbone/pontos/compare/v1.0.0...master 
"""
    test_md = """
# Changelog
something, somehing
- unreleased
- not unreleased
## 1.0.0
### added
- cool stuff 1
- cool stuff 2
{}
        """.format(
        unreleased
    )
    _, result = changelog.update(test_md, '', '')
    self.assertEqual(result.strip(), unreleased.strip())
