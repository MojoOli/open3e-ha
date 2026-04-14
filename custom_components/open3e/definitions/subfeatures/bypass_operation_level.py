from enum import StrEnum
from typing import Any

from homeassistant.util.json import json_loads


class BypassOperationLevel(StrEnum):
    Off = "off"
    Dynamic = "dynamic"
    Soft = "soft"
    Manual = "manual"
    Unknown = "unknown"


def get_bypass_operation_level(data: Any) -> BypassOperationLevel | None:
    try:
        # DID 2403 is O3EByteVal (simple integer) according to Open3Edatapoints.py
        # but let's handle complex structure too just in case it's actually O3EEnum
        if isinstance(data, str) and data.strip().startswith("{"):
            payload = json_loads(data)
            raw_id = payload.get("ID")
            if raw_id is None:
                return None
            value = int(raw_id)
        else:
            value = int(data)

        match value:
            case 0:
                return BypassOperationLevel.Off
            case 1:
                return BypassOperationLevel.Dynamic
            case 2:
                return BypassOperationLevel.Soft
            case 3:
                return BypassOperationLevel.Manual
            case _:
                return BypassOperationLevel.Unknown
    except (TypeError, ValueError, KeyError):
        return None
