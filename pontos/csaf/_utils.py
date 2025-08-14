# Copyright (C) 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Dict, Iterable, Optional, Set


def iter_next_branches(
    branch: Dict, limit_to_categories: Optional[Set[str]] = None
) -> Iterable[Dict]:
    for inner_branch in branch.get("branches", []):
        if (
            limit_to_categories
            and inner_branch["category"] not in limit_to_categories
        ):
            continue
        yield inner_branch
