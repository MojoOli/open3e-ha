from dataclasses import dataclass


@dataclass(frozen=True)
class Feature:
    id: int
    """The ID used on the Open3e server to identify the feature."""
    refresh_interval: int | None
    """Represent the refresh interval in seconds.
    The minimum and step size is 5 seconds.
    
    If its set to None, the feature should not be refreshed and only be used for setting data.
    """


class Features:
    class Temperature:
        FlowTemperature = Feature(id=268, refresh_interval=5)
        ReturnTemperature = Feature(id=269, refresh_interval=5)
        DomesticHotWaterTemperature = Feature(id=271, refresh_interval=5)
        OutsideTemperature = Feature(id=274, refresh_interval=5)
        FlowCircuit1Temperature = Feature(id=284, refresh_interval=5)
        PrimaryHeatExchangerTemperature = Feature(id=320, refresh_interval=5)
        Room1Temperature = Feature(id=334, refresh_interval=5)
        SecondaryHeatExchangerTemperature = Feature(id=355, refresh_interval=5)
        SetTargetTemperature = Feature(id=424, refresh_interval=None)
        TargetTemperature = Feature(id=1643, refresh_interval=5)

    class Pressure:
        WaterPressure = Feature(id=318, refresh_interval=15)

    class Energy:
        EnergyConsumptionCentralHeatingToday = Feature(id=548, refresh_interval=300)
        EnergyConsumptionDomesticHotWaterToday = Feature(id=565, refresh_interval=300)
        EnergyConsumptionCoolingToday = Feature(id=566, refresh_interval=300)

    class Power:
        FanPower = Feature(id=1775, refresh_interval=30)

    class State:
        Hvac = Feature(id=1415, refresh_interval=30)
        Heater = Feature(id=2352, refresh_interval=30)

    class Speed:
        CentralHeatingPump = Feature(id=381, refresh_interval=10)
