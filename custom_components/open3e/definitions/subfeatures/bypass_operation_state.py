from enum import StrEnum
from typing import Any

from homeassistant.util.json import json_loads


class BypassOperationState(StrEnum):
    Closed = "closed"
    Automatic = "automatic"
    Open = "open"
    TransitionError = "transition_error"

    @staticmethod
    def from_str(mode: str):
        match mode:
            case "closed":
                return BypassOperationState.Closed
            case "automatic":
                return BypassOperationState.Automatic
            case "open":
                return BypassOperationState.Open
            case "transition_error":
                return BypassOperationState.TransitionError
        return None

    def map_to_api(self):
        match self:
            case BypassOperationState.Closed:
                return 0
            case BypassOperationState.Automatic:
                return 1
            case BypassOperationState.Open:
                return 2
            case BypassOperationState.TransitionError:
                return 3
        return None


def get_bypass_operation_state(data: Any) -> BypassOperationState | None:
    try:
        if isinstance(data, str) and data.strip().startswith("{"):
            payload = json_loads(data)
            raw_id = payload.get("BypassStatus")
            if raw_id is None:
                return None
            value = int(raw_id)
        else:
            return None

        match value:
            case 0:
                return BypassOperationState.Closed
            case 1:
                return BypassOperationState.Automatic
            case 2:
                return BypassOperationState.Open
            case 3:
                return BypassOperationState.TransitionError
            case _:
                return None
    except (TypeError, ValueError, KeyError):
        return None
