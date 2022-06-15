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


import re
from datetime import date
from typing import List, Tuple


class ChangelogError(Exception):
    """
    Some error has occurred during changelog handling
    """


__UNRELEASED_FOOTER_MATCHER = re.compile("unreleased", re.IGNORECASE)
__UNRELEASED_HEADER_MATCHER = re.compile(
    r"[\(\[]{1}[0-9\.]*.*?[Uu]nreleased[\)\]]{1}"
)
__MASTER_MATCHER = re.compile("master|main|HEAD")

__UNRELEASED_SKELETON = """## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed

[Unreleased]: https://github.com/{}/{}/compare/{}...HEAD


"""


def add_skeleton(
    markdown: str,
    new_version: str,
    project_name: str,
    git_tag_prefix: str = "v",
    git_space: str = "greenbone",
) -> str:
    git_tag = f"{git_tag_prefix}{new_version}"
    tokens = _tokenize(markdown)
    updated_markdown = ""

    for tt, _, tc in tokens:
        if tt == "heading" and new_version in tc:
            prepared_skeleton = __UNRELEASED_SKELETON.format(
                git_space, project_name, git_tag
            )
            updated_markdown += prepared_skeleton + tc
        else:
            updated_markdown += tc

    return updated_markdown


def update(
    markdown: str,
    new_version: str,
    git_tag_prefix: str = "v",
    containing_version: str = None,
) -> Tuple[str, str]:
    """
    update tokenizes CHANGELOG.md and if a version is given it changes
    unreleased headline and link to given version.

    returns updated markdown and change log for further processing.
    """

    git_tag = f"{git_tag_prefix}{new_version}"
    tokens = _tokenize(markdown)
    unreleased_heading_count = 0
    changelog = ""
    updated_markdown = ""
    current_state = []
    previous_state = []
    unreleased = []

    for tt, hc, tc in tokens:
        previous_state = current_state.copy()

        if tt == "unreleased":
            if (
                containing_version and containing_version in tc
            ) or not containing_version:
                unreleased_heading_count = hc
                current_state = [tt]
        elif (
            tt == "heading"
            and unreleased_heading_count > 0
            and hc <= unreleased_heading_count
        ):
            current_state = []

        if "unreleased" not in current_state and "unreleased" in previous_state:
            changelog = _prepare_changelog(unreleased, new_version, git_tag)
            updated_markdown += changelog

        if "unreleased" not in current_state:
            updated_markdown += tc

        if "unreleased" in current_state:
            unreleased.append((tt, hc, tc))

    if "unreleased" in current_state and unreleased:
        changelog = _prepare_changelog(unreleased, new_version, git_tag)
        updated_markdown += changelog

    return (
        updated_markdown if changelog else "",
        changelog,
    )


def _prepare_changelog(
    tokens: List[Tuple[str, int, str]], new_version: str, git_tag: str
) -> str:
    current = ""
    previous = ""
    output = ""
    keyword_text = ""
    unreleased_link = ""

    for tt, _, tc in tokens:
        previous = current

        if tt == "unreleased":
            if new_version:
                tc = __UNRELEASED_HEADER_MATCHER.sub(f"[{new_version}]", tc)
                tc += f" - {date.today().isoformat()}"
            output += tc
        elif tt == "unreleased_link":
            if new_version:
                tc = __UNRELEASED_FOOTER_MATCHER.sub(new_version, tc)
                tc = __MASTER_MATCHER.sub(git_tag, tc)
            unreleased_link += tc + "\n\n"
        elif "kw_" in tt:
            if keyword_text.strip().count("\n") > 0:
                output += keyword_text
            keyword_text = tc
            current = tt
        elif "kw_" in previous:
            keyword_text += tc
        else:
            output += tc

    if keyword_text.strip().count("\n") > 0:
        output += keyword_text.strip() + "\n\n"

    output += unreleased_link

    return output


def __build_scanner():
    def token_handler(key: str):
        """
        generates a lambda for the regex scanner with a given key.

        This lambda will return a tuple: key, count # of token and token.

        The count is used to identify the level of heading on a special
        ended which can be used to identify when this section ended.
        """
        return lambda _, token: (key, token.count("#"), token)

    return re.Scanner(
        [
            (r"#{1,} [Aa]dded", token_handler("kw_added")),
            (r"#{1,} [Cc]hanged", token_handler("kw_changed")),
            (r"#{1,} [Dd]eprecated", token_handler("kw_deprecated")),
            (r"#{1,} [Rr]emoved", token_handler("kw_removed")),
            (r"#{1,} [Ff]ixed", token_handler("kw_fixed")),
            (r"#{1,} [Ss]ecurity", token_handler("kw_security")),
            (r"#{1,}.*(?=[Uu]nreleased).*", token_handler("unreleased")),
            (
                r"\[[Uu]nreleased\].*",
                token_handler("unreleased_link"),
            ),
            (r"#{1,} .*", token_handler("heading")),
            (r"\n", token_handler("newline")),
            (r"..*", token_handler("any")),
        ]
    )


__CHANGELOG_SCANNER = __build_scanner()


def _tokenize(
    markdown: str,
) -> List[Tuple[int, str, int, str],]:
    toks, remainder = __CHANGELOG_SCANNER.scan(markdown)
    if remainder != "":
        raise ChangelogError(f"unrecognized tokens in markdown: {remainder}")

    return toks
