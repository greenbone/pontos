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
from datetime import date, datetime
from inspect import isclass
from typing import Any, Dict, Type, Union, get_type_hints

from dateutil import parser as dateparser

from pontos.errors import PontosError

try:
    from typing import get_args, get_origin
except ImportError:
    from typing_extensions import get_args, get_origin

__all__ = ("Model",)


class ModelError(PontosError):
    """
    Errors raised for Models
    """


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
            default = None if hasattr(obj, key) else ModelAttribute()
            prop = getattr(obj, key, default)
            value = dotted_attributes(prop, value)

        setattr(obj, key, value)

    return obj


class ModelAttribute:
    """
    A utility class to allow setting attributes
    """


@dataclass(init=False)
class Model:
    """
    Base class for models
    """

    @staticmethod
    def _get_value_from_model_field_cls(
        model_field_cls: Type[Any], value: Any
    ) -> Any:
        if isclass(model_field_cls) and issubclass(model_field_cls, Model):
            value = model_field_cls.from_dict(value)
        elif isclass(model_field_cls) and issubclass(model_field_cls, datetime):
            # Only Python 3.11 supports sufficient formats in
            # datetime.fromisoformat. Therefore we have to use dateutil here.
            value = dateparser.isoparse(value)
            # the iso format may not contain UTC data or a UTC offset
            # this means it is considered local time (Python calls this "naive"
            # datetime) and can't really be compared to other times. maybe we
            # should always assume UTC for these formats.
            # This could be done the following:
            # if not value.tzinfo:
            #     value = value.replace(tzinfo=timezone.utc)
        elif isclass(model_field_cls) and issubclass(model_field_cls, date):
            value = date.fromisoformat(value)
        elif get_origin(model_field_cls) == list:
            model_field_cls = get_args(model_field_cls)[0]
            value = Model._get_value_from_model_field_cls(
                model_field_cls, value
            )
        elif get_origin(model_field_cls) == dict:
            model_field_cls = dict
            value = Model._get_value_from_model_field_cls(
                model_field_cls, value
            )
        elif get_origin(model_field_cls) == Union:
            possible_types = get_args(model_field_cls)
            current_type = type(value)
            if current_type in possible_types:
                model_field_cls = current_type
            else:
                # currently Unions should not contain Models. this would require
                # to iterate over the possible type, check if it is a Model
                # class and try to create an instance of this class until it
                # fits. For now just fallback to first type
                model_field_cls = possible_types[0]

            value = Model._get_value_from_model_field_cls(
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
            value = Model._get_value_from_model_field_cls(
                model_field_cls, value
            )
        return value

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a model from a dict

        Example:
            .. code-block:: python

            model = Model.from_dict({
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
            try:
                if isinstance(value, list):
                    model_field_cls = type_hints.get(name)
                    value = [cls._get_value(model_field_cls, v) for v in value]
                elif value is not None:
                    model_field_cls = type_hints.get(name)
                    value = cls._get_value(model_field_cls, value)
            except TypeError as e:
                raise ModelError(
                    f"Error while creating {cls.__name__}. Could not set value "
                    f"for '{name}' from '{value}'."
                ) from e

            if name in type_hints:
                kwargs[name] = value
            else:
                additional_attrs[name] = value

        instance = cls(**kwargs)
        dotted_attributes(instance, additional_attrs)
        return instance
