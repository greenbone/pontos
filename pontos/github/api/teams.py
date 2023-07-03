# Copyright (C) 2022 Greenbone AG
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

from typing import Any, AsyncIterator, Dict, Iterable, Optional, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.base import (
    Permission,
    Team,
    TeamPrivacy,
    TeamRole,
    User,
)
from pontos.github.models.organization import Repository
from pontos.helper import enum_or_value


class GitHubAsyncRESTTeams(GitHubAsyncREST):
    async def get_all(self, organization: str) -> AsyncIterator[Team]:
        """
        Get information about teams of an organization.

        https://docs.github.com/en/rest/teams/teams#list-teams

        Args:
            organization: GitHub organization to use

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            An async iterator yielding teams

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for team in api.teams.get_all("foo"):
                        print(team)
        """
        api = f"/orgs/{organization}/teams"
        params = {
            "per_page": "100",
        }

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for team in response.json():
                yield Team.from_dict(team)

    async def create(
        self,
        organization: str,
        name: str,
        *,
        description: Optional[str] = None,
        maintainers: Optional[Iterable[str]] = None,
        repo_names: Optional[Iterable[str]] = None,
        privacy: Union[TeamPrivacy, str, None] = None,
        parent_team_id: Optional[str] = None,
    ) -> Team:
        # pylint: disable=line-too-long
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
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            A new team

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    team = await api.teams.create("foo", "devops")
                    print(team)
        """  # noqa: E501
        api = f"/orgs/{organization}/teams"
        data: Dict[str, Any] = {"name": name}
        if description:
            data["description"] = description
        if maintainers:
            data["maintainers"] = list(maintainers)
        if repo_names:
            data["repo_names"] = list(repo_names)
        if privacy:
            data["privacy"] = enum_or_value(privacy)
        if parent_team_id:
            data["parent_team_id"] = parent_team_id

        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return Team.from_dict(response.json())

    async def get(
        self,
        organization: str,
        team: str,
    ) -> Team:
        """
        Gets a team using the team's slug. GitHub generates the slug from the
        team name.

        https://docs.github.com/en/rest/teams/teams#get-a-team-by-name

        Args:
            organization: GitHub organization to use
            team: The team slug of the team.

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            Information about the team

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    team = await api.teams.get("foo", "devops")
                    print(team)
        """
        api = f"/orgs/{organization}/teams/{team}"
        response = await self._client.get(api)
        response.raise_for_status()
        return Team.from_dict(response.json())

    async def update(
        self,
        organization: str,
        team: str,
        *,
        name: str,
        description: Optional[str] = None,
        privacy: Union[TeamPrivacy, str, None] = None,
        parent_team_id: Optional[str] = None,
    ) -> Team:
        # pylint: disable=line-too-long
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
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            The updated team

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    team = await api.teams.update(
                        "foo", "devops", name="DevSecOps"
                    )
        """  # noqa: E501
        api = f"/orgs/{organization}/teams/{team}"
        data: Dict[str, Any] = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if privacy:
            data["privacy"] = enum_or_value(privacy)
        if parent_team_id:
            data["parent_team_id"] = parent_team_id

        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return Team.from_dict(response.json())

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
            `httpx.HTTPStatusError`: If there was an error in the request

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    await api.teams.delete("foo", "bar")
        """
        api = f"/orgs/{organization}/teams/{team}"
        response = await self._client.delete(api)
        response.raise_for_status()

    async def members(
        self,
        organization: str,
        team: str,
    ) -> AsyncIterator[User]:
        """
        Get all members of a team. Team members will include the members of
        child teams.

        https://docs.github.com/en/rest/teams/members#list-team-members

        Args:
            organization: GitHub organization to use
            team: The slug of the team name.

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            An async iterator yielding users

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for user in api.teams.members("foo", "bar):
                        print(user)
        """
        api = f"/orgs/{organization}/teams/{team}/members"
        params = {
            "per_page": "100",
        }

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for member in response.json():
                yield User.from_dict(member)

    async def update_member(
        self,
        organization: str,
        team: str,
        username: str,
        *,
        role: Union[TeamRole, str] = TeamRole.MEMBER,
    ) -> None:
        """
        Add or update a member of a team.

        https://docs.github.com/en/rest/teams/members#add-or-update-team-membership-for-a-user

        Args:
            organization: GitHub organization to use
            team: The slug of the team name.
            username: The handle for the GitHub user account.
            role: The role that this user should have in the team.
                Default: member. Can be one of: member, maintainer.

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi
                from pontos.github.models import TeamRole

                async with GitHubAsyncRESTApi(token) as api:
                    await api.teams.update_member(
                        "foo",
                        "bar",
                        "a_user",
                        role=TeamRole.MAINTAINER,
                    )
        """
        api = f"/orgs/{organization}/teams/{team}/memberships/{username}"
        data: Dict[str, Any] = {"role": enum_or_value(role)}
        response = await self._client.put(api, data=data)
        response.raise_for_status()

    # add_member is the same API as update_member
    add_member = update_member

    async def remove_member(
        self,
        organization: str,
        team: str,
        username: str,
    ) -> None:
        """
        Remove a member from a team.

        https://docs.github.com/en/rest/teams/members#remove-team-membership-for-a-user

        Args:
            organization: GitHub organization to use
            team: The slug of the team name.
            username: The handle for the GitHub user account.

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi
                from pontos.github.models import TeamRole

                async with GitHubAsyncRESTApi(token) as api:
                    await api.teams.remove_member(
                        "foo",
                        "bar",
                        "a_user",
                    )
        """
        api = f"/orgs/{organization}/teams/{team}/memberships/{username}"
        response = await self._client.delete(api)
        response.raise_for_status()

    async def repositories(
        self,
        organization: str,
        team: str,
    ) -> AsyncIterator[Repository]:
        """
        Lists a team's repositories visible to the authenticated user.

        https://docs.github.com/en/rest/teams/teams#list-team-repositories

        Args:
            organization: GitHub organization to use
            team: The slug of the team name.

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Returns:
            An async iterator yielding repositories

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for repo in api.teams.repositories("foo", "bar"):
                        print(repo)
        """
        api = f"/orgs/{organization}/teams/{team}/repos"
        params = {
            "per_page": "100",
        }

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for repo in response.json():
                yield Repository.from_dict(repo)

    async def update_permission(
        self,
        organization: str,
        team: str,
        repository: str,
        permission: Union[Permission, str],
    ) -> None:
        """
        Add or update team repository permissions

        Args:
            organization: GitHub organization to use
            team: The slug of the team name.
            repository: GitHub repository (only name) to add or change
                permissions on.
            permission: The permission to grant the team on the repository.

        Raises:
            `httpx.HTTPStatusError`: If there was an error in the request

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi
                from pontos.github.models import Permission

                async with GitHubAsyncRESTApi(token) as api:
                    await api.teams.update_permission(
                        "foo",
                        "bar",
                        "baz",
                        Permission.MAINTAIN,
                    )
        """
        api = (
            f"/orgs/{organization}/teams/{team}/repos/{organization}/"
            f"{repository}"
        )
        data: Dict[str, Any] = {"permission": enum_or_value(permission)}
        response = await self._client.put(api, data=data)
        response.raise_for_status()

    add_permission = update_permission
