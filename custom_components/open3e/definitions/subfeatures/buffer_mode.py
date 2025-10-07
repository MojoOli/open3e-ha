from enum import StrEnum


class BufferMode(StrEnum):
    Heating = "heating"
    Cooling = "cooling"

    @staticmethod
    def from_operation_mode(mode: int):
        match mode:
            case 0:
                return BufferMode.Heating
            case 1:
                return BufferMode.Cooling

        return None

    @staticmethod
    def from_str(mode: str):
        match mode:
            case BufferMode.Heating:
                return BufferMode.Heating
            case BufferMode.Cooling:
                return BufferMode.Cooling

        return None

    def map_to_api(self):
        match self:
            case BufferMode.Heating:
                return 0
            case BufferMode.Cooling:
                return 1
