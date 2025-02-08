from dataclasses import dataclass


@dataclass(frozen=True)
class Device:
    name: str


OPEN3E_DEVICES = {
    "HPMU": Device(name="Vitocal"),
    "VCU": Device(name="Vitoair"),
    "HMU": Device(name="Vitodens"),
    "EMCU": Device(name="Vitocharge"),
}
