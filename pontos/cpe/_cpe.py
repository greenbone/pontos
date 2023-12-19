# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import urllib.parse
from dataclasses import dataclass
from typing import Any, Optional

from pontos.errors import PontosError
from pontos.models import StrEnum

__all__ = (
    "ANY",
    "NA",
    "CPEParsingError",
    "Part",
    "CPE",
)

ANY = "*"
NA = "-"


class CPEParsingError(PontosError):
    """
    An error occurred while parsing a CPE
    """


class Part(StrEnum):
    """
    Represents the possible values for a part CPE attribute
    """

    APPLICATION = "a"
    OPERATING_SYSTEM = "o"
    HARDWARE_DEVICE = "h"


def is_uri_binding(cpe: str) -> bool:
    """
    Returns True if cpe is a CPE v2.2 URI string
    """
    return cpe.startswith("cpe:/")


def is_formatted_string_binding(cpe: str) -> bool:
    """
    Returns True if cpe is a CPE v2.3 formatted string
    """
    return cpe.startswith("cpe:2.3:")


def convert_double_backslash(value: str) -> str:
    """
    Convert a double backslash into s single backslash
    """
    return re.sub("\\\\(\\W)", lambda match: match.group(1), value)


def _url_quote(value: str) -> str:
    """
    Quote value according to the pct_encode function from the spec for uri format
    """
    return urllib.parse.quote(value, safe="").lower()


def _url_unquote(value: str) -> str:
    """
    Un-quote value according to the the spec for uri format
    """
    return urllib.parse.unquote(value)


def pack_extended_attributes(
    edition: Optional[str],
    sw_edition: Optional[str],
    target_sw: Optional[str],
    target_hw: Optional[str],
    other: Optional[str],
) -> str:
    """
    Pack the extended attributes (v2.3) for an edition attribute (v2.2)
    """
    if (
        (not sw_edition or sw_edition == ANY)
        and (not target_sw or target_sw == ANY)
        and (not target_hw or target_hw == ANY)
        and (not other or other == ANY)
    ):
        if not edition or edition == ANY:
            return ""
        else:
            return edition
    else:
        return (
            f"~{'' if not edition or edition == ANY else edition}"
            f"~{'' if not sw_edition or sw_edition == ANY else sw_edition}"
            f"~{'' if not target_sw or target_sw == ANY else target_sw}"
            f"~{'' if not target_hw or target_hw == ANY else target_hw}"
            f"~{'' if not other or other == ANY else other}"
        )


def unpack_edition(edition: str) -> dict[str, Optional[str]]:
    """
    Unpack the edition attribute of v2.2 into extended attributes of v2.3
    """
    return dict(
        zip(
            [
                "edition",
                "sw_edition",
                "target_sw",
                "target_hw",
                "other",
            ],
            [None if not a else a for a in edition.split("~")[1:-1]],
        )
    )


def bind_value_for_formatted_string(value: Optional[str]) -> str:
    """
    Convert an attribute value for formatted string representation
    """
    if not value or value == ANY:
        return ANY

    value = value.replace("\\.", ".")
    value = value.replace("\\-", "-")
    value = value.replace("\\_", "_")
    return value


def _add_quoting(value: str) -> str:
    """
    Add quoting for parsing attributes from formatted string format to
    Well-Formed CPE Name Data Model (WFN)
    """
    result: list[str] = []
    index = 0
    embedded = False

    while index < len(value):
        c = value[index]
        if c.isalnum() or c in ["_"]:
            # just add character
            result.append(c)
            index += 1
            embedded = True
            continue

        if c == "\\":
            # keep escaped character
            result.append(value[index : index + 2])
            index += 2
            embedded = True
            continue

        if c == ANY:
            # An unquoted asterisk must appear at the beginning or
            # end of the string.
            if index == 0 or index == (len(value) - 1):
                result.append(c)
                index += 1
                embedded = True
                continue
            else:
                raise CPEParsingError(
                    "An unquoted asterisk must appear at the beginning or end "
                    f"of '{value}'"
                )
        if c == "?":
            # An unquoted question mark must appear at the beginning or
            # end of the string, or in a leading or trailing sequence
            if (
                (  # ? is legal at the beginning or the end
                    (index == 0) or (index == (len(value) - 1))
                )
                or (  # embedded is false, so must be preceded by ?
                    not embedded and (value[index - 1 : index] == "?")
                )
                or (  # embedded is true, so must be followed by ?
                    embedded and (value[index + 1] == "?")
                )
            ):
                result.append(c)
                index += 1
                embedded = False
                continue
            else:
                raise CPEParsingError(
                    "An unquoted question mark must appear at the beginning or "
                    f"end, or in a leading or trailing sequence '{value}'"
                )

        # all other characters must be quoted
        result.append(f"\\{c}")
        index += 1
        embedded = True

    return "".join(result)


