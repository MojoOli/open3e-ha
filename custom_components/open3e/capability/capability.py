from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from custom_components.open3e.const import VIESSMANN_UNAVAILABLE_VALUE
from custom_components.open3e.definitions.devices import Open3eDevices, Device
from custom_components.open3e.definitions.features import Features, Feature
from custom_components.open3e.definitions.subfeatures.temperature_cooling import TemperatureCooling


class Capability(Enum):
    Cooling = auto()
    Room1Temperature = auto()
    Room2Temperature = auto()
    Room3Temperature = auto()
    Room4Temperature = auto()
    Fan2 = auto()
    HeatingCircuit2 = auto()
    HeatingCircuit3 = auto()
    HeatingCircuit4 = auto()


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
            capability=Capability.Cooling,
            feature=Features.Temperature.FlowCircuit1Cooling,
            path=TemperatureCooling.EffectiveSetTemperature,
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        ),
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
            capability=Capability.HeatingCircuit2,
            feature=Features.Temperature.FlowCircuit2,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.HeatingCircuit3,
            feature=Features.Temperature.FlowCircuit3,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        ),
        CapabilityFeature(
            capability=Capability.HeatingCircuit4,
            feature=Features.Temperature.FlowCircuit4,
            path="Actual",
            invalid_value=VIESSMANN_UNAVAILABLE_VALUE
        )
    ],
    Open3eDevices.Vitoair: [],
    Open3eDevices.Vitodens: [],
    Open3eDevices.Vitocharge: []
}
