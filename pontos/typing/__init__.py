# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class SupportsStr(Protocol):
    """
    A protocol for classes supporting __str__
    """

    @abstractmethod
    def __str__(self) -> str:
        pass
