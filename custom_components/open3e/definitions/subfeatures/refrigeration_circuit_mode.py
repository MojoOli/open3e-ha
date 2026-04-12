from enum import StrEnum


class RefrigerationCircuitOperationMode(StrEnum):
    OFF = "off"
    SHUTDOWN = "shutdown"
    HEATING = "heating"
    COOLING = "cooling"
    MANUAL = "manual"
    DEFROST = "defrost"
    EVU_LOCK = "evu_lock"


REFRIGERATION_CIRCUIT_OPERATION_MODES_MAP: dict[int, RefrigerationCircuitOperationMode] = {
    0: RefrigerationCircuitOperationMode.OFF,
    1: RefrigerationCircuitOperationMode.SHUTDOWN,
    2: RefrigerationCircuitOperationMode.HEATING,
    3: RefrigerationCircuitOperationMode.COOLING,
    4: RefrigerationCircuitOperationMode.MANUAL,
    5: RefrigerationCircuitOperationMode.DEFROST,
    6: RefrigerationCircuitOperationMode.EVU_LOCK,
}
