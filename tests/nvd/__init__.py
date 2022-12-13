# Copyright (C) 2022 Greenbone Networks GmbH
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

# pylint: disable=line-too-long

from typing import Any, Dict, Optional


def get_cve_data(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cve = {
        "id": "CVE-2022-45536",
        "source_identifier": "cve@mitre.org",
        "published": "2022-11-22T21:15:11.103",
        "last_modified": "2022-11-23T16:02:07.367",
        "vuln_status": "Analyzed",
        "descriptions": [
            {
                "lang": "en",
                "value": "AeroCMS v0.0.1 was discovered to contain a SQL "
                "Injection vulnerability via the id parameter at "
                "\\admin\\post_comments.php. This vulnerability allows "
                "attackers to access database information.",
            }
        ],
        "references": [
            {
                "url": "https://github.com/rdyx0/CVE/blob/master/AeroCMS/AeroCMS-v0.0.1-SQLi/post_comments_sql_injection/post_comments_sql_injection.md",
                "source": "cve@mitre.org",
                "tags": ["Exploit", "Third Party Advisory"],
            },
            {
                "url": "https://rdyx0.github.io/2018/09/07/AeroCMS-v0.0.1-SQLi%20post_comments_sql_injection/",
                "source": "cve@mitre.org",
                "tags": ["Exploit", "Third Party Advisory"],
            },
        ],
    }
    if data:
        cve.update(data)
    return cve


def get_cpe_data(update: Dict[str, Any] = None) -> Dict[str, Any]:
    data = {
        "deprecated": False,
        "cpe_name": "cpe:2.3:o:microsoft:windows_10_22h2:-:*:*:*:*:*:arm64:*",
        "cpe_name_id": "9BAECDB2-614D-4E9C-9936-190C30246F03",
        "last_modified": "2022-12-09T18:15:16.973",
        "created": "2022-12-09T16:20:06.943",
    }

    if update:
        data.update(update)
    return data
