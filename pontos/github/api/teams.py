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

from enum import Enum
from typing import Iterable, Optional

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.helper import JSON_OBJECT


class TeamPrivacy(Enum):
    SECRET = "secret"
    CLOSED = "closed"


class GitHubAsyncRESTTeams(GitHubAsyncREST):
    async def get_all(self, organization: str) -> Iterable[JSON_OBJECT]:
        """
        Get information about teams of an organization.

        https://docs.github.com/en/rest/teams/teams#list-teams

        Args:
            organization: GitHub organization to use

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/teams"
        teams = []
        params = {
            "per_page": "100",
        }

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            teams.extend(response.json())

        return teams

    async def create(
        self,
        organization: str,
        name: str,
        *,
        description: Optional[str] = None,
        maintainers: Optional[Iterable[str]] = None,
        repo_names: Optional[Iterable[str]] = None,
        privacy: Optional[TeamPrivacy] = None,
        parent_team_id: Optional[str] = None,
    ) -> JSON_OBJECT:
        """
        Create a new team in an organization

        https://docs.github.com/en/rest/teams/teams#create-a-team

        Args:
            organization: GitHub organization to use
            name: The name of the new team.
            description: The description of the team.
            maintainers: List GitHub IDs for organization members who will
                become team maintainers.
            repo_names: The full name (e.g., "organization-name/repository-name"
                ) of repositories to add the team to.
            privacy: The level of privacy this team should have. The options
                are:
                For a non-nested team:
                    * secret - only visible to organization owners and members
                        of this team.
                    * closed - visible to all members of this organization.
                Default: secret

                For a parent or child team:
                    * closed - visible to all members of this organization.
                Default for child team: closed
            parent_team_id: The ID of a team to set as the parent team.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/teams"
        data = {"name": name}
        if description:
            data["description"] = description
        if maintainers:
            data["maintainers"] = list(maintainers)
        if repo_names:
            data["repo_names"] = list(repo_names)
        if privacy:
            data["privacy"] = privacy.value
        if parent_team_id:
            data["parent_team_id"] = parent_team_id

        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return response.json()

    async def get(
        self,
        organization: str,
        team: str,
    ) -> JSON_OBJECT:
        """
        Gets a team using the team's slug. GitHub generates the slug from the
        team name.

        https://docs.github.com/en/rest/teams/teams#get-a-team-by-name

        Args:
            organization: GitHub organization to use
            team: The team slug of the team.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/teams/{team}"
        response = await self._client.get(api)
        response.raise_for_status()
        return response.json()

    async def update(
        self,
        organization: str,
        team: str,
        *,
        name: str,
        description: Optional[str] = None,
        privacy: Optional[TeamPrivacy] = None,
        parent_team_id: Optional[str] = None,
    ) -> JSON_OBJECT:
        """
        Update team information in an organization

        https://docs.github.com/en/rest/teams/teams#update-a-team

        Args:
            organization: GitHub organization to use
            team: The slug of the team name.
            name: The name of the team.
            description: The description of the team.
            privacy: The level of privacy this team should have. The options
                are:
                For a non-nested team:
                    * secret - only visible to organization owners and members
                        of this team.
                    * closed - visible to all members of this organization.
                Default: secret

                For a parent or child team:
                    * closed - visible to all members of this organization.
                Default for child team: closed
            parent_team_id: The ID of a team to set as the parent team.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/teams/{team}"
        data = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if privacy:
            data["privacy"] = privacy.value
        if parent_team_id:
            data["parent_team_id"] = parent_team_id

        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return response.json()

    async def delete(
        self,
        organization: str,
        team: str,
    ) -> None:
        """
        Delete a new team of an organization

        https://docs.github.com/en/rest/teams/teams#delete-a-team

        Args:
            organization: GitHub organization to use
            team: The slug of the team name.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/teams/{team}"
        response = await self._client.delete(api)
        response.raise_for_status()

    async def members(
        self,
        organization: str,
        team: str,
    ) -> Iterable[JSON_OBJECT]:
        """
        Get all members of a team. Team members will include the members of
        child teams.

        https://docs.github.com/en/rest/teams/members#list-team-members

        Args:
            organization: GitHub organization to use
            team: The slug of the team name.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/teams/{team}/members"
        members = []
        params = {
            "per_page": "100",
        }

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            members.extend(response.json())

        return members
