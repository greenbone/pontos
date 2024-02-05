# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentTypeError
from enum import Enum
from typing import Callable, Type, TypeVar, Union


class StrEnum(str, Enum):
    # Should be replaced by enum.StrEnum when we require Python >= 3.11
    """
    An Enum that provides str like behavior
    """

    def __str__(self) -> str:
        return self.value


def enum_choice(enum: Type[Enum]) -> list[str]:
    """
    Return a sequence of choices for argparse from an enum
    """
    return [str(e) for e in enum]


def to_choices(enum: Type[Enum]) -> str:
    """
    Convert an enum to a comma separated string of choices. For example useful
    in help messages for argparse.
    """
    return ", ".join([str(t) for t in enum])


T = TypeVar("T", bound=Enum)


def enum_type(enum: Type[T]) -> Callable[[Union[str, T]], T]:
    """
    Create a argparse type function for converting the string input into an Enum
    """

    def convert(value: Union[str, T]) -> T:
        if isinstance(value, str):
            try:
                return enum(value)
            except ValueError:
                raise ArgumentTypeError(
                    f"invalid value {value}. Expected one of {to_choices(enum)}."
                ) from None
        return value

    return convert
