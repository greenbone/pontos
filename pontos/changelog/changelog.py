# Copyright (C) 2020 Greenbone Networks GmbH
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


import re
from typing import Tuple, List
from datetime import date


class ChangelogError(Exception):
    """
    Some error has occurred during changelog handling
    """


__UNRELEASED_MATCHER = re.compile("unreleased", re.IGNORECASE)
__MASTER_MATCHER = re.compile("master")

__UNRELEASED_SKELETON = """## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed

[Unreleased]: https://github.com/{}/{}/compare/{}...HEAD


"""


def update(
    markdown: str,
    new_version: str,
    project_name: str,
    git_tag_prefix: str = 'v',
    git_space: str = 'greenbone',
    containing_version: str = None,
) -> Tuple[str, str]:
    """
    update tokenizes CHANGELOG.md and if a version is given it changes
    unreleased headline and link to given version.

    returns updated markdown and change log for further processing.
    """

    def may_add_skeleton(
        heading_count: int, first_headline_state: int, markdown: str
    ) -> Tuple[int, str]:
        if first_headline_state == -1 and heading_count == 1:
            return 0, markdown
        if first_headline_state == 0 and heading_count > 1:
            prepared_skeleton = __UNRELEASED_SKELETON.format(
                git_space, project_name, git_tag
            )
            return 1, markdown + prepared_skeleton
        return first_headline_state, markdown

    git_tag = "{}{}".format(git_tag_prefix, new_version)
    tokens = _tokenize(markdown)
    hc = 0
    changelog = ""
    updated_markdown = ""
    may_changelog_relevant = True
    first_headline_state = -1  # -1 initial, 0 found, 1 handled

    for tt, heading_count, tc in tokens:
        first_headline_state, updated_markdown = may_add_skeleton(
            heading_count, first_headline_state, updated_markdown
        )
        if tt == 'unreleased':
            if (
                containing_version and containing_version in tc
            ) or not containing_version:
                hc = heading_count
                if new_version:
                    tc = __UNRELEASED_MATCHER.sub(new_version, tc)
                    tc += " - {}".format(date.today().isoformat())
        elif heading_count > 0 and hc > 0 and heading_count <= hc:
            may_changelog_relevant = False
        if tt == 'unreleased_link' and new_version:
            tc = __UNRELEASED_MATCHER.sub(new_version, tc)
            tc = __MASTER_MATCHER.sub(git_tag, tc)

        updated_markdown += tc
        if may_changelog_relevant:
            append_word = hc > 0
            if append_word:
                changelog += tc
    return (
        updated_markdown if changelog else "",
        changelog,
    )


def __build_scanner():
    def token_handler(key: str):
        """
        generates a lambda for the regex scanner with a given key.

        This lambda will return a tuple: key, count # of token and token.

        The count is used to identify the level of heading on a special
        ended which can be used to identify when this section ended.
        """
        return lambda _, token: (key, token.count('#'), token)

    return re.Scanner(
        [
            (r'#{1,} Added', token_handler('added')),
            (r'#{1,} Changed', token_handler("changed")),
            (r'#{1,} Deprecated', token_handler("deprecated")),
            (r'#{1,} Removed', token_handler("removed")),
            (r'#{1,} Fixed', token_handler("fixed")),
            (r'#{1,} Security', token_handler("security")),
            (r'#{1,}.*(?=[Uu]nreleased).*', token_handler("unreleased")),
            (r'\[[Uu]nreleased\].*', token_handler("unreleased_link"),),
            (r'#{1,} .*', token_handler("heading")),
            (r'\n', token_handler("newline")),
            (r'..*', token_handler("any")),
        ]
    )


__CHANGELOG_SCANNER = __build_scanner()


def _tokenize(
    markdown: str,
) -> List[
    Tuple[int, str, int, str],
]:
    toks, remainder = __CHANGELOG_SCANNER.scan(markdown)
    if remainder != '':
        raise ChangelogError(
            "unrecognized tokens in markdown: {}".format(remainder)
        )
    return toks
