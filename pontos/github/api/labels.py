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


from typing import List

import httpx


class GitHubRESTLabelsMixin:
    def get_labels(
        self,
        repo: str,
        issue: int,
    ) -> List[str]:
        """
        Get all labels that are set in the issue/pr

        Args:
            repo:   GitHub repository (owner/name) to use
            issue:  Issue/Pull request number

        Returns:
            List of existing labels
        """
        api = f"/repos/{repo}/issues/{issue}/labels"
        response: httpx.Response = self._request(api)
        return [f["name"] for f in response.json()]

    def set_labels(self, repo: str, issue: int, labels: List[str]):
        """
        Set labels in the issue/pr. Existing labels will be overwritten

        Args:
            repo:   GitHub repository (owner/name) to use
            issue:  Issue/Pull request number
            labels: List of labels, that should be set.
                    Existing labels will be overwritten
        """
        api = f"/repos/{repo}/issues/{issue}/labels"
        data = {"labels": labels}
        response: httpx.Response = self._request(
            api, data=data, request=httpx.post
        )
        response.raise_for_status()
