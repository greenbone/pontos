# Copyright (C) 2023 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

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
VERSIONING_SCHEMES: dict[str, type[VersioningScheme]] = {
    "pep440": PEP440VersioningScheme,
    "semver": SemanticVersioningScheme,
}


def versioning_scheme_argument_type(value: str) -> type[VersioningScheme]:
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
