# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import AsyncIterator, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.helper import JSON_OBJECT
from pontos.github.models.base import User
from pontos.github.models.user import (
    EmailInformation,
    SSHPublicKey,
    SSHPublicKeyExtended,
)


class GitHubAsyncRESTUsers(GitHubAsyncREST):
    async def users(self) -> AsyncIterator[User]:
        """

        https://docs.github.com/en/rest/users/users#list-users

        Args:
            username: The handle for the GitHub user account

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding user information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for user in api.users.users():
                        print(user)
        """
        api = "/users"
        params = {"per_page": "100"}
        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for user in response.json():
                yield User.from_dict(user)

    async def user(self, username: str) -> User:
        """
        Provide publicly available information about someone with a GitHub
        account

        https://docs.github.com/en/rest/users/users#get-a-user

        Args:
            username: The handle for the GitHub user account

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the user

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    user = await api.users.user("foo")
                    print(user)
        """
        api = f"/users/{username}"
        response = await self._client.get(api)
        response.raise_for_status()
        return User.from_dict(response.json())

    async def current_user(self) -> User:
        """
        Get the current authenticated user

        https://docs.github.com/en/rest/users/users#get-the-authenticated-user

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the user

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    user = await api.users.current_user()
                    print(user)
        """
        api = "/user"
        response = await self._client.get(api)
        response.raise_for_status()
        return User.from_dict(response.json())

    async def user_keys(self, username: str) -> AsyncIterator[SSHPublicKey]:
        """
        List the verified public SSH keys for a user

        https://docs.github.com/en/rest/users/keys#list-public-keys-for-a-user

        Args:
            username: The handle for the GitHub user account

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding ssh key information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for key in api.users.user_keys("foo"):
                        print(key)
        """
        api = f"/users/{username}/keys"
        params = {"per_page": "100"}
        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for key in response.json():
                yield SSHPublicKey.from_dict(key)

    async def keys(self) -> AsyncIterator[SSHPublicKey]:
        """
        List the public SSH keys for the authenticated user's GitHub account

        https://docs.github.com/en/rest/users/keys#list-public-ssh-keys-for-the-authenticated-user

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding ssh key information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for key in api.users.keys():
                        print(key)
        """
        api = "/user/keys"
        params = {"per_page": "100"}
        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for key in response.json():
                yield SSHPublicKey.from_dict(key)

    async def emails(self) -> AsyncIterator[EmailInformation]:
        """
        List all email addresses of the currently logged in user

        https://docs.github.com/en/rest/users/emails#list-email-addresses-for-the-authenticated-user

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding email information

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for email in api.users.emails():
                        print(email)
        """
        api = "/user/emails"
        params = {"per_page": "100"}
        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()

            for email in response.json():
                yield EmailInformation.from_dict(email)

    async def key(self, key_id: Union[str, int]) -> SSHPublicKeyExtended:
        """
        View extended details for a single public SSH key

        https://docs.github.com/en/rest/users/keys#get-a-public-ssh-key-for-the-authenticated-user

        Args:
            key_id: The unique identifier of the key

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Extended information about the SSH key

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    key = await api.users.key(123)
                    print(key)
        """
        api = f"/user/keys/{key_id}"
        response = await self._client.get(api)
        response.raise_for_status()
        return SSHPublicKeyExtended.from_dict(response.json())

    async def delete_key(self, key_id: Union[str, int]) -> None:
        """
        Removes a public SSH key from the authenticated user's GitHub account

        https://docs.github.com/en/rest/users/keys#delete-a-public-ssh-key-for-the-authenticated-user

        Args:
            key_id: The unique identifier of the key

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    await api.users.delete_key(123)
        """
        api = f"/user/keys/{key_id}"
        response = await self._client.delete(api)
        response.raise_for_status()

    async def create_key(self, title: str, key: str) -> SSHPublicKeyExtended:
        """
        Adds a public SSH key to the authenticated user's GitHub account

        https://docs.github.com/en/rest/users/keys#create-a-public-ssh-key-for-the-authenticated-user

        Args:
            title: A descriptive name for the new key
            key: The public SSH key to add to your GitHub account

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Extended information about the SSH key

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    key = await api.users.create_key(
                        "My SSH Public Key",
                        "2Sg8iYjAxxmI2LvUXpJjkYrMxURPc8r+dB7TJyvv1234"
                    )
                    print(key)
        """
        api = "/user/keys"
        data: JSON_OBJECT = {"key": key, "title": title}
        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return SSHPublicKeyExtended.from_dict(response.json())
