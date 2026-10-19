from typing import Any

from homeassistant.util.json import json_loads


def get_first_byte_value(data: Any) -> float | None:
    """Parse a single-value feature that older Open3e releases publish as quoted raw hex.

    Newer Open3e releases decode these features to a number (e.g. 88.0).
    Older ones publish the raw hex (e.g. "5800"), where the value is the first byte.
    """
    try:
        payload = json_loads(data)
        if isinstance(payload, str):
            return float(int(payload[0:2], 16))

        return float(payload)
    except (TypeError, ValueError):
        return None
