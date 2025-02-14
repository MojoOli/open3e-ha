from enum import StrEnum

from homeassistant.components.climate import PRESET_COMFORT, PRESET_ECO, PRESET_HOME


class Program(StrEnum):
    Reduced = "Reduced"
    Standard = "Standard"
    Comfort = "Comfort"

    @staticmethod
    def from_text(text: str):
        match text:
            case Program.Reduced.name:
                return Program.Reduced
            case Program.Standard.name:
                return Program.Standard
            case Program.Comfort.name:
                return Program.Comfort
            case "Normal":
                return Program.Standard

        return None

    def to_ha_preset_mode(self):
        return HA_PRESET_HEATING[self]


HA_PRESET_HEATING = {
    Program.Reduced: PRESET_ECO,
    Program.Standard: PRESET_HOME,
    Program.Comfort: PRESET_COMFORT
}
