"""Tests for the LAN gateway sensors (DIDs 592, 1696, 1697) and the WiFi/LAN entity selection.

See https://github.com/MojoOli/open3e-ha/issues/204.
"""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from custom_components.open3e.capability.capability import Capability
from custom_components.open3e.definitions.sensors import SENSORS
from custom_components.open3e.definitions.subfeatures.gateway_ethernet_ip import get_gateway_ethernet_ip
from custom_components.open3e.util import map_devices_to_entities

WIFI_KEYS = {"gateway_mac", "gateway_remote_local_network_status", "gateway_remote_ip", "gateway_remote_signal_strength"}
LAN_KEYS = {"gateway_ethernet_mac", "gateway_ethernet_network_status", "gateway_ethernet_ip"}


class GatewayEthernetIpTest(unittest.TestCase):
    def test_raw_hex(self) -> None:
        self.assertEqual(
            get_gateway_ethernet_ip('"0a0000eaffffff000a0000010a00000100000000"'),
            "10.0.0.234",
        )
        # Vitocal without a LAN module
        self.assertEqual(get_gateway_ethernet_ip('"0000000000000000000000000000000000000000"'), "0.0.0.0")

    def test_decoded(self) -> None:
        self.assertEqual(
            get_gateway_ethernet_ip('{"LAN_IP-Address": "010.000.000.234", "SubnetMask": "255.255.255.000"}'),
            "10.0.0.234",
        )

    def test_bad_input(self) -> None:
        self.assertIsNone(get_gateway_ethernet_ip('"zz"'))
        self.assertIsNone(get_gateway_ethernet_ip('"0a00"'))
        self.assertIsNone(get_gateway_ethernet_ip("{}"))
        self.assertIsNone(get_gateway_ethernet_ip("not json"))


class _Device(SimpleNamespace):
    """Hashable stand-in for Open3eDataDevice, which map_devices_to_entities uses as dict key."""
    __hash__ = object.__hash__


class GatewayEntitySelectionTest(unittest.TestCase):
    @staticmethod
    def __gateway_keys(capabilities: set[Capability]) -> set[str]:
        feature_ids = {f.id for sensor in SENSORS for f in (sensor.poll_data_features or [])}
        device = _Device(
            name="HPMU",
            features=[SimpleNamespace(id=feature_id) for feature_id in feature_ids],
            capabilities=capabilities,
        )
        coordinator = SimpleNamespace(system_information=SimpleNamespace(devices=[device]))
        keys = {entity.key for entity in map_devices_to_entities(coordinator, SENSORS)[device]}
        return keys & (WIFI_KEYS | LAN_KEYS)

    def test_wifi_without_ethernet(self) -> None:
        self.assertEqual(self.__gateway_keys(set()), WIFI_KEYS)

    def test_lan_with_ethernet(self) -> None:
        self.assertEqual(self.__gateway_keys({Capability.Ethernet}), LAN_KEYS)


if __name__ == "__main__":
    unittest.main()
