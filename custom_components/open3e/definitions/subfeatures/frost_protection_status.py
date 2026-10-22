from typing import Any

from homeassistant.util.json import json_loads


def is_frost_protection_active(data: Any) -> bool | None:
    """Parse feature 2489 (Vitoair frost protection).

    Newer Open3e releases decode it as {"Status": "on"/"off", "Unknown": ".."}.
    Older ones publish the quoted raw hex (e.g. "013e00"), where the first byte is the status.
    """
    try:
        payload = json_loads(data)
        if isinstance(payload, dict):
            return str(payload["Status"]).lower() == "on"

        return int(str(payload)[0:2], 16) > 0
    except (TypeError, ValueError, KeyError):
        return None
