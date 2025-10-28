from enum import StrEnum


class ConnectionStatus(StrEnum):
    CONNECTED = "connected"
    NOT_CONNECTED = "not_connected"


# Map numeric CAN values to the Enum
def get_connection_status(status: int):
    if status == 3:
        return ConnectionStatus.CONNECTED
    else:
        return ConnectionStatus.NOT_CONNECTED
