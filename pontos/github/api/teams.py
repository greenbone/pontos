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

from typing import Iterable

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.helper import JSON_OBJECT


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
