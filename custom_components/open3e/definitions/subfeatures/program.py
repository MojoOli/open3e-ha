from enum import StrEnum


class Program(StrEnum):
    Off = "off_mode"
    Reduced = "reduced"
    Normal = "normal"
    Comfort = "comfort"
    FixedValue = "fixed_value"
    FrostProtection = "frost_protection"
    EcoReduced = "eco_reduced"
    EcoNormal = "eco_normal"
    EcoComfort = "eco_comfort"

    @staticmethod
    def from_operation_mode(mode: int):
        match mode:
            case 0:
                return Program.Off
            case 1:
                return Program.Reduced
            case 2:
                return Program.Normal
            case 3:
                return Program.Comfort
            case 4:
                return Program.FixedValue
            case 5:
                return Program.FrostProtection
            case 6:
                return Program.EcoReduced
            case 7:
                return Program.EcoNormal
            case 8:
                return Program.Comfort

        return None

    def map_to_api_heating(self):
        match self:
            case Program.Off:
                return "Reduced"
            case Program.Reduced:
                return "Reduced"
            case Program.FrostProtection:
                return "Reduced"
            case Program.Comfort:
                return "Comfort"

        return "Standard"

    def map_to_api_cooling(self):
        match self:
            case Program.Off:
                return "Reduced"
            case Program.Reduced:
                return "Reduced"
            case Program.FrostProtection:
                return "Reduced"
            case Program.Comfort:
                return "Comfort"

        return "Normal"
