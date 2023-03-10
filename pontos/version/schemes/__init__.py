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

from argparse import ArgumentTypeError

from ._pep440 import PEP440VersioningScheme
from ._scheme import VersioningScheme
from ._semantic import SemanticVersioningScheme

__all__ = (
    "VERSIONING_SCHEMES",
    "versioning_scheme_argument_type",
    "VersioningScheme",
    "PEP440VersioningScheme",
    "SemanticVersioningScheme",
)

#: Dictionary with available versioning schemes
VERSIONING_SCHEMES = {
    "pep440": PEP440VersioningScheme,
    "semver": SemanticVersioningScheme,
}


def versioning_scheme_argument_type(value: str) -> VersioningScheme:
    """
    Verifies if the passed value is a valid versioning scheme and returns
    the corresponding versioning scheme.

    Intended to be used as in `ArgumentParser.add_argument` as the type.

    Raises:
        ArgumentTypeError: If the passed value is not a valid versioning scheme

    Example:
        .. code-block:: python

            from argparse import ArgumentParser
            from pontos.version.scheme versioning_scheme_argument_type

            parser = ArgumentParser()
            parser.add_argument(
                "--versioning-scheme",
                type=versioning_scheme_argument_type,
            )
    """
    try:
        return VERSIONING_SCHEMES[value]
    except KeyError:
        raise ArgumentTypeError(
            f"invalid value {value}. Expected one of "
            f"{', '.join(VERSIONING_SCHEMES.keys())}."
        ) from None
