from enum import StrEnum
from json import loads as json_loads
from typing import Any


class RefrigerationCircuitOperationMode(StrEnum):
    OFF = "off"
    SHUTDOWN = "shutdown"
    HEATING = "heating"
    COOLING = "cooling"
    MANUAL = "manual"
    DEFROST = "defrost"
    GRID_LOCK = "grid_lock"


REFRIGERATION_CIRCUIT_OPERATION_MODES_MAP: dict[int, RefrigerationCircuitOperationMode] = {
    0: RefrigerationCircuitOperationMode.OFF,
    1: RefrigerationCircuitOperationMode.SHUTDOWN,
    2: RefrigerationCircuitOperationMode.HEATING,
    3: RefrigerationCircuitOperationMode.COOLING,
    4: RefrigerationCircuitOperationMode.MANUAL,
    5: RefrigerationCircuitOperationMode.DEFROST,
    6: RefrigerationCircuitOperationMode.GRID_LOCK,
}


def get_refrigeration_circuit_mode(data: Any) -> RefrigerationCircuitOperationMode | None:
    """Parse legacy and current JSON payloads for feature 2806."""
    try:
        if isinstance(data, str) and data.strip().startswith("{"):
            payload = json_loads(data)
            state = payload.get("State")
            if isinstance(state, dict):
                # Current format: {"State": {"ID": 1, ...}}
                raw_id = state.get("ID")
            else:
                # Legacy format: {"State": 1}
                raw_id = state

            if raw_id is None:
                return None
            value = int(raw_id)
            return REFRIGERATION_CIRCUIT_OPERATION_MODES_MAP.get(value)
        return None
    except (TypeError, ValueError, KeyError):
        return None
