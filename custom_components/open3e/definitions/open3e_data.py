"""Types for open3e"""
from dataclasses import dataclass
from typing import Any

from .devices import Open3eDevices
from ..capability.capability import Capability


@dataclass(frozen=True)
class Open3eDataDeviceFeature:
    id: int
    topic: str

    @staticmethod
    def from_dict(data: dict[str, Any]):
        return Open3eDataDeviceFeature(data.pop("id"), data.pop("topic"))


class Open3eDataDevice:
    id: int
    name: str
    serial_number: str
    software_version: str | None
    hardware_version: str | None
    features: tuple[Open3eDataDeviceFeature, ...]
    capabilities: set[Capability]

    def __init__(
            self,
            id: int,
            name: str,
            serial_number: str,
            software_version: str,
            hardware_version: str,
            features: tuple[Open3eDataDeviceFeature, ...]
    ):
        self.id = id
        self.name = name
        self.serial_number = serial_number
        self.software_version = software_version
        self.hardware_version = hardware_version
        self.features = features
        self.manufacturer = "Viessmann"
        self.capabilities = set()

    @staticmethod
    def from_dict(data: dict[str, Any]):
        name = data.pop("name")

        device = next((dev for dev in Open3eDevices if dev.id in name), None)

        if device is None:
            return None

        features_dict = data.pop("features")
        features = tuple(
            Open3eDataDeviceFeature.from_dict(feature_dict)
            for feature_dict in features_dict
        )

        device = Open3eDataDevice(
            id=data.pop("id"),
            name=device.display_name,
            serial_number=data.pop("serial_number"),
            software_version=data.pop("software_version"),
            hardware_version=data.pop("hardware_version"),
            features=features
        )

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
