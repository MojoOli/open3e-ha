from enum import StrEnum
from typing import Any

from homeassistant.util.json import json_loads


class DomesticHotWaterOperationState(StrEnum):
    OFF = "off"
    HOT_WATER = "hot_water"
    PARALLEL_OPERATION = "parallel_operation"
    CHIMNEY_SWEEP = "chimney_sweep"
    TEST_MODE = "test_mode"
    EXTERNAL_TEMPERATURE_SETPOINT = "external_temperature_setpoint"
    EXTERNAL_MODULATION_SETPOINT = "external_modulation_setpoint"
    HYGIENE_FUNCTION = "hygiene_function"
    AUTOMATIC = "automatic"


DOMESTIC_HOT_WATER_OPERATION_STATE_MAP = {
    0: DomesticHotWaterOperationState.OFF,
    1: DomesticHotWaterOperationState.HOT_WATER,
    2: DomesticHotWaterOperationState.PARALLEL_OPERATION,
    3: DomesticHotWaterOperationState.CHIMNEY_SWEEP,
    4: DomesticHotWaterOperationState.TEST_MODE,
    5: DomesticHotWaterOperationState.EXTERNAL_TEMPERATURE_SETPOINT,
    6: DomesticHotWaterOperationState.EXTERNAL_MODULATION_SETPOINT,
    7: DomesticHotWaterOperationState.HYGIENE_FUNCTION,
    8: DomesticHotWaterOperationState.AUTOMATIC,
}


def get_domestic_hot_water_operation_state(data: Any) -> DomesticHotWaterOperationState | None:
    """Parse legacy integer payloads and new JSON payloads for feature 531."""
    try:
        if isinstance(data, str):
            stripped = data.strip()

            # New format: {"Mode": 0, "State": {"ID": 1, "Text": "Hot water"}}
            if stripped.startswith("{"):
                payload = json_loads(stripped)
                state_data = payload.get("State")
                if isinstance(state_data, dict):
                    state_id = int(state_data.get("ID", -1))
                elif isinstance(state_data, (str, int, float)):
                    state_id = int(state_data)
                else:
                    state_id = -1
            else:
                # Legacy format: 1
                state_id = int(stripped)
        else:
            state_id = int(data)
    except (TypeError, ValueError, KeyError, AttributeError):
        return None

    return DOMESTIC_HOT_WATER_OPERATION_STATE_MAP.get(state_id)


def is_domestic_hot_water_operation_state_active(data: Any) -> bool:
    """Determine if DHW operation state is active for binary sensor (legacy and new)."""
    state = get_domestic_hot_water_operation_state(data)
    if state is None:
        return False
    return state != DomesticHotWaterOperationState.OFF
