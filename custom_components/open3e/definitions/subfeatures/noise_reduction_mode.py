from enum import StrEnum
from typing import Any


class NoiseReductionMode(StrEnum):
    NONE = "none"
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"


NOISE_REDUCTION_MODE_MAP: dict[int, NoiseReductionMode] = {
    0: NoiseReductionMode.NONE,
    1: NoiseReductionMode.LEVEL_1,
    2: NoiseReductionMode.LEVEL_2,
}


def get_noise_reduction_mode(data: Any) -> NoiseReductionMode | None:
    """Parse integer payload for feature 2634."""
    try:
        value = int(data)
        return NOISE_REDUCTION_MODE_MAP.get(value)
    except (TypeError, ValueError):
        return None