def unbind_value_from_formatted_string(value: Optional[str]) -> Optional[str]:
    """
    Convert a formatted string representation to an attribute value for WNF
    """
    if value is None or value == ANY or value == NA:
        return value
    return _add_quoting(value)


def _transform_for_uri(value: str) -> str:
    """
    Applies transform to convert an attribute for an uri representation

    The following transformations are applied:
        - Pass alphanumeric characters thru untouched
        - Percent-encode quoted non-alphanumerics as needed
        - Unquoted special characters are mapped to their special forms
    """
    transformed = ""
    index = 0
    while index < len(value):
        c = value[index]

        # alpha numeric characters
        if c.isalnum() or c in ["_", "-", ".", "~"]:
            transformed += c
            index += 1
            continue

        # percent encoding
        if c == "\\":
            index += 1
            next = value[index]
            transformed += _url_quote(convert_double_backslash(next))
            index += 1
            continue

        # special forms
        if c == "?":
            transformed += "%01"
        elif c == "*":
            transformed += "%02"

        index += 1

    return transformed


def bind_value_for_uri(value: Optional[str]) -> str:
    """
    Convert an attribute value for uri representation
    """
    if not value or value == ANY:
        return ""
    if value == NA:
        return value
    try:
        return _transform_for_uri(value)
    except Exception as e:
        raise CPEParsingError(f"Can't bind '{value}' for URI") from e


def unbind_value_uri(value: Optional[str]) -> Optional[str]:
    """
    Convert an uri representation to an attribute value
    """
    if value is None:
        return None
    if value == "":
        return ANY
    if value == NA:
        return NA

    result = ""
    index = 0
    embedded = False
    while index < len(value):
        c = value[index]
        if c == "." or c == "-" or c == "~":
            result += f"\\{c}"
            index += 1
            embedded = True
            continue

        if c != "%":
            result += c
            index += 1
            embedded = True
            continue

        form = value[index : index + 3]
        if form == "%01":
            if (
                index == 0
                or (index == (len(value) - 3))
                or (not embedded and (value[index - 3 : index] == "%01"))
                or (
                    embedded
                    and (len(value) >= index + 6)
                    and (value[index + 3 : index + 6]) == "%01"
                )
            ):
                result += "?"
            else:
                raise CPEParsingError(
                    "A percent-encoded question mark is not found at the "
                    f"beginning or the end or embedded in sequence '{value}'"
                )
        elif form == "%02":
            if (index == 0) or (index == (len(value) - 3)):
                result += "*"
            else:
                raise CPEParsingError(
                    "Percent-encoded asterisk is no at the beginning "
                    f"or the end of '{value}'"
                )
        else:
            result += f"\\{_url_unquote(form)}"
        index += 3
        embedded = True

    return result


def unquote_attribute_value(value: Optional[str]) -> Optional[str]:
    """
    Unquote a Well-Formed CPE Name Data Model (WFN) attribute value
    """
    if not value or "\\" not in value:
        # do nothing
        return value

    index = 0
    result = ""
    while index < len(value):
        c = value[index]
        if c == "\\":
            next_c = value[index + 1]
            if next_c in ["*", "?"]:
                # keep escaped asterisks and question marks
                result += f"{c}{next_c}"
            else:
                result += next_c

            index += 2
            continue
        else:
            result += c

        index += 1

    return result


