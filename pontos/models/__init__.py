# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from dataclasses import dataclass
from datetime import date, datetime, timezone
from inspect import isclass
from typing import Any, Dict, Type, Union, get_args, get_origin, get_type_hints

from dateutil import parser as dateparser

from pontos.enum import StrEnum
from pontos.errors import PontosError

__all__ = (
    "Model",
    "ModelError",
    "StrEnum",
    "dotted_attributes",
)


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
            value = dotted_attributes(prop, value)  # noqa: PLW2901

        setattr(obj, key, value)

    return obj


class ModelAttribute:
    """
    A utility class to allow setting attributes
    """


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
        # datetime) and can't really be compared to other times.
        # Let's UTC in these cases:
        if not value.tzinfo:
            value = value.replace(tzinfo=timezone.utc)
    elif isclass(model_field_cls) and issubclass(model_field_cls, date):
        value = date.fromisoformat(value)
    elif get_origin(model_field_cls) == list:
        model_field_cls = get_args(model_field_cls)[0]
        value = _get_value_from_model_field_cls(model_field_cls, value)
    elif get_origin(model_field_cls) == dict:
        model_field_cls = dict
        value = _get_value_from_model_field_cls(model_field_cls, value)
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

        value = _get_value_from_model_field_cls(model_field_cls, value)
    else:
        if isinstance(value, dict):
            value = model_field_cls(**value)
        else:
            value = model_field_cls(value)
    return value


def _get_value(model_field_cls: Type[Any], value: Any) -> Any:
    if model_field_cls:
        value = _get_value_from_model_field_cls(model_field_cls, value)
    return value


@dataclass(init=False)
class Model:
    """
    Base class for models
    """

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
        if not isinstance(data, dict):
            raise ValueError(
                f"Invalid data for creating an instance of {cls.__name__} "
                f"model. Data is {data!r}"
            )

        kwargs = {}
        additional_attrs = {}
        type_hints = get_type_hints(cls)
        for name, value in data.items():
            try:
                if isinstance(value, list):
                    model_field_cls = type_hints.get(name)
                    value = [_get_value(model_field_cls, v) for v in value]  # type: ignore # pylint: disable=line-too-long # noqa: E501,PLW2901
                elif value is not None:
                    model_field_cls = type_hints.get(name)
                    value = _get_value(model_field_cls, value)  # type: ignore # pylint: disable=line-too-long # noqa: E501,PLW2901
            except (ValueError, TypeError) as e:
                raise ModelError(
                    f"Error while creating {cls.__name__} model. Could not set "
                    f"value for property '{name}' from '{value}'."
                ) from e

            if name in type_hints:
                kwargs[name] = value
            else:
                additional_attrs[name] = value

        instance = cls(**kwargs)
        dotted_attributes(instance, additional_attrs)
        return instance
