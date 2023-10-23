# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from typing import Optional

from pontos.github.models.base import GitHubModel


@dataclass
class ActionsMinutesUsedBreakdown(GitHubModel):
    """
    Attributes:
        UBUNTU: Total minutes used on Ubuntu runner machines
        MACOS: Total minutes used on macOS runner machines
        WINDOWS: Total minutes used on Windows runner machines
        total: Total minutes used on all runner machines
    """

    UBUNTU: Optional[int] = None
    MACOS: Optional[int] = None
    WINDOWS: Optional[int] = None
    total: Optional[int] = None


@dataclass
class ActionsBilling(GitHubModel):
    """
    Billing Information for using GitHub Actions

    Attributes:
        total_minutes_used: The sum of the free and paid GitHub Actions minutes
            used
        total_paid_minutes_used: The total paid GitHub Actions minutes used
        included_minutes: The amount of free GitHub Actions minutes available
        minutes_used_breakdown:
    """

    total_minutes_used: int
    total_paid_minutes_used: int
    included_minutes: int
    minutes_used_breakdown: ActionsMinutesUsedBreakdown


@dataclass
class PackagesBilling(GitHubModel):
    """
    Billing Information for using GitHub Packages

    Attributes:
        total_gigabytes_bandwidth_used: Sum of the free and paid storage space
            (GB) for GitHub Packages
        total_paid_gigabytes_bandwidth_used: Total paid storage space (GB) for
            GitHub Packages
        included_gigabytes_bandwidth: Free storage space (GB) for GitHub
            Packages
    """

    total_gigabytes_bandwidth_used: int
    total_paid_gigabytes_bandwidth_used: int
    included_gigabytes_bandwidth: int


@dataclass
class StorageBilling(GitHubModel):
    """
    Billing Information for using GitHub storage

    Attributes:
        days_left_in_billing_cycle: Numbers of days left in billing cycle
        estimated_paid_storage_for_month: Estimated storage space (GB) used in
            billing cycle
        estimated_storage_for_month: Estimated sum of free and paid storage
            space (GB) used in billing cycle
    """

    days_left_in_billing_cycle: int
    estimated_paid_storage_for_month: int
    estimated_storage_for_month: int