def split_cpe(cpe: str) -> list[str]:
    """
    Split a CPE into its parts
    """
    if "\\:" in cpe:
        # houston we have a problem
        # the cpe string contains an escaped colon (:)
        parts = []
        index = 0
        start_index = 0
        stripped_cpe = cpe
        while index < len(cpe):
            if index > 0 and cpe[index] == ":" and cpe[index - 1] != "\\":
                part = cpe[start_index:index]
                parts.append(part)
                start_index = index + 1
                stripped_cpe = cpe[start_index:]
            index += 1

        if stripped_cpe:
            parts.append(stripped_cpe)
    else:
        parts = cpe.split(":")

    return parts


@dataclass(frozen=True)
class CPEWellFormed:
    """
    Represents a Common Platform Enumeration (CPE) name using the Well-Formed
    CPE Name (WNF) Data Model. Attributes are quoted according to the WNF model.

    In most cases this class should not be used directly and the CPE class
    should be used instead.

    Attributes:
        part: Value should be "a" for application, "o" for operating system or
            "h" for hardware
        vendor: Person or organization that manufactured or created the product
        product: Identifies the most common and recognizable title or name of
            the product
        version: A vendor-specific alphanumeric string characterizing the
            particular release version of the product
        update: A vendor-specific alphanumeric string characterizing the
            particular update, service pack, or point release of the product
        edition: The edition attribute is considered deprecated in the 2.3
            CPE specification, and it should be assigned the logical value ANY
            except where required for backward compatibility with version 2.2 of
            the CPE specification. This attribute is referred to as the “legacy
            edition” attribute
        language: Defines the language supported in the user interface of the
            product (as language tags defined by RFC5646)
        sw_edition: Characterizes how the product is tailored to a particular
            market or class of end users. Extended attribute introduced with
            version 2.3 of the CPE specification
        target_sw: Characterizes the software computing environment within which
            the product operates. Extended attribute introduced with
            version 2.3 of the CPE specification
        hardware_sw: Characterizes the instruction set architecture (e.g., x86)
            on which the product operates. Extended attribute introduced with
            version 2.3 of the CPE specification
        other: Captures any other general descriptive or identifying information
            which is vendor- or product-specific and which does not logically
            fit in any other attribute value. Extended attribute introduced with
            version 2.3 of the CPE specification
    """

    part: Part
    vendor: str
    product: str
    version: Optional[str] = None
    update: Optional[str] = None
    edition: Optional[str] = None
    language: Optional[str] = None
    sw_edition: Optional[str] = None
    target_sw: Optional[str] = None
    target_hw: Optional[str] = None
    other: Optional[str] = None


