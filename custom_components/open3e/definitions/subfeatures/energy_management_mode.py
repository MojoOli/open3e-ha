from enum import StrEnum


class EnergyManagementMode(StrEnum):
    SHUTDOWN = "shutdown_mode"
    NORMAL = "normal_mode"
    PREFERRED = "preferred_mode"
    FORCED = "forced_mode"


# Map numeric CAN values to the Enum
ENERGY_MANAGEMENT_MODES_MAP = {
    1: EnergyManagementMode.SHUTDOWN,
    2: EnergyManagementMode.NORMAL,
    3: EnergyManagementMode.PREFERRED,
    4: EnergyManagementMode.FORCED
}
