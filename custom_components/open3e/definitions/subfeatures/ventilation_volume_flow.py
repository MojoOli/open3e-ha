from typing import Any

from homeassistant.util.json import json_loads


def get_exhaust_air_volume_flow(data: Any) -> float | None:
    """Parse the exhaust air volume flow of feature 2328 (Vitoair current volume flow).

    Open3e names the field "ExhaustFlow" once decoded, older releases call it "Unknown".
    "Unknown" is a number in releases before May 2026 and raw little-endian hex (e.g. "9a00" = 154) since then.
    """
    try:
        payload = json_loads(data)
        value = payload["ExhaustFlow"] if "ExhaustFlow" in payload else payload["Unknown"]
        if isinstance(value, str):
            return float(int.from_bytes(bytes.fromhex(value), "little"))

        return float(value)
    except (TypeError, ValueError, KeyError):
        return None
