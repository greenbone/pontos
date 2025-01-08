# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pontos.models import Model


@dataclass
class CPEMatch(Model):
    """
    Represents a single CPE match.

    Attributes:
        cpe_name: Name of the matching CPE
        cpe_name_id: Name ID of the matching CPE
    """

    cpe_name: str
    cpe_name_id: UUID


@dataclass
class CPEMatchString(Model):
    """
    Represents a CPE match string, matching criteria to one or more CPEs

    Attributes:
        match_criteria_id: The identifier of the CPE match
        criteria: The CPE formatted match criteria
        version_start_including: Optional start of the matching version range, including the given version
        version_start_excluding: Optional start of the matching version range, excluding the given version
        version_end_including: Optional end of the matching version range, including the given version
        version_end_excluding: Optional end of the matching version range, excluding the given version
        status: Status of the CPE match
        cpe_last_modified: Optional date the CPEs list of the match was last modified
        created: Creation date of the CPE
        last_modified: Last modification date of the CPE
        matches: List of CPEs matching the criteria string and the optional range limits
    """

    match_criteria_id: UUID
    criteria: str
    status: str
    created: datetime
    last_modified: datetime
    cpe_last_modified: Optional[datetime] = None
    matches: List[CPEMatch] = field(default_factory=list)
    version_start_including: Optional[str] = None
    version_start_excluding: Optional[str] = None
    version_end_including: Optional[str] = None
    version_end_excluding: Optional[str] = None

    @classmethod
    def from_dict_with_cache(
        cls,
        data: dict[str, Any],
        cpe_match_cache: dict[str, CPEMatch],
    ):
        """
        Create a CPEMatchString model from a dict, reusing
        duplicate CPEMatch objects to reduce memory usage if a cache
        dict is given.

        Args:
            data: The JSON dict to generate the model from
            cpe_match_cache: A dictionary to store CPE matches or None
                to not cache and reused CPE matches
        """
        new_match_string = cls.from_dict(data)

        for i, match in enumerate(new_match_string.matches):
            cached_match: Optional[CPEMatch] = cpe_match_cache.get(
                match.cpe_name_id
            )
            if cached_match and cached_match.cpe_name == match.cpe_name:
                new_match_string.matches[i] = cached_match
            else:
                cpe_match_cache[match.cpe_name_id] = match
        return new_match_string
