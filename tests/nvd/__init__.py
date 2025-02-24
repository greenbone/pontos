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


def get_cpe_match_data(
    update: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    data = {
        "cpe_last_modified": "2019-07-22T16:37:38.133",
        "created": "2019-06-17T09:16:33.960",
        "criteria": "cpe:2.3:a:sun:jre:*:update3:*:*:*:*:*:*",
        "last_modified": "2019-06-17T09:16:44.000",
        "match_criteria_id": "EAB2C9C2-F685-450B-9980-553966FC3B63",
        "matches": [
            {
                "cpe_name": "cpe:2.3:a:sun:jre:1.3.0:update3:*:*:*:*:*:*",
                "cpe_name_id": "2D284534-DA21-43D5-9D89-07F19AE400EA",
            },
            {
                "cpe_name": "cpe:2.3:a:sun:jre:1.4.1:update3:*:*:*:*:*:*",
                "cpe_name_id": "CE55E1DF-8EA2-41EA-9C51-1BAE728CA094",
            },
            {
                "cpe_name": "cpe:2.3:a:sun:jre:1.4.2:update3:*:*:*:*:*:*",
                "cpe_name_id": "A09C4E47-6548-40C5-8458-5C07C3292C86",
            },
            {
                "cpe_name": "cpe:2.3:a:sun:jre:1.5.0:update3:*:*:*:*:*:*",
                "cpe_name_id": "C484A93A-2677-4501-A6E0-E4ADFFFB549E",
            },
            {
                "cpe_name": "cpe:2.3:a:sun:jre:1.6.0:update3:*:*:*:*:*:*",
                "cpe_name_id": "C518A954-369E-453E-8E17-2AF639150115",
            },
        ],
        "status": "Active",
        "version_end_including": "1.6.0",
    }

    if update:
        data.update(update)
    return data


def get_cve_change_data(
    data: Optional[Dict[str, Any]] = None,
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


def get_source_data(
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    sources = {
        "name": "MITRE",
        "contact_email": "cve@mitre.org",
        "source_identifiers": [
            "cve@mitre.org",
            "8254265b-2729-46b6-b9e3-3dfca2d5bfca",
        ],
        "last_modified": "2019-09-09T16:18:45.930",
        "created": "2019-09-09T16:18:45.930",
        "v3_acceptance_level": {
            "description": "Contributor",
            "last_modified": "2025-01-30T00:00:20.107",
        },
        "cwe_acceptance_level": {
            "description": "Reference",
            "last_modified": "2025-01-24T00:00:00.043",
        },
    }

    if data:
        sources.update(data)
    return sources
