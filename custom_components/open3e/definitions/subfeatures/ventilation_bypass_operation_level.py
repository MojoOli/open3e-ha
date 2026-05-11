from enum import StrEnum
from typing import Any


class VentilationBypassOperationLevel(StrEnum):
    NOISE_REDUCED = "noise_reduced"
    DYNAMIC = "dynamic"


VENTILATION_BYPASS_OPERATION_LEVEL_MAP: dict[int, VentilationBypassOperationLevel] = {
    1: VentilationBypassOperationLevel.NOISE_REDUCED,
    2: VentilationBypassOperationLevel.DYNAMIC,
}


def get_ventilation_bypass_operation_level(data: Any) -> VentilationBypassOperationLevel | None:
    """Parse integer payload for feature 2403."""
    try:
        value = int(float(data))
        return VENTILATION_BYPASS_OPERATION_LEVEL_MAP.get(value)
    except (TypeError, ValueError):
        return None
