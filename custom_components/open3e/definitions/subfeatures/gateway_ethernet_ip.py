from typing import Any

from homeassistant.util.json import json_loads

GATEWAY_ETHERNET_IP_FIELD = "LAN_IP-Address"


def get_gateway_ethernet_ip(data: Any) -> str | None:
    """Parse the LAN IP address of feature 1696 (GatewayEthernetIp).

    The 20 bytes have the layout of 607 (GatewayRemoteIp): IP address, subnet mask, gateway, DNS server 1 and 2,
    4 bytes each. Older Open3e releases publish them as raw hex, where the IP address is the first 4 bytes.
    Newer ones decode them (open3e/open3e#406) to {"LAN_IP-Address": "192.168.178.025", "SubnetMask": ..., ...};
    if the field is named differently, the first field is used.
    """
    try:
        payload = json_loads(data)
        if isinstance(payload, dict):
            ip = payload[GATEWAY_ETHERNET_IP_FIELD] if GATEWAY_ETHERNET_IP_FIELD in payload else next(iter(payload.values()))
            octets = str(ip).split(".")
        else:
            octets = [str(byte) for byte in bytes.fromhex(payload)[0:4]]

        if len(octets) != 4:
            return None

        return ".".join(str(int(octet)) for octet in octets)
    except (TypeError, ValueError, StopIteration):
        return None
