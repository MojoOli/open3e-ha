"""Tests for Vitoair payload parsers that must accept old (raw hex) and new (decoded) Open3e formats.

Samples are from a Vitoair FS 300, see https://github.com/MojoOli/open3e-ha/issues/63.
"""

from __future__ import annotations

import unittest

from custom_components.open3e.definitions.subfeatures.first_byte_value import get_first_byte_value
from custom_components.open3e.definitions.subfeatures.frost_protection_status import is_frost_protection_active
from custom_components.open3e.definitions.subfeatures.ventilation_volume_flow import get_exhaust_air_volume_flow


class FrostProtectionStatusTest(unittest.TestCase):
    def test_raw_hex(self) -> None:
        self.assertFalse(is_frost_protection_active('"000000"'))
        self.assertTrue(is_frost_protection_active('"013e00"'))
        self.assertTrue(is_frost_protection_active('"010000"'))

    def test_decoded(self) -> None:
        self.assertFalse(is_frost_protection_active('{"Status": "off", "Unknown": "0000"}'))
        self.assertTrue(is_frost_protection_active('{"Status": "on", "Unknown": "3e00"}'))

    def test_bad_input(self) -> None:
        self.assertIsNone(is_frost_protection_active('{"Unknown": "0000"}'))
        self.assertIsNone(is_frost_protection_active('"zz"'))
        self.assertIsNone(is_frost_protection_active("not json"))


class FirstByteValueTest(unittest.TestCase):
    def test_raw_hex(self) -> None:
        self.assertEqual(get_first_byte_value('"5800"'), 88.0)  # 3206 FilterPercentageBlocked
        self.assertEqual(get_first_byte_value('"03"'), 3.0)  # 2846 VentilationBypassDynamicVentilationLevel

    def test_decoded(self) -> None:
        self.assertEqual(get_first_byte_value("88.0"), 88.0)
        self.assertEqual(get_first_byte_value("3"), 3.0)

    def test_bad_input(self) -> None:
        self.assertIsNone(get_first_byte_value('"zz"'))
        self.assertIsNone(get_first_byte_value('{"Value": 1}'))
        self.assertIsNone(get_first_byte_value("null"))


class ExhaustAirVolumeFlowTest(unittest.TestCase):
    def test_named_field(self) -> None:
        self.assertEqual(get_exhaust_air_volume_flow('{"TargetFlow": 160.0, "ExhaustFlow": 154.0}'), 154.0)

    def test_unknown_raw_hex(self) -> None:
        self.assertEqual(get_exhaust_air_volume_flow('{"TargetFlow": 160.0, "Unknown": "9a00"}'), 154.0)
        self.assertEqual(get_exhaust_air_volume_flow('{"TargetFlow": 160.0, "Unknown": "0901"}'), 265.0)

    def test_unknown_decoded(self) -> None:
        self.assertEqual(get_exhaust_air_volume_flow('{"TargetFlow": 160.0, "Unknown": 154}'), 154.0)

    def test_bad_input(self) -> None:
        self.assertIsNone(get_exhaust_air_volume_flow('{"TargetFlow": 160.0}'))
        self.assertIsNone(get_exhaust_air_volume_flow('{"Unknown": "zz"}'))
        self.assertIsNone(get_exhaust_air_volume_flow('"a0009a00"'))
        self.assertIsNone(get_exhaust_air_volume_flow("not json"))


if __name__ == "__main__":
    unittest.main()
