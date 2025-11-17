from enum import StrEnum

from homeassistant.components.climate import HVACMode


class HvacMode(StrEnum):
    Off = "Off"
    Heating = "Eco"
    Cooling = "Comfort"
    Auto = "Auto"

    @staticmethod
    def from_ha_hvac_mode(hvac_mode: HVACMode):
        match hvac_mode:
            case HVACMode.OFF:
                return HvacMode.Off
            case HVACMode.HEAT:
                return HvacMode.Heating
            case HVACMode.COOL:
                return HvacMode.Cooling

        return HvacMode.Auto

    @staticmethod
    def from_api(id: int):
        match id:
            case 0:
                return HvacMode.Off
            case 1:
                return HvacMode.Heating
            case 5:
                return HvacMode.Cooling
            case _:
                return HvacMode.Auto

    def to_api(self):
        match self:
            case HvacMode.Off:
                return {"Mode": {"ID": 0, "Text": "Off"}, "State": {"ID": 12, "Text": "No request"}}
            case HvacMode.Heating:
                return {"Mode": {"ID": 1, "Text": "Heating"}, "State": {"ID": 12, "Text": "No request"}}
            case HvacMode.Cooling:
                return {"Mode": {"ID": 5, "Text": "Cooling"}, "State": {"ID": 12, "Text": "No request"}}
            case _:
                return {"Mode": {"ID": 0, "Text": "Off"}, "State": {"ID": 12, "Text": "No request"}}

    def to_ha_hvac_mode(self):
        match self:
            case HvacMode.Off:
                return HVACMode.OFF
            case HvacMode.Heating:
                return HVACMode.HEAT
            case HvacMode.Cooling:
                return HVACMode.COOL

        return HVACMode.AUTO
