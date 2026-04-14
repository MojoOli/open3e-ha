from enum import StrEnum


class SmartGridReadyStatus(StrEnum):
    LOCKED = "locked"
    NORMAL = "normal"
    PV_RECOMMENDED = "pv_recommended"
    HIGH_TEMPERATURE = "high_temperature"


SMART_GRID_READY_STATUS_MAP: dict[int, SmartGridReadyStatus] = {
    0: SmartGridReadyStatus.LOCKED,
    1: SmartGridReadyStatus.NORMAL,
    2: SmartGridReadyStatus.PV_RECOMMENDED,
    3: SmartGridReadyStatus.HIGH_TEMPERATURE,
}
