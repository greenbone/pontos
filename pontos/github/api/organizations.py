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

import httpx

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.errors import GitHubApiError
from pontos.github.api.helper import JSON, JSON_OBJECT, RepositoryType


class MemberFilter(Enum):
    TWO_FA_DISABLED = "2fa_disabled"
    ALL = "all"


class MemberRole(Enum):
    ALL = "all"
    ADMIN = "admin"
    MEMBER = "member"


class InvitationRole(Enum):
    ADMIN = "admin"
    DIRECT_MEMBER = "direct_member"
    BILLING_MANAGER = "billing_manager"


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
        repository_type: RepositoryType = RepositoryType.ALL,
    ) -> Iterable[JSON_OBJECT]:
        """
        Get information about organization repositories

        Args:
            organization: GitHub organization to use

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/repos"
        params = {"type": repository_type.value, "per_page": "100"}
        repos = []

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            repos.extend(response.json())

        return repos

    async def members(
        self,
        organization: str,
        *,
        member_filter: MemberFilter = MemberFilter.ALL,
        role: MemberRole = MemberRole.ALL,
    ) -> Iterable[JSON_OBJECT]:
        """
        Get information about organization members

        Args:
            organization: GitHub organization to use
            member_filter:

        Raises:
            `httpx.HTTPStatusError` if there was an error in the request
        """
        api = f"/orgs/{organization}/members"
        params = {
            "filter": member_filter.value,
            "per_page": "100",
            "role": role.value,
        }
        members = []

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            members.extend(response.json())

        return members

    async def invite(
        self,
        organization: str,
        *,
        email: Optional[str] = None,
        invitee_id: Optional[str] = None,
        role: InvitationRole = InvitationRole.DIRECT_MEMBER,
        team_ids: Iterable[str] = None,
    ) -> None:
        """
        Invite a user to a GitHub Organization

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
        data = {"role": role.value}
        if team_ids:
            data["team_ids"] = list(team_ids)

        if invitee_id:
            data["invitee_id"] = invitee_id
        else:
            data["email"] = email

        response = await self._client.post(api, data=data)
        response.raise_for_status()


class GitHubRESTOrganizationsMixin:
    def organisation_exists(self, orga: str) -> bool:
        """
        Check if an organization exists

        Args:
            repo: GitHub repository (owner/name) to use
        """
        api = f"/orgs/{orga}"
        response: httpx.Response = self._request(api)
        return response.is_success

    def get_organization_repository_number(
        self, orga: str, repository_type: RepositoryType
    ) -> int:
        """
        Get total number of repositories of organization

        Args:
            repo: GitHub repository (owner/name) to use
            pull_request: Pull request number to check
        """
        api = f"/orgs/{orga}"
        response: httpx.Response = self._request(api)
        response.raise_for_status()
        response_json = response.json()

        if repository_type == RepositoryType.PUBLIC:
            return response_json["public_repos"]
        if repository_type == RepositoryType.PRIVATE:
            return response_json["total_private_repos"]
            # Use ALL for currently unsupported "types" (INTERNAL, FORKS ...)
        return (
            response_json["public_repos"] + response_json["total_private_repos"]
        )

    def get_repositories(
        self,
        orga: str,
        repository_type: RepositoryType = RepositoryType.ALL,
    ) -> JSON:
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
        params = {"type": repository_type.value, "per_page": 100}
        page = 0
        while count - downloaded > 0:
            page += 1
            params["page"] = page
            response: httpx.Response = self._request(api, params=params)
            response.raise_for_status()

            repos.extend(response.json())
            downloaded = len(repos)

        return repos
