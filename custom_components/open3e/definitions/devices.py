from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Device:
    id: str
    display_name: str


class Open3eDevices(Device, Enum):
    Vitocal = ("HPMU", "Vitocal")
    Vitoair = ("VCU", "Vitoair")
    Vitodens = ("HMU", "Vitodens")
    Vitocharge = ("EMCU", "Vitocharge")

    def __init__(self, id: str, display_name: str):
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "display_name", display_name)
