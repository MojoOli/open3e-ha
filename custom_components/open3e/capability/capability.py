from enum import Enum, auto

from custom_components.open3e.definitions.devices import Open3eDevices, Device
from custom_components.open3e.definitions.features import Features


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


DEVICE_CAPABILITIES: dict[Device, set[Capability]] = {
    Open3eDevices.Vitocal: {
        Capability.Cooling,
        Capability.Room1Temperature,
        Capability.Room2Temperature,
        Capability.Room3Temperature,
        Capability.Room4Temperature,
        Capability.Fan2,
        Capability.HeatingCircuit2,
        Capability.HeatingCircuit3,
        Capability.HeatingCircuit4
    },
    Open3eDevices.Vitoair: {},
    Open3eDevices.Vitodens: {},
    Open3eDevices.Vitocharge: {},
}

CAPABILITY_FEATURE_MAP = {
    Capability.Cooling: Features.Temperature.FlowCircuit1Cooling,
    Capability.Room1Temperature: Features.Temperature.Room1,
    Capability.Room2Temperature: Features.Temperature.Room2,
    Capability.Room3Temperature: Features.Temperature.Room3,
    Capability.Room4Temperature: Features.Temperature.Room4,
    Capability.Fan2: Features.Power.Fan2,
    Capability.HeatingCircuit2: Features.Temperature.FlowCircuit2,
    Capability.HeatingCircuit3: Features.Temperature.FlowCircuit3,
    Capability.HeatingCircuit4: Features.Temperature.FlowCircuit4,
}
