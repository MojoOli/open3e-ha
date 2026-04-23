from enum import StrEnum
from typing import Any

from homeassistant.util.json import json_loads


class BypassOperationState(StrEnum):
    Closed = "closed"
    Automatic = "automatic"
    Open = "open"

    @staticmethod
    def from_str(mode: str):
        match mode:
            case "closed":
                return BypassOperationState.Closed
            case "open":
                return BypassOperationState.Open
            case "automatic":
                return BypassOperationState.Automatic
        return None

    def map_to_api(self):
        match self:
            case BypassOperationState.Closed:
                return 0
            case BypassOperationState.Open:
                return 1
            case BypassOperationState.Automatic:
                return 2


def get_bypass_operation_state(data: Any) -> BypassOperationState | None:
    try:
        if isinstance(data, str) and data.strip().startswith("{"):
            payload = json_loads(data)
            value = payload.get("BypassStatus")
            if value is None:
                return None
        else:
            return None

        match value:
            case 0:
                return BypassOperationState.Closed
            case 1:
                return BypassOperationState.Open
            case 2:
                return BypassOperationState.Automatic
            case _:
                return None
    except (TypeError, ValueError, KeyError):
        return None
