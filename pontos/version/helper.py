# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Greenbone AG
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
#

from typing import Iterator, Optional

from pontos.git import Git, TagSort
from pontos.git.git import DEFAULT_TAG_SORT_SUFFIX

from .version import ParseVersionFuncType, Version


def get_last_release_versions(
    parse_version: ParseVersionFuncType,
    *,
    git_tag_prefix: Optional[str] = "",
    ignore_pre_releases: Optional[bool] = False,
    tag_name: Optional[str] = None,
) -> Iterator[Version]:
    """Get the last released Versions from git.

    Args:
        git_tag_prefix: Git tag prefix to consider
        ignore_pre_release: Ignore pre releases and only consider non pre
            releases. Default is False.
        tag_name: A pattern for filtering the tags. For example: "1.2.*"

    Returns:
        List of released versions
    """

    tag_list = Git().list_tags(
        sort=TagSort.VERSION,
        sort_suffix=DEFAULT_TAG_SORT_SUFFIX,
        tag_name=tag_name,
    )
    tag_list.reverse()

    for tag in tag_list:
        last_release_version = tag.strip(git_tag_prefix)

        version = parse_version(last_release_version)
        if version.is_pre_release and ignore_pre_releases:
            continue

        yield version


def get_last_release_version(
    parse_version: ParseVersionFuncType,
    *,
    git_tag_prefix: Optional[str] = "",
    ignore_pre_releases: Optional[bool] = False,
    tag_name: Optional[str] = None,
) -> Optional[Version]:
    """Get the last released Version from git.

    Args:
        git_tag_prefix: Git tag prefix to consider
        ignore_pre_release: Ignore pre releases and only consider non pre
            releases. Default is False.
        tag_name: A pattern for filtering the tags. For example: "1.2.*"

    Returns:
        Last released git tag as Version if tags were found
        or None
    """

    it = get_last_release_versions(
        parse_version=parse_version,
        git_tag_prefix=git_tag_prefix,
        ignore_pre_releases=ignore_pre_releases,
        tag_name=tag_name,
    )

    try:
        return next(it)
    except StopIteration:
        return None
