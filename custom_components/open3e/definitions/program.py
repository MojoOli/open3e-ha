from enum import StrEnum


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
