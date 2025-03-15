"""Types for open3e"""
from dataclasses import dataclass
from typing import Any

from .devices import OPEN3E_DEVICES


@dataclass(frozen=True)
class Open3eDataDeviceFeature:
    id: int
    topic: str

    @staticmethod
    def from_dict(data: dict[str, Any]):
        return Open3eDataDeviceFeature(data.pop("id"), data.pop("topic"))


@dataclass(frozen=True)
class Open3eDataDevice:
    id: int
    name: str
    serial_number: str | None
    software_version: str | None
    hardware_version: str | None
    features: list[Open3eDataDeviceFeature]
    manufacturer: str = "Viessmann"

    @staticmethod
    def from_dict(data: dict[str, Any]):
        name = data.pop("name")

        device = next((device for key, device in OPEN3E_DEVICES.items() if key in name), None)

        if device is None:
            return None

        features_dict = data.pop("features")
        features: list[Open3eDataDeviceFeature] = []
        for feature_dict in features_dict:
            features.append(Open3eDataDeviceFeature.from_dict(feature_dict))

        device = Open3eDataDevice(data.pop("id"), device.name, data.pop("serial_number"), data.pop("software_version"),
                                  data.pop("hardware_version"), features)

        return device


@dataclass(frozen=True)
class Open3eDataSystemInformation:
    devices: list[Open3eDataDevice]

    @staticmethod
    def from_dict(data: dict[str, Any]):
        devices_dict: list[dict[str, Any]] = data.pop("devices")
        devices: list[Open3eDataDevice] = []

        for device_dict in devices_dict:
            device = Open3eDataDevice.from_dict(device_dict)
            if device is not None:
                devices.append(device)

        return Open3eDataSystemInformation(devices)
