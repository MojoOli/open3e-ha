from enum import StrEnum


class VitoairQuickMode(StrEnum):
    Intensive = "intensive"
    ReducedNoise = "reduced_noise"
    Off = "off"
    Nothing = "none"

    @staticmethod
    def from_operation_mode(mode: int):
        match mode:
            case 8:
                return VitoairQuickMode.Intensive
            case 9:
                return VitoairQuickMode.ReducedNoise
            case 12:
                return VitoairQuickMode.Off

        return VitoairQuickMode.Nothing

    @staticmethod
    def from_str(mode: str):
        match mode:
            case VitoairQuickMode.Intensive:
                return VitoairQuickMode.Intensive
            case VitoairQuickMode.ReducedNoise:
                return VitoairQuickMode.ReducedNoise
            case VitoairQuickMode.Off:
                return VitoairQuickMode.Off
            case VitoairQuickMode.Nothing:
                return VitoairQuickMode.Nothing

        return None

    def map_to_api(self):
        match self:
            case VitoairQuickMode.Intensive:
                return 8
            case VitoairQuickMode.ReducedNoise:
                return 9
            case VitoairQuickMode.Off:
                return 12
            case VitoairQuickMode.Nothing:
                return 0
