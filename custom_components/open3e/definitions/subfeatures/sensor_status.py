from enum import StrEnum
from typing import Any

from homeassistant.util.json import json_loads


class SensorStatus(StrEnum):
    NO_ERROR = "no_error"
    INTERRUPTION = "interruption"
    SHORT_CIRCUIT = "short_circuit"
    ELECTRICAL_FAULT = "electrical_fault"
    NOT_AVAILABLE = "not_available"
    INVALIDATES = "invalidates"


SENSOR_STATUS_MAP: dict[int, SensorStatus] = {
    0: SensorStatus.NO_ERROR,
    1: SensorStatus.INTERRUPTION,
    2: SensorStatus.SHORT_CIRCUIT,
    3: SensorStatus.ELECTRICAL_FAULT,
    4: SensorStatus.NOT_AVAILABLE,
    5: SensorStatus.INVALIDATES,
}


def get_sensor_status(data: Any) -> SensorStatus | None:
    """Parse the "SensorStatus" field (Open3e enum "SensorStates") of a complex sensor payload, e.g. feature 3170."""
    try:
        payload = json_loads(data) if isinstance(data, str) else data
        status = payload["SensorStatus"]
        # Enum as {"ID": n, "Text": ".."} or, in older formats, a plain value
        raw_id = status.get("ID") if isinstance(status, dict) else status
        return SENSOR_STATUS_MAP.get(int(raw_id))
    except (TypeError, ValueError, KeyError, AttributeError):
        return None
