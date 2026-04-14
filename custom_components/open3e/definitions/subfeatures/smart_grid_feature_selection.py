from enum import StrEnum
from typing import Any


class SmartGridFeatureSelection(StrEnum):
    DOMESTIC_HOT_WATER = "domestic_hot_water"
    HEATING_BUFFER = "heating_buffer"
    ROOM_HEATING = "room_heating"
    ROOM_COOLING = "room_cooling"


SMART_GRID_FEATURE_SELECTION_MAP: dict[int, SmartGridFeatureSelection] = {
    1: SmartGridFeatureSelection.DOMESTIC_HOT_WATER,
    2: SmartGridFeatureSelection.HEATING_BUFFER,
    4: SmartGridFeatureSelection.ROOM_HEATING,
    8: SmartGridFeatureSelection.ROOM_COOLING,
}


def get_smart_grid_feature_selection(data: Any) -> SmartGridFeatureSelection | None:
    """Parse integer payload for feature 2560."""
    try:
        value = int(data)
        return SMART_GRID_FEATURE_SELECTION_MAP.get(value)
    except (TypeError, ValueError):
        return None
