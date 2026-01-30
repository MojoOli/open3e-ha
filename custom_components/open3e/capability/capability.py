from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from custom_components.open3e.const import VIESSMANN_UNAVAILABLE_VALUE, VITODENS_UNAVAILABLE_VALUE
from custom_components.open3e.definitions.devices import Open3eDevices, Device
from custom_components.open3e.definitions.features import Features, Feature


class Capability(Enum):
    Room1Temperature = auto()
    Room2Temperature = auto()
    Room3Temperature = auto()
    Room4Temperature = auto()
    Fan2 = auto()
    Circuit1 = auto()
    Circuit2 = auto()
    Circuit3 = auto()
    Circuit4 = auto()
    BackupBox = auto()


@dataclass(frozen=True)
class CapabilityFeature:
    capability: Capability
    feature: Feature
    path: str | None
    invalid_value: Any

    def evaluate(self, data: Any) -> bool:
        if self.path is None:
            return data != self.invalid_value
        else:
            return data[self.path] != self.invalid_value


DEVICE_CAPABILITIES: dict[Device, list[CapabilityFeature]] = {
    Open3eDevices.Vitocal: [
        CapabilityFeature(
            capability=Capability.Room1Temperature,
            feature=Features.Temperature.Room1,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.Room2Temperature,
            feature=Features.Temperature.Room2,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.Room3Temperature,
            feature=Features.Temperature.Room3,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.Room4Temperature,
            feature=Features.Temperature.Room4,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.Fan2,
            feature=Features.Power.Fan2,
            path=None,
            invalid_value=255
        ),
        CapabilityFeature(
            capability=Capability.Circuit1,
            feature=Features.Temperature.FlowCircuit1,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.Circuit2,
            feature=Features.Temperature.FlowCircuit2,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.Circuit3,
            feature=Features.Temperature.FlowCircuit3,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.Circuit4,
            feature=Features.Temperature.FlowCircuit4,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        )
    ],
    Open3eDevices.Vitoair: [],
    Open3eDevices.Vitodens: [
        CapabilityFeature(
            capability=Capability.Circuit1,
            feature=Features.Temperature.FlowCircuit1,
            path="Actual",
            invalid_value=VITODENS_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.Circuit2,
            feature=Features.Temperature.FlowCircuit2,
            path="Actual",
            invalid_value=VITODENS_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.Circuit3,
            feature=Features.Temperature.FlowCircuit3,
            path="Actual",
            invalid_value=VITODENS_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.Circuit4,
            feature=Features.Temperature.FlowCircuit4,
            path="Actual",
            invalid_value=VITODENS_UNAVAILABLE_VALUE
        )
    ],
    Open3eDevices.Vitocharge: [
        CapabilityFeature(
            capability=Capability.BackupBox,
            feature=Features.State.BackUpBox,
            path="Unknown",  # TODO: Needs to be renamed when open3e is updated to BackUpBoxInstalled
            invalid_value=0 # 0 = not installed, 1 = installed
        )
    ]
}
