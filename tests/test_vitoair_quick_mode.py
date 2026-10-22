"""Tests for the Vitoair quick mode parser (DID 1007).

Samples are from a Vitoair FS 300, see https://github.com/MojoOli/open3e-ha/issues/63 and #97.
"""

from __future__ import annotations

import unittest

from custom_components.open3e.definitions.subfeatures.vitoair_quick_mode import (
    VitoairQuickMode,
    get_vitoair_quick_mode,
)


class VitoairQuickModeTest(unittest.TestCase):
    def test_decoded(self) -> None:
        self.assertEqual(
            get_vitoair_quick_mode('{"OpMode": 8, "Required": "on", "Runtime": 90.0, "Unknown": "0000"}'),
            VitoairQuickMode.Intensive,
        )
        self.assertEqual(
            get_vitoair_quick_mode('{"OpMode": 9, "Required": "on", "Runtime": 5.0, "Unknown": "0000"}'),
            VitoairQuickMode.ReducedNoise,
        )
        self.assertEqual(
            get_vitoair_quick_mode('{"OpMode": 0, "Required": "off", "Runtime": 0.0, "Unknown": "0000"}'),
            VitoairQuickMode.Nothing,
        )

    def test_not_required_is_nothing(self) -> None:
        self.assertEqual(
            get_vitoair_quick_mode('{"OpMode": 8, "Required": "off", "Runtime": 0.0, "Unknown": "0000"}'),
            VitoairQuickMode.Nothing,
        )

    def test_raw_hex_is_unavailable(self) -> None:
        # Open3e without the 6-byte Vitoair codec publishes raw hex; writes would fail there.
        self.assertIsNone(get_vitoair_quick_mode('"080105000000"'))
        self.assertIsNone(get_vitoair_quick_mode('"000000000000"'))

    def test_bad_input(self) -> None:
        self.assertIsNone(get_vitoair_quick_mode('{"OpMode": 8}'))
        self.assertIsNone(get_vitoair_quick_mode("not json"))


if __name__ == "__main__":
    unittest.main()
