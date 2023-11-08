# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

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


def get_cpe_data(update: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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


def get_cve_change_data(
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    cve_changes = {
        "cve_id": "CVE-2022-0001",
        "event_name": "Initial Analysis",
        "cve_change_id": "5160FDEB-0FF0-457B-AA36-0AEDCAB2522E",
        "source_identifier": "nvd@nist.gov",
        "created": "2022-03-18T20:13:08.123",
        "details": [
            {
                "action": "Added",
                "type": "CVSS V2",
                "new_value": "NIST (AV:L/AC:L/Au:N/C:P/I:N/A:N)",
            },
            {
                "action": "Added",
                "type": "CVSS V3.1",
                "new_value": "NIST AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N",
            },
            {
                "action": "Changed",
                "type": "Reference Type",
                "old_value": "http://www.openwall.com/lists/oss-security/2022/03/18/2 No Types Assigned",
                "new_value": "http://www.openwall.com/lists/oss-security/2022/03/18/2 Mailing List, Third Party Advisory",
            },
        ],
    }

    if data:
        cve_changes.update(data)
    return cve_changes
