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

from typing import AsyncIterator, Iterable, Optional, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.errors import GitHubApiError
from pontos.github.models.base import User
from pontos.github.models.organization import (
    InvitationRole,
    MemberFilter,
    MemberRole,
    Repository,
    RepositoryType,
)
from pontos.helper import enum_or_value


class GitHubAsyncRESTOrganizations(GitHubAsyncREST):
    async def exists(self, organization: str) -> bool:
        """
        Check if an organization exists

        Args:
            repo: GitHub repository (owner/name) to use
        """
        api = f"/orgs/{organization}"
        response = await self._client.get(api)
        return response.is_success

    async def get_repositories(
        self,
        organization: str,
        *,
        repository_type: Union[RepositoryType, str] = RepositoryType.ALL,
    ) -> AsyncIterator[Repository]:
        """
        Get information about organization repositories

        https://docs.github.com/en/rest/repos/repos#list-organization-repositories

        Args:
            organization: GitHub organization to use
            repository_type: Only list repositories of this type.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/repos"
        params = {"type": enum_or_value(repository_type), "per_page": "100"}

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()
            for repo in response.json():
                yield Repository.from_dict(repo)

    async def members(
        self,
        organization: str,
        *,
        member_filter: Union[MemberFilter, str] = MemberFilter.ALL,
        role: Union[MemberRole, str] = MemberRole.ALL,
    ) -> AsyncIterator[User]:
        """
        Get information about organization members

        https://docs.github.com/en/rest/orgs/members#list-organization-members

        Args:
            organization: GitHub organization to use
            member_filter: Include only members of this kind.
            role: Filter members by their role.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/members"
        params = {
            "filter": enum_or_value(member_filter),
            "role": enum_or_value(role),
            "per_page": "100",
        }
        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for member in response.json():
                yield User.from_dict(member)

    async def invite(
        self,
        organization: str,
        *,
        email: Optional[str] = None,
        invitee_id: Optional[Union[str, int]] = None,
        role: Union[InvitationRole, str] = InvitationRole.DIRECT_MEMBER,
        team_ids: Iterable[Union[str, int]] = None,
    ) -> None:
        """
        Invite a user to a GitHub Organization

        https://docs.github.com/en/rest/orgs/members#create-an-organization-invitation

        Args:
            organization: GitHub organization to use
            email: Email address of the person you are inviting, which can be an
                existing GitHub user. Either an email or an invitee_id must be
                given.
            invitee_id: GitHub user ID for the person you are inviting. Either
                an email or an invitee_id must be given.
            role: The role for the new member.
                * admin - Organization owners with full administrative rights to
                  the organization and complete access to all repositories and
                  teams.
                * direct_member - Non-owner organization members with ability to
                  see other members and join teams by invitation.
                * billing_manager - Non-owner organization members with ability
                  to manage the billing settings of your organization.
            team_ids: Specify IDs for the teams you want to invite new members
                to.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        if not email and not invitee_id:
            raise GitHubApiError("Either email or invitee_id must be provided")

        api = f"/orgs/{organization}/invitations"
        data = {"role": enum_or_value(role)}
        if team_ids:
            data["team_ids"] = list(team_ids)

        if invitee_id:
            data["invitee_id"] = invitee_id
        else:
            data["email"] = email

        response = await self._client.post(api, data=data)
        response.raise_for_status()

    async def remove_member(
        self,
        organization: str,
        username: str,
    ) -> None:
        """
        Remove a member from a GitHub Organization

        https://docs.github.com/en/rest/orgs/members#remove-organization-membership-for-a-user

        Args:
            organization: GitHub organization to use
            username: The handle for the GitHub user account to remove from the
                organization.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/memberships/{username}"
        response = await self._client.delete(api)
        response.raise_for_status()

    async def outside_collaborators(
        self,
        organization: str,
        *,
        member_filter: Union[MemberFilter, str] = MemberFilter.ALL,
    ) -> AsyncIterator[User]:
        """
        Get information about outside collaborators of an organization

        https://docs.github.com/en/rest/orgs/outside-collaborators#list-outside-collaborators-for-an-organization

        Args:
            organization: GitHub organization to use
            member_filter: Filter the list of outside collaborators.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/outside_collaborators"
        params = {
            "filter": enum_or_value(member_filter),
            "per_page": "100",
        }
        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for member in response.json():
                yield User.from_dict(member)

    async def remove_outside_collaborator(
        self,
        organization: str,
        username: str,
    ) -> None:
        """
        Remove an outside collaborator from a GitHub Organization

        https://docs.github.com/en/rest/orgs/outside-collaborators#remove-outside-collaborator-from-an-organization

        Args:
            organization: GitHub organization to use
            username: The handle for the GitHub user account to remove from the
                organization.

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/outside_collaborators/{username}"
        response = await self._client.delete(api)
        response.raise_for_status()
