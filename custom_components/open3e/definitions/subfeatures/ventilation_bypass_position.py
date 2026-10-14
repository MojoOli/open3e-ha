from typing import Any

from homeassistant.util.json import json_loads


def get_ventilation_bypass_position(data: Any) -> float | None:
    """Parse feature 2493, which Open3e still publishes as a quoted raw hex string (e.g. "6464")."""
    try:
        payload = json_loads(data)
        if isinstance(payload, dict):
            return float(payload["BypassPosition"])

        # The first byte is the position in percent: "6464" -> 100, "4949" -> 73
        return float(int(payload[0:2], 16))
    except (TypeError, ValueError, KeyError):
        return None
