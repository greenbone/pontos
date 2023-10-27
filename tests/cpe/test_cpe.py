# SPDX-FileCopyrightText: 2022 - 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa: E501

import unittest

from pontos.cpe import ANY, CPE, NA, CPEParsingError, Part


class CPETestCase(unittest.TestCase):
    def test_uri_binding(self):
        cpe_string = "cpe:/o:microsoft:windows_xp:::pro"
        cpe = CPE.from_string(cpe_string)

        self.assertEqual(str(cpe), "cpe:/o:microsoft:windows_xp:::pro")
        self.assertEqual(
            cpe.as_uri_binding(), "cpe:/o:microsoft:windows_xp:::pro"
        )
        self.assertEqual(
            cpe.as_formatted_string_binding(),
            "cpe:2.3:o:microsoft:windows_xp:*:*:pro:*:*:*:*:*",
        )
        self.assertTrue(cpe.is_uri_binding())
        self.assertFalse(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.OPERATING_SYSTEM)
        self.assertEqual(cpe.vendor, "microsoft")
        self.assertEqual(cpe.product, "windows_xp")
        self.assertEqual(cpe.edition, "pro")
        self.assertEqual(cpe.version, ANY)
        self.assertEqual(cpe.update, ANY)
        self.assertIsNone(cpe.language)
        self.assertIsNone(cpe.sw_edition)
        self.assertIsNone(cpe.target_sw)
        self.assertIsNone(cpe.target_hw)
        self.assertIsNone(cpe.other)

        cpe = CPE.from_string(
            "cpe:/a:foo%5cbar:big%24money_manager_2010:::~~special~ipod_touch~80gb~"
        )
        print(repr(cpe))
        self.assertEqual(
            str(cpe),
            "cpe:/a:foo%5cbar:big%24money_manager_2010:::~~special~ipod_touch~80gb~",
        )
        self.assertEqual(
            cpe.as_uri_binding(),
            "cpe:/a:foo%5cbar:big%24money_manager_2010:::~~special~ipod_touch~80gb~",
        )
        self.assertEqual(
            cpe.as_formatted_string_binding(),
            "cpe:2.3:a:foo\\\\bar:big\$money_manager_2010:*:*:*:*:special:ipod_touch:80gb:*",
        )
        self.assertTrue(cpe.is_uri_binding())
        self.assertFalse(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "foo\\\\bar")
        self.assertEqual(cpe.product, "big\$money_manager_2010")
        self.assertEqual(cpe.version, ANY)
        self.assertEqual(cpe.update, ANY)
        self.assertIsNone(cpe.language)
        self.assertIsNone(cpe.edition)
        self.assertEqual(cpe.sw_edition, "special")
        self.assertEqual(cpe.target_sw, "ipod_touch")
        self.assertEqual(cpe.target_hw, "80gb")
        self.assertIsNone(cpe.other)

    def test_formatted_string_binding(self):
        cpe_string = (
            "cpe:2.3:a:qrokes:qr_twitter_widget:*:*:*:*:*:wordpress:*:*"
        )
        cpe = CPE.from_string(cpe_string)
        print(repr(cpe))

        self.assertEqual(
            str(cpe),
            "cpe:2.3:a:qrokes:qr_twitter_widget:*:*:*:*:*:wordpress:*:*",
        )
        self.assertEqual(
            cpe.as_uri_binding(),
            "cpe:/a:qrokes:qr_twitter_widget:::~~~wordpress~~",
        )
        self.assertEqual(
            cpe.as_formatted_string_binding(),
            "cpe:2.3:a:qrokes:qr_twitter_widget:*:*:*:*:*:wordpress:*:*",
        )
        self.assertFalse(cpe.is_uri_binding())
        self.assertTrue(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "qrokes")
        self.assertEqual(cpe.product, "qr_twitter_widget")
        self.assertEqual(cpe.version, ANY)
        self.assertEqual(cpe.update, ANY)
        self.assertEqual(cpe.edition, ANY)
        self.assertEqual(cpe.language, ANY)
        self.assertEqual(cpe.sw_edition, ANY)
        self.assertEqual(cpe.target_sw, "wordpress")
        self.assertEqual(cpe.target_hw, ANY)
        self.assertEqual(cpe.other, ANY)

    def test_uri_bind_examples(self):
        # test examples from https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7695.pdf

        # example 1
        cpe = CPE(
            part=Part.APPLICATION,
            vendor="microsoft",
            product="internet_explorer",
            version="8\.0\.6001",
            update="beta",
            edition=ANY,
        )
        self.assertEqual(
            cpe.as_uri_binding(),
            "cpe:/a:microsoft:internet_explorer:8.0.6001:beta",
        )

        # example 2
        cpe = CPE(
            part=Part.APPLICATION,
            vendor="microsoft",
            product="internet_explorer",
            version="8\.*",
            update="sp?",
        )
        self.assertEqual(
            cpe.as_uri_binding(),
            "cpe:/a:microsoft:internet_explorer:8.%02:sp%01",
        )

        # example 3
        cpe = CPE(
            part=Part.APPLICATION,
            vendor="hp",
            product="insight_diagnostics",
            version="7\.4\.0\.1570",
            update=NA,
            sw_edition="online",
            target_sw="win2003",
            target_hw="x64",
        )
        self.assertEqual(
            cpe.as_uri_binding(),
            "cpe:/a:hp:insight_diagnostics:7.4.0.1570:-:~~online~win2003~x64~",
        )

        # example 4
        cpe = CPE(
            part=Part.APPLICATION,
            vendor="hp",
            product="openview_network_manager",
            version="7\.51",
            target_sw="linux",
        )
        self.assertEqual(
            cpe.as_uri_binding(),
            "cpe:/a:hp:openview_network_manager:7.51::~~~linux~~",
        )

        # example 5
        cpe = CPE(
            part=Part.APPLICATION,
            vendor="foo\\\\bar",
            product="big\$money_manager_2010",
            sw_edition="special",
            target_sw="ipod_touch",
            target_hw="80gb",
        )
        self.assertEqual(
            cpe.as_uri_binding(),
            "cpe:/a:foo%5cbar:big%24money_manager_2010:::~~special~ipod_touch~80gb~",
        )

    def test_uri_unbind_examples(self):
        # test examples from https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7695.pdf

        # example 1
        cpe = CPE.from_string(
            "cpe:/a:microsoft:internet_explorer:8.0.6001:beta"
        )
        self.assertTrue(cpe.is_uri_binding())
        self.assertFalse(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "microsoft")
        self.assertEqual(cpe.product, "internet_explorer")
        self.assertEqual(cpe.version, "8\.0\.6001")
        self.assertEqual(cpe.update, "beta")
        self.assertIsNone(cpe.language)
        self.assertIsNone(cpe.edition)
        self.assertIsNone(cpe.sw_edition)
        self.assertIsNone(cpe.target_sw)
        self.assertIsNone(cpe.target_hw)
        self.assertIsNone(cpe.other)

        # example 2
        cpe = CPE.from_string("cpe:/a:microsoft:internet_explorer:8.%2a:sp%3f")
        self.assertTrue(cpe.is_uri_binding())
        self.assertFalse(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "microsoft")
        self.assertEqual(cpe.product, "internet_explorer")
        self.assertEqual(cpe.version, "8\.\*")
        self.assertEqual(cpe.update, "sp\?")
        self.assertIsNone(cpe.language)
        self.assertIsNone(cpe.edition)
        self.assertIsNone(cpe.sw_edition)
        self.assertIsNone(cpe.target_sw)
        self.assertIsNone(cpe.target_hw)
        self.assertIsNone(cpe.other)

        # example 3
        cpe = CPE.from_string("cpe:/a:microsoft:internet_explorer:8.%02:sp%01")
        self.assertTrue(cpe.is_uri_binding())
        self.assertFalse(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "microsoft")
        self.assertEqual(cpe.product, "internet_explorer")
        self.assertEqual(cpe.version, "8\.*")
        self.assertEqual(cpe.update, "sp?")
        self.assertIsNone(cpe.language)
        self.assertIsNone(cpe.edition)
        self.assertIsNone(cpe.sw_edition)
        self.assertIsNone(cpe.target_sw)
        self.assertIsNone(cpe.target_hw)
        self.assertIsNone(cpe.other)

        # example 4
        cpe = CPE.from_string(
            "cpe:/a:hp:insight_diagnostics:7.4.0.1570::~~online~win2003~x64~"
        )
        print(repr(cpe))
        self.assertTrue(cpe.is_uri_binding())
        self.assertFalse(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "hp")
        self.assertEqual(cpe.product, "insight_diagnostics")
        self.assertEqual(cpe.version, "7\.4\.0\.1570")
        self.assertEqual(cpe.update, ANY)
        self.assertIsNone(cpe.language)
        self.assertIsNone(cpe.edition)
        self.assertEqual(cpe.sw_edition, "online")
        self.assertEqual(cpe.target_sw, "win2003")
        self.assertEqual(cpe.target_hw, "x64")
        self.assertIsNone(cpe.other)

        # example 5
        cpe = CPE.from_string(
            "cpe:/a:hp:openview_network_manager:7.51:-:~~~linux~~"
        )
        self.assertTrue(cpe.is_uri_binding())
        self.assertFalse(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "hp")
        self.assertEqual(cpe.product, "openview_network_manager")
        self.assertEqual(cpe.version, "7\.51")
        self.assertEqual(cpe.update, NA)
        self.assertIsNone(cpe.language)
        self.assertIsNone(cpe.edition)
        self.assertIsNone(cpe.sw_edition)
        self.assertEqual(cpe.target_sw, "linux")
        self.assertIsNone(cpe.target_hw)
        self.assertIsNone(cpe.other)

        # example 6
        # with self.assertRaises(CPEParsingError):
        #     CPE.from_string(
        #         "cpe:/a:foo%5cbar:big%24money_2010%07:::~~special~ipod_touch~80gb~"
        #     )

        # example 7
        cpe = CPE.from_string("cpe:/a:foo~bar:big%7emoney_2010")
        self.assertTrue(cpe.is_uri_binding())
        self.assertFalse(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "foo\~bar")
        self.assertEqual(cpe.product, "big\~money_2010")
        self.assertIsNone(cpe.version)
        self.assertIsNone(cpe.update)
        self.assertIsNone(cpe.language)
        self.assertIsNone(cpe.edition)
        self.assertIsNone(cpe.sw_edition)
        self.assertIsNone(cpe.target_sw)
        self.assertIsNone(cpe.target_hw)
        self.assertIsNone(cpe.other)

        # example 8
        with self.assertRaisesRegex(
            CPEParsingError,
            "^Percent-encoded asterisk is no at the beginning or the end "
            "of '12.%02.1234'$",
        ):
            CPE.from_string("cpe:/a:foo:bar:12.%02.1234")

    def test_formatted_bind_examples(self):
        # test examples from https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7695.pdf

        # example 1
        cpe = CPE(
            part=Part.APPLICATION,
            vendor="microsoft",
            product="internet_explorer",
            version="8\.0\.6001",
            update="beta",
            edition=ANY,
        )
        self.assertEqual(
            cpe.as_formatted_string_binding(),
            "cpe:2.3:a:microsoft:internet_explorer:8.0.6001:beta:*:*:*:*:*:*",
        )

        # example 2
        cpe = CPE(
            part=Part.APPLICATION,
            vendor="microsoft",
            product="internet_explorer",
            version="8\.*",
            update="sp?",
            edition=ANY,
        )
        self.assertEqual(
            cpe.as_formatted_string_binding(),
            "cpe:2.3:a:microsoft:internet_explorer:8.*:sp?:*:*:*:*:*:*",
        )

        cpe = CPE(
            part=Part.APPLICATION,
            vendor="microsoft",
            product="internet_explorer",
            version="8\.\*",
            update="sp?",
        )
        self.assertEqual(
            cpe.as_formatted_string_binding(),
            "cpe:2.3:a:microsoft:internet_explorer:8.\*:sp?:*:*:*:*:*:*",
        )

        # example 3
        cpe = CPE(
            part=Part.APPLICATION,
            vendor="hp",
            product="insight",
            version="7\.4\.0\.1570",
            update=NA,
            sw_edition="online",
            target_sw="win2003",
            target_hw="x64",
        )
        self.assertEqual(
            cpe.as_formatted_string_binding(),
            "cpe:2.3:a:hp:insight:7.4.0.1570:-:*:*:online:win2003:x64:*",
        )

        # example 4
        cpe = CPE(
            part=Part.APPLICATION,
            vendor="hp",
            product="openview_network_manager",
            version="7\.51",
            target_sw="linux",
        )
        self.assertEqual(
            cpe.as_formatted_string_binding(),
            "cpe:2.3:a:hp:openview_network_manager:7.51:*:*:*:*:linux:*:*",
        )

        # example 5
        cpe = CPE(
            part=Part.APPLICATION,
            vendor="foo\\\\bar",
            product="big\$money_2010",
            sw_edition="special",
            target_sw="ipod_touch",
            target_hw="80gb",
        )
        self.assertEqual(
            cpe.as_formatted_string_binding(),
            "cpe:2.3:a:foo\\\\bar:big\$money_2010:*:*:*:*:special:ipod_touch:80gb:*",
        )

    def test_formatted_unbind_examples(self):
        # test examples from https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7695.pdf

        # example 1
        cpe = CPE.from_string(
            "cpe:2.3:a:microsoft:internet_explorer:8.0.6001:beta:*:*:*:*:*:*"
        )
        self.assertFalse(cpe.is_uri_binding())
        self.assertTrue(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "microsoft")
        self.assertEqual(cpe.product, "internet_explorer")
        # self.assertEqual(cpe.version, "8\.0\.6001")
        self.assertEqual(cpe.update, "beta")
        self.assertEqual(cpe.language, ANY)
        self.assertEqual(cpe.edition, ANY)
        self.assertEqual(cpe.sw_edition, ANY)
        self.assertEqual(cpe.target_sw, ANY)
        self.assertEqual(cpe.target_hw, ANY)
        self.assertEqual(cpe.other, ANY)

        # example 2
        cpe = CPE.from_string(
            "cpe:2.3:a:microsoft:internet_explorer:8.*:sp?:*:*:*:*:*:*"
        )
        self.assertFalse(cpe.is_uri_binding())
        self.assertTrue(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "microsoft")
        self.assertEqual(cpe.product, "internet_explorer")
        self.assertEqual(cpe.version, "8\.*")
        self.assertEqual(cpe.update, "sp?")
        self.assertEqual(cpe.language, ANY)
        self.assertEqual(cpe.edition, ANY)
        self.assertEqual(cpe.sw_edition, ANY)
        self.assertEqual(cpe.target_sw, ANY)
        self.assertEqual(cpe.target_hw, ANY)
        self.assertEqual(cpe.other, ANY)

        # example 3
        cpe = CPE.from_string(
            "cpe:2.3:a:hp:insight_diagnostics:7.4.0.1570:-:*:*:online:win2003:x64:*"
        )
        self.assertFalse(cpe.is_uri_binding())
        self.assertTrue(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "hp")
        self.assertEqual(cpe.product, "insight_diagnostics")
        self.assertEqual(cpe.version, "7\.4\.0\.1570")
        self.assertEqual(cpe.update, NA)
        self.assertEqual(cpe.language, ANY)
        self.assertEqual(cpe.edition, ANY)
        self.assertEqual(cpe.sw_edition, "online")
        self.assertEqual(cpe.target_sw, "win2003")
        self.assertEqual(cpe.target_hw, "x64")
        self.assertEqual(cpe.other, ANY)

        with self.assertRaisesRegex(
            CPEParsingError,
            "^An unquoted asterisk must appear at the beginning or end of "
            "'7.4.*.1570'$",
        ):
            # embedded unquoted asterisk in the version attribute
            CPE.from_string(
                "cpe:2.3:a:hp:insight_diagnostics:7.4.*.1570:*:*:*:*:*:*"
            )

        # example 4
        cpe = CPE.from_string(
            "cpe:2.3:a:foo\\\\bar:big\$money:2010:*:*:*:special:ipod_touch:80gb:*"
        )
        self.assertFalse(cpe.is_uri_binding())
        self.assertTrue(cpe.is_formatted_string_binding())
        self.assertEqual(cpe.part, Part.APPLICATION)
        self.assertEqual(cpe.vendor, "foo\\\\bar")
        self.assertEqual(cpe.product, "big\$money")
        self.assertEqual(cpe.version, "2010")
        self.assertEqual(cpe.update, ANY)
        self.assertEqual(cpe.edition, ANY)
        self.assertEqual(cpe.language, ANY)
        self.assertEqual(cpe.sw_edition, "special")
        self.assertEqual(cpe.target_sw, "ipod_touch")
        self.assertEqual(cpe.target_hw, "80gb")
        self.assertEqual(cpe.other, ANY)

    def test_as_uri_binding(self):
        cpe_string = "cpe:2.3:a:microsoft:internet_explorer:8\\.*:sp?"
        cpe = CPE.from_string(cpe_string)
        self.assertEqual(
            cpe.as_uri_binding(),
            "cpe:/a:microsoft:internet_explorer:8.%02:sp%01",
        )

    def test_as_uri_binding_with_edition(self):
        cpe_string = "cpe:2.3:a:hp:insight_diagnostics:7.4.0.1570:-:*:*:online:win2003:x64"
        cpe = CPE.from_string(cpe_string)

        self.assertEqual(
            cpe.as_uri_binding(),
            "cpe:/a:hp:insight_diagnostics:7.4.0.1570:-:~~online~win2003~x64~",
        )

    def test_parse_error(self):
        with self.assertRaisesRegex(
            CPEParsingError,
            "^Invalid CPE string 'foo/bar'. CPE does not start with 'cpe:/' "
            "or 'cpe:2.3'$",
        ):
            CPE.from_string("foo/bar")

    def test_str(self):
        cpe = CPE(part=Part.APPLICATION, vendor="foo", product="bar")
        self.assertEqual(str(cpe), "cpe:/a:foo:bar")

        cpe = CPE(
            part=Part.APPLICATION,
            vendor="foo",
            product="bar",
            target_sw="ipsum",
        )
        self.assertEqual(str(cpe), "cpe:2.3:a:foo:bar:*:*:*:*:*:ipsum:*:*")

        cpe = CPE(
            cpe_string="cpe:2.3:a:foo:bar",
            part=Part.APPLICATION,
            vendor="foo",
            product="bar",
        )
        self.assertEqual(str(cpe), "cpe:2.3:a:foo:bar")

    def test_has_extended_attribute(self):
        cpe = CPE(part=Part.APPLICATION, vendor="foo", product="bar")
        self.assertFalse(cpe.has_extended_attribute())

        cpe = CPE(
            part=Part.APPLICATION,
            vendor="foo",
            product="bar",
            target_sw="ipsum",
        )
        self.assertTrue(cpe.has_extended_attribute())
