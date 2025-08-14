# Copyright (C) 2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later


class Revision(dict):
    # Defined in 3.2.1.12.6
    # shall only exist for non-pre-release document states
    @property
    def date(self) -> "date":
        # string; format date-time
        return self["date"]

    @property
    def number(self) -> int:
        # version_t type
        # must not be '0' or '0.x.y' for any document
        # in the final state
        return self["number"]

    @property
    def summary(self) -> str:
        return self["summary"]

    @property
    def legacy_version(self):
        # designed to refer to version numbers of the human-readable
        # equivalent SA
        return self["legacy_version"]
