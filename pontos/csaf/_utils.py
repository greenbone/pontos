# Copyright (C) 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any, Container, Dict, Iterable, Optional


def iter_next_branches(
    branch: Dict[str, Any], limit_to_categories: Optional[Container[str]] = None
) -> Iterable[Dict[str, Any]]:
    for inner_branch in branch.get("branches", []):
        if (
            limit_to_categories is not None
            and inner_branch["category"] not in limit_to_categories
        ):
            continue
        yield inner_branch
