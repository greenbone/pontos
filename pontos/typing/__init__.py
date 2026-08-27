# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import sys
from abc import abstractmethod
from typing import Protocol, runtime_checkable

__all__ = (
    "Self",
    "SupportsStr",
    "override",
)


@runtime_checkable
class SupportsStr(Protocol):
    """
    A protocol for classes supporting __str__
    """

    @abstractmethod
    def __str__(self) -> str:
        pass


if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
