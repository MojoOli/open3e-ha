from enum import StrEnum
from typing import Any


class DhwHysteresis(StrEnum):
    On = "SetpointSwitchOn"
    Off = "SetpointSwitchOff"


def get_hysteresis_setpoint(data: Any, hysteresis: DhwHysteresis) -> float | None:
    """Return a hysteresis setpoint, or None for raw payloads from older Open3e releases (e.g. DID 1593)."""
    if not isinstance(data, dict):
        return None
    value = data.get(hysteresis)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value
