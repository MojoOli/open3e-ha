from enum import StrEnum


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
