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

from dataclasses import dataclass
from enum import Enum
from inspect import isclass
from typing import Any, Dict, List, Optional, Type, Union, get_type_hints

try:
    from typing import get_args, get_origin
except ImportError:
    from typing_extensions import get_args, get_origin

__all__ = (
    "App",
    "GitHubModel",
    "User",
    "Team",
)


def dotted_attributes(obj: Any, data: Dict[str, Any]) -> Any:
    """
    Set dotted attributes on an object

    Example:
        .. code-block:: python

            class Foo:
                '''Some class'''

            foo = Foo()
            attrs = {"bar": 123, "baz": 456}

            foo = dotted_attributes(foo, attrs)
            print(foo.bar, foo.baz)
    """
    for key, value in data.items():
        if isinstance(value, dict):
            default = None if hasattr(obj, key) else GitHubModelAttribute()
            prop = getattr(obj, key, default)
            value = dotted_attributes(prop, value)

        setattr(obj, key, value)

    return obj


class GitHubModelAttribute:
    """
    A utility class to allow setting attributes
    """


@dataclass(init=False)
class GitHubModel:
    """
    Base class for all GitHub models
    """

    @staticmethod
    def _get_value_from_model_field_cls(
        model_field_cls: Type[Any], value: Any
    ) -> Any:
        if isclass(model_field_cls) and issubclass(
            model_field_cls, GitHubModel
        ):
            value = model_field_cls.from_dict(value)
        elif (
            get_origin(model_field_cls) == Union
            or get_origin(model_field_cls) == list
        ):
            # it should be an Optional field
            model_field_cls = get_args(model_field_cls)[0]
            value = GitHubModel._get_value_from_model_field_cls(
                model_field_cls, value
            )
        else:
            if isinstance(value, dict):
                value = model_field_cls(**value)
            else:
                value = model_field_cls(value)
        return value

    @staticmethod
    def _get_value(model_field_cls: Type[Any], value: Any) -> Any:
        if model_field_cls:
            value = GitHubModel._get_value_from_model_field_cls(
                model_field_cls, value
            )
        return value

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a model from a dict

        Example:
            .. code-block:: python

            model = GitHubModel.from_dict({
                "id": 123,
                "node_id": "abcde",
                "created_at": "2017-07-08T16:18:44-04:00",
                "updated_at": "2017-07-08T16:18:44-04:00",
            })
        """
        kwargs = {}
        additional_attrs = {}
        type_hints = get_type_hints(cls)
        for name, value in data.items():
            if isinstance(value, list):
                model_field_cls = type_hints.get(name)
                value = [cls._get_value(model_field_cls, v) for v in value]
            elif value is not None:
                model_field_cls = type_hints.get(name)
                value = cls._get_value(model_field_cls, value)

            if name in type_hints:
                kwargs[name] = value
            else:
                additional_attrs[name] = value

        instance = cls(**kwargs)
        dotted_attributes(instance, additional_attrs)
        return instance


@dataclass
class User(GitHubModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool


class TeamPrivacy(Enum):
    SECRET = "secret"
    CLOSED = "closed"


class TeamRole(Enum):
    MEMBER = "member"
    MAINTAINER = "maintainer"


class Permission(Enum):
    PULL = "pull"
    PUSH = "push"
    TRIAGE = "triage"
    MAINTAIN = "maintain"
    ADMIN = "admin"


@dataclass
class Team(GitHubModel):
    id: int
    node_id: str
    url: str
    html_url: str
    name: str
    slug: str
    description: str
    privacy: TeamPrivacy
    permission: Permission
    members_url: str
    repositories_url: str
    parent: Optional["Team"] = None


@dataclass
class App(GitHubModel):
    id: int
    slug: str
    node_id: str
    owner: User
    name: str
    description: str
    external_url: str
    html_url: str
    created_at: str
    updated_at: str
    events: List[str]
