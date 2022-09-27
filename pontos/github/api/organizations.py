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


class GitHubRESTOrganizationsMixin:
    def organisation_exists(self, orga: str) -> bool:
        """
        Check if an organization exists

        Args:
            repo: GitHub repository (owner/name) to use
        """
        api = f"/orgs/{orga}"
        response = self._request(api)
        return response.is_success

    def get_organization_repository_number(
        self, orga: str, repository_type: str
    ) -> int:
        """
        Get total number of repositories of organization

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number to check
        """
        api = f"/orgs/{orga}"
        response = self._request(api)
        response.raise_for_status()
        response_json = response.json()

        if repository_type == "ALL":
            return (
                response_json["public_repos"]
                + response_json["total_private_repos"]
            )
        if repository_type == "PUBLIC":
            return response_json["public_repos"]
        if repository_type == "PRIVATE":
            return response_json["total_private_repos"]

    def get_repositories(
        self,
        orga: str,
        repository_type: str,
    ):
        """
        Get information about organization repositories

        Args:
            orga: GitHub organization to use
        """
        api = f"/orgs/{orga}/repos"

        count = self.get_organization_repository_number(
            orga=orga, repository_type=repository_type
        )
        downloaded = 0

        repos = []
        params = {}
        params["type"] = repository_type
        params["per_page"] = 100  # max
        while count - downloaded > 0:
            params["page"] = downloaded / params["per_page"] + 1
            response = self._request(api, params=params)
            downloaded += params["per_page"]
            repos.extend(response.json())
        response.raise_for_status()

        return response.json()
