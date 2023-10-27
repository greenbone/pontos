# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ._cpe import ANY, CPE, NA, CPEParsingError, Part

"""
Module for parsing and handling Common Platform Enumeration (CPE) information
"""

__all__ = (
    "ANY",
    "NA",
    "CPEParsingError",
    "Part",
    "CPE",
)
