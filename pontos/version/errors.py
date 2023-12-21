# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


from pontos.errors import PontosError


class VersionError(PontosError):
    """
    Some error has occurred during version handling
    """


class ProjectError(PontosError):
    """
    An error has occured while gathering a project
    """
