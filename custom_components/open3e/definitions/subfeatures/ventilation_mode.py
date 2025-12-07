from enum import StrEnum


class VentilationMode(StrEnum):
    Continuous = "continuous"
    Timed = "timed"
    TimedSensor = "timed_sensor"
    SensorAuto = "sensor_auto"

    @staticmethod
    def from_operation_mode(mode: int):
        match mode:
            case 1:
                return VentilationMode.Continuous
            case 2:
                return VentilationMode.Timed
            case 3:
                return VentilationMode.TimedSensor
            case 4:
                return VentilationMode.SensorAuto
        return None

    @staticmethod
    def from_str(mode: str):
        match mode:
            case "continuous":
                return VentilationMode.Continuous
            case "timed":
                return VentilationMode.Timed
            case "timed_sensor":
                return VentilationMode.TimedSensor
            case "sensor_auto":
                return VentilationMode.SensorAuto
        return None

    def map_to_api(self):
        match self:
            case VentilationMode.Continuous:
                return 1
            case VentilationMode.Timed:
                return 2
            case VentilationMode.TimedSensor:
                return 3
            case VentilationMode.SensorAuto:
                return 4
