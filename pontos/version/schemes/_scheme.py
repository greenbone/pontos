# Copyright (C) 2023 Greenbone Networks GmbH
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

from abc import ABC
from typing import Type

from .._calculator import VersionCalculator
from ..version import Version


class VersioningScheme(ABC):
    """
    An abstract base class for versioning schemes

    Example:
        Example on how to implement a new VersioningScheme

        .. code-block:: python

            from pontos.version.scheme import VersioningScheme

            class MyVersioningScheme(VersioningScheme):
                version_cls = MyVersion
                version_calculator_cls = MyVersionCalculator
    """

    version_cls: Type[Version]
    version_calculator_cls: Type[VersionCalculator]
    name: str

    @classmethod
    def parse_version(cls, version: str) -> Version:
        """
        Parse a version from a version string

        Raises:
            :py:class:`pontos.version.error.VersionError`: If the version
                string contains an invalid version

        Returns:
            A version instance
        """
        return cls.version_cls.from_string(version)

    @classmethod
    def from_version(cls, version: Version) -> Version:
        return cls.version_cls.from_version(version)

    @classmethod
    def calculator(cls) -> Type[VersionCalculator]:
        """
        Return a matching version calculator for the implemented versioning
        schema.

        Returns:
            A version calculator
        """
        return cls.version_calculator_cls
