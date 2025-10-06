from enum import StrEnum

from homeassistant.components.water_heater import STATE_ECO, STATE_PERFORMANCE
from homeassistant.const import STATE_OFF


class DmwMode(StrEnum):
    Off = "Off"
    Eco = "Eco"
    Comfort = "Comfort"

    @staticmethod
    def from_ha_preset_mode(text: str):
        match text:
            case "eco":
                return DmwMode.Eco
            case "performance":
                return DmwMode.Comfort
            case "off":
                return DmwMode.Off

        return None

    def to_ha_preset_mode(self):
        return HA_PRESET_HEATING[self]


HA_PRESET_HEATING = {
    DmwMode.Eco: STATE_ECO,
    DmwMode.Comfort: STATE_PERFORMANCE,
    DmwMode.Off: STATE_OFF
}
