# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentTypeError
from collections.abc import Callable
from enum import Enum, StrEnum
from typing import TypeVar

__all__ = ("StrEnum", "enum_choice", "enum_type", "to_choices")


def enum_choice(enum: type[Enum]) -> list[str]:
    """
    Return a sequence of choices for argparse from an enum
    """
    return [str(e) for e in enum]


def to_choices(enum: type[Enum]) -> str:
    """
    Convert an enum to a comma separated string of choices. For example useful
    in help messages for argparse.
    """
    return ", ".join([str(t) for t in enum])


T = TypeVar("T", bound=Enum)


def enum_type(enum: type[T]) -> Callable[[str | T], T]:
    """
    Create a argparse type function for converting the string input into an Enum
    """

    def convert(value: str | T) -> T:
        if isinstance(value, str):
            try:
                return enum(value)
            except ValueError:
                raise ArgumentTypeError(
                    f"invalid value {value}. Expected one of {to_choices(enum)}."
                ) from None
        return value

    return convert
