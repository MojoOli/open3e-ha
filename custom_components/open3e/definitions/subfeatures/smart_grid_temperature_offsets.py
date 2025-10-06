from enum import StrEnum


class SmartGridTemperatureOffsets(StrEnum):
    IncreaseRoomTemperatureHeating = "SetpointIncreaseRoomTemperatureHeating"
    DecreaseRoomTemperatureCooling = "SetpointDecreaseRoomTemperatureCooling"
    IncreaseBufferTemperatureHeating = "SetpointIncreaseBufferTemperatureHeating"
    DecreaseBufferTemperatureCooling = "SetpointDecreaseBufferTemperatureCooling"
    IncreaseDHWTemperature = "SetpointIncreaseDHWTemperature"
