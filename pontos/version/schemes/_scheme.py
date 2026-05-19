# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from abc import ABC

from .._calculator import VersionCalculator
from .._version import Version


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

    version_cls: type[Version]
    version_calculator_cls: type[VersionCalculator]
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
    def calculator(cls) -> type[VersionCalculator]:
        """
        Return a matching version calculator for the implemented versioning
        schema.

        Returns:
            A version calculator
        """
        return cls.version_calculator_cls
