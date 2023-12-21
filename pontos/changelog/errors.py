# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from pontos.errors import PontosError


class ChangelogError(PontosError):
    """
    Some error has occurred during changelog handling
    """


class ChangelogBuilderError(ChangelogError):
    """
    An error while building a changelog
    """
