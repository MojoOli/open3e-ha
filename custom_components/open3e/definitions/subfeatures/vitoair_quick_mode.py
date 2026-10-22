from enum import StrEnum
from typing import Any

from homeassistant.util.json import json_loads


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


def get_vitoair_quick_mode(data: Any) -> VitoairQuickMode | None:
    """Parse feature 1007 (Vitoair current quick mode).

    Needs an Open3e release that decodes the 6-byte Vitoair variant
    ({"OpMode": 8, "Required": "on", "Runtime": 90.0, "Unknown": "0000"}).
    Older releases publish raw hex, which returns None so the select stays unavailable.
    """
    try:
        payload = json_loads(data)
        if not isinstance(payload, dict):
            return None

        if str(payload["Required"]).lower() != "on":
            return VitoairQuickMode.Nothing

        return VitoairQuickMode.from_operation_mode(int(payload["OpMode"]))
    except (TypeError, ValueError, KeyError):
        return None
