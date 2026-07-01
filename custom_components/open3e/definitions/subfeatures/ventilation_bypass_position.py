from typing import Any

from homeassistant.util.json import json_loads


def get_ventilation_bypass_position(data: Any) -> float | None:
    """Parse complex data type for feature 2493."""
    try:
        if isinstance(data, str) and data.strip().startswith("{"):
            payload = json_loads(data)
            return float(payload.get("BypassPosition", 0))

        # Fallback for raw hex string if not yet decoded by open3e base
        # User says 100% is 6464 (hex). 0x64 = 100.
        # It's Little Endian, but if it's 6464, both bytes are same.
        # If it's raw hex string from MQTT:
        if isinstance(data, str):
            # Try to parse as hex if it's 4 chars
            if len(data) == 4:
                # BypassPosition is likely the first byte
                return float(int(data[0:2], 16))
        return float(int(str(data), 16))
    except (TypeError, ValueError, KeyError):
        return None
