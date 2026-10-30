from typing import Any

from homeassistant.util.json import json_loads


def get_gateway_ethernet_ip(data: Any) -> str | None:
    """Parse the LAN IP address of feature 1696 (GatewayEthernetIp).

    Open3e publishes the 20 bytes as raw hex. They are assumed to have the layout of 607 (GatewayRemoteIp):
    IP address, subnet mask, gateway, DNS server 1 and 2, 4 bytes each. The IP address is the first 4 bytes.
    A decoded payload ({"<IP field>": "192.168.001.010", ...}) is read from its first field.
    """
    try:
        payload = json_loads(data)
        if isinstance(payload, dict):
            octets = str(next(iter(payload.values()))).split(".")
        else:
            octets = [str(byte) for byte in bytes.fromhex(payload)[0:4]]

        if len(octets) != 4:
            return None

        return ".".join(str(int(octet)) for octet in octets)
    except (TypeError, ValueError, StopIteration):
        return None
