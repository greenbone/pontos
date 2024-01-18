# SPDX-FileCopyrightText: 2021-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import Iterator, Optional

from pontos.git import DEFAULT_TAG_SORT_SUFFIX, Git, TagSort

from ._errors import VersionError
from ._version import ParseVersionFuncType, Version


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

        try:
            version = parse_version(last_release_version)
        except VersionError:
            # be safe and ignore invalid versions
            continue

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
