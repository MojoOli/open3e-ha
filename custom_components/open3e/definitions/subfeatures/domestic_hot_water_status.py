from enum import StrEnum
from typing import Any

from homeassistant.util.json import json_loads


class DomesticHotWaterStatus(StrEnum):
    IDLE = "idle"
    ACTIVE = "active"
    POSTRUN = "postrun"


DOMESTIC_HOT_WATER_STATUS_MAP = {
    0: DomesticHotWaterStatus.IDLE,
    1: DomesticHotWaterStatus.ACTIVE,
    2: DomesticHotWaterStatus.POSTRUN,
}


def get_domestic_hot_water_status(data: Any) -> DomesticHotWaterStatus | None:
    """Parse legacy integer payloads and new JSON payloads for feature 2320."""
    try:
        if isinstance(data, str) and data.strip().startswith("{"):
            payload = json_loads(data)
            # DomesticHotWaterStatus often comes as an enum complex type
            raw_id = payload.get("ID") if payload.get("ID") is not None else payload.get("State", {}).get("ID")
            if raw_id is None:
                return None
            value = int(raw_id)
        else:
            # Legacy format (simple integer or byte)
            value = int(data)
        return DOMESTIC_HOT_WATER_STATUS_MAP.get(value)
    except (TypeError, ValueError, KeyError):
        return None