class CPE:
    """
    Represents a Common Platform Enumeration (CPE) name

    Supports CPE specification 2.2 (uri) and 2.3 (formatted string)

    Attributes:
        part: Value should be "a" for application, "o" for operating system or
            "h" for hardware
        vendor: Person or organization that manufactured or created the product
        product: Identifies the most common and recognizable title or name of
            the product
        version: A vendor-specific alphanumeric string characterizing the
            particular release version of the product
        update: A vendor-specific alphanumeric string characterizing the
            particular update, service pack, or point release of the product
        edition: The edition attribute is considered deprecated in the 2.3
            CPE specification, and it should be assigned the logical value ANY
            except where required for backward compatibility with version 2.2 of
            the CPE specification. This attribute is referred to as the “legacy
            edition” attribute
        language: Defines the language supported in the user interface of the
            product (as language tags defined by RFC5646)
        sw_edition: Characterizes how the product is tailored to a particular
            market or class of end users. Extended attribute introduced with
            version 2.3 of the CPE specification
        target_sw: Characterizes the software computing environment within which
            the product operates. Extended attribute introduced with
            version 2.3 of the CPE specification
        hardware_sw: Characterizes the instruction set architecture (e.g., x86)
            on which the product operates. Extended attribute introduced with
            version 2.3 of the CPE specification
        other: Captures any other general descriptive or identifying information
            which is vendor- or product-specific and which does not logically
            fit in any other attribute value. Extended attribute introduced with
            version 2.3 of the CPE specification
        cpe_string: The original parsed CPE string

    Example:
        .. code-block:: python

            from pontos.cpe import CPE

            cpe = CPE.from_string("cpe:2.3:o:google:android:13.0:*:*:*:*:*:*:*")

            print(cpe.vendor)           # google
            print(cpe.product)          # android
            print(cpe.version)          # 13.0
            print(cpe.as_uri_binding()) # cpe:/o:google:android:13.0
    """

    def __init__(
        self,
        *,
        cpe_string: Optional[str] = None,
        part: Part,
        vendor: str,
        product: str,
        version: Optional[str] = None,
        update: Optional[str] = None,
        edition: Optional[str] = None,
        language: Optional[str] = None,
        sw_edition: Optional[str] = None,
        target_sw: Optional[str] = None,
        target_hw: Optional[str] = None,
        other: Optional[str] = None,
    ) -> None:
        self.cpe_string = cpe_string
        self.__wnf__ = CPEWellFormed(
            part=part,
            vendor=vendor,
            product=product,
            version=version,
            update=update,
            edition=edition,
            language=language,
            sw_edition=sw_edition,
            target_sw=target_sw,
            target_hw=target_hw,
            other=other,
        )
        self.part = part
        self.vendor = unquote_attribute_value(vendor)
        self.product = unquote_attribute_value(product)
        self.version = unquote_attribute_value(version)
        self.update = unquote_attribute_value(update)
        self.edition = unquote_attribute_value(edition)
        self.language = unquote_attribute_value(language)
        self.sw_edition = unquote_attribute_value(sw_edition)
        self.target_sw = unquote_attribute_value(target_sw)
        self.target_hw = unquote_attribute_value(target_hw)
        self.other = unquote_attribute_value(other)

    @staticmethod
    def from_string(cpe: str) -> "CPE":
        """
        Create a new CPE from a string
        """
        cleaned_cpe = cpe.strip().lower()
        parts = split_cpe(cleaned_cpe)

        if is_uri_binding(cleaned_cpe):
            values: dict[str, Optional[str]] = dict(
                zip(
                    [
                        "vendor",
                        "product",
                        "version",
                        "update",
                        "edition",
                        "language",
                    ],
                    parts[2:],
                )
            )
            for attribute in [
                "vendor",
                "product",
                "version",
                "update",
                "language",
            ]:
                values[attribute] = unbind_value_uri(values.get(attribute))

            edition = values.get("edition")
            if (
                edition is None
                or edition == ""
                or edition == NA
                or edition[0] != "~"
            ):
                edition = unbind_value_uri(edition)
            else:
                values.update(unpack_edition(edition))

            return CPE(cpe_string=cleaned_cpe, part=Part(parts[1][1]), **values)  # type: ignore[arg-type]

        elif is_formatted_string_binding(cleaned_cpe):
            values = dict(
                zip(
                    [
                        "vendor",
                        "product",
                        "version",
                        "update",
                        "edition",
                        "language",
                        "sw_edition",
                        "target_sw",
                        "target_hw",
                        "other",
                    ],
                    [unbind_value_from_formatted_string(a) for a in parts[3:]],
                )
            )

            return CPE(cpe_string=cleaned_cpe, part=Part(parts[2]), **values)  # type: ignore[arg-type]

        raise CPEParsingError(
            f"Invalid CPE string '{cpe}'. CPE does not start with "
            "'cpe:/' or 'cpe:2.3'"
        )

    def has_extended_attribute(self) -> bool:
        """
        Returns True if the CPE has an extended attribute set
        """
        return bool(
            self.sw_edition or self.target_sw or self.target_hw or self.other
        )

    def is_uri_binding(self) -> bool:
        """
        Returns True if the CPE is parsed from a URI binding
        """
        if self.cpe_string:
            return is_uri_binding(self.cpe_string)
        return not self.has_extended_attribute()

    def is_formatted_string_binding(self) -> bool:
        """
        Returns True if the CPE is parsed from a formatted string binding
        """
        if self.cpe_string:
            return is_formatted_string_binding(self.cpe_string)
        return self.has_extended_attribute()

    def as_uri_binding(self) -> str:
        """
        Converts the CPE to an URI binding
        """
        part = self.part.value
        vendor = bind_value_for_uri(self.__wnf__.vendor)
        product = bind_value_for_uri(self.__wnf__.product)
        version = bind_value_for_uri(self.__wnf__.version)
        update = bind_value_for_uri(self.__wnf__.update)
        language = bind_value_for_uri(self.__wnf__.language)
        edition = bind_value_for_uri(self.__wnf__.edition)
        sw_edition = bind_value_for_uri(self.__wnf__.sw_edition)
        target_sw = bind_value_for_uri(self.__wnf__.target_sw)
        target_hw = bind_value_for_uri(self.__wnf__.target_hw)
        other = bind_value_for_uri(self.__wnf__.other)

        edition = pack_extended_attributes(
            edition,
            sw_edition,
            target_sw,
            target_hw,
            other,
        )

        uri = f"cpe:/{part}:{vendor}:{product}"
        if version or update or edition or language:
            uri = f"{uri}:{version}"
        if update or edition or language:
            uri = f"{uri}:{update}"
        if edition or language:
            uri = f"{uri}:{edition}"
        if language:
            uri = f"{uri}:{language}"
        return uri

    def as_formatted_string_binding(self) -> str:
        """
        Converts the CPE to a formatted string binding
        """
        part = self.part.value
        vendor = bind_value_for_formatted_string(self.__wnf__.vendor)
        product = bind_value_for_formatted_string(self.__wnf__.product)
        version = bind_value_for_formatted_string(self.__wnf__.version)
        update = bind_value_for_formatted_string(self.__wnf__.update)
        edition = bind_value_for_formatted_string(self.__wnf__.edition)
        language = bind_value_for_formatted_string(self.__wnf__.language)
        sw_edition = bind_value_for_formatted_string(self.__wnf__.sw_edition)
        target_sw = bind_value_for_formatted_string(self.__wnf__.target_sw)
        target_hw = bind_value_for_formatted_string(self.__wnf__.target_hw)
        other = bind_value_for_formatted_string(self.__wnf__.other)
        return (
            f"cpe:2.3:{part}:{vendor}:{product}:{version}:{update}:"
            f"{edition}:{language}:{sw_edition}:{target_sw}:{target_hw}:{other}"
        )

    def clone(
        self,
        **kwargs,
    ) -> "CPE":
        """
        Clone a CPE and allow to override parts

        Example:
            .. code-block:: python

                from pontos.cpe import CPE, ANY

                android_13 = CPE.from_string(
                    "cpe:2.3:o:google:android:13.0:*:*:*:*:*:*:*"
                )
                all_android_versions = cpe.clone(version=ANY)
        """
        args = {
            "part": self.__wnf__.part,
            "vendor": self.__wnf__.vendor,
            "product": self.__wnf__.product,
            "version": self.__wnf__.version,
            "update": self.__wnf__.update,
            "edition": self.__wnf__.edition,
            "language": self.__wnf__.language,
            "sw_edition": self.__wnf__.sw_edition,
            "target_sw": self.__wnf__.target_sw,
            "target_hw": self.__wnf__.target_hw,
            "other": self.__wnf__.other,
            "cpe_string": self.cpe_string,
        }
        args.update(**kwargs)
        return CPE(**args)  # type: ignore[arg-type]

    def __str__(self) -> str:
        """
        Returns the string representation (uri of formatted string) of the CPE
        """
        if self.cpe_string:
            return self.cpe_string

        if not self.has_extended_attribute():
            return self.as_uri_binding()

        return self.as_formatted_string_binding()

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f'part="{self.part}" '
            f'vendor="{self.vendor}" '
            f'product="{self.product}" '
            f'version="{self.version}" '
            f'update="{self.update}" '
            f'edition="{self.edition}" '
            f'language="{self.language}" '
            f'sw_edition="{self.sw_edition}" '
            f'target_sw="{self.target_sw}" '
            f'target_hw="{self.target_hw}" '
            f'other="{self.other}"'
            ">"
        )

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CPE):
            return False
        return str(self) == str(other)
