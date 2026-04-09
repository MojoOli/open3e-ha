from enum import StrEnum
from typing import Any

from homeassistant.util.json import json_loads


class FourThreeWayValvePosition(StrEnum):
    BUFFER = "buffer"
    IDLE = "idle"
    HOT_WATER = "hot_water"


# Map numeric CAN values to the Enum
FOUR_THREE_WAY_VALVE_POSITION_MAP = {
    0: FourThreeWayValvePosition.BUFFER,
    1: FourThreeWayValvePosition.IDLE,
    2: FourThreeWayValvePosition.HOT_WATER
}


def get_four_three_way_valve_position(data: Any) -> FourThreeWayValvePosition | None:
    """Parse legacy integer payloads and new JSON payloads for feature 2735."""
    try:
        if isinstance(data, str):
            stripped = data.strip()

            # New format: {"ID": 1, "Text": "Internal Buffer"}
            if stripped.startswith("{"):
                payload = json_loads(stripped)
                valve_id = int(payload.get("ID", -1))
            else:
                # Legacy format: 1
                valve_id = int(stripped)
        else:
            valve_id = int(data)
    except (TypeError, ValueError, KeyError, AttributeError):
        return None

    return FOUR_THREE_WAY_VALVE_POSITION_MAP.get(valve_id)
