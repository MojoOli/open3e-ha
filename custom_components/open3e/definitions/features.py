from dataclasses import dataclass


@dataclass(frozen=True)
class Feature:
    id: int
    """The ID used on the Open3e server to identify the feature."""
    refresh_interval: int | None
    """Represent the refresh interval in seconds.
    The minimum and step size is 5 seconds.
    
    If its set to None, the feature will not be refreshed and only be used for setting data.
    """


class Features:
    class Temperature:
        Flow = Feature(id=268, refresh_interval=5)
        Return = Feature(id=269, refresh_interval=5)
        DomesticHotWater = Feature(id=271, refresh_interval=5)
        DomesticHotWaterTarget = Feature(id=396, refresh_interval=300)
        Outside = Feature(id=274, refresh_interval=5)
        FlowCircuit1 = Feature(id=284, refresh_interval=5)
        FlowCircuit2 = Feature(id=286, refresh_interval=5)
        FlowCircuit3 = Feature(id=288, refresh_interval=5)
        FlowCircuit4 = Feature(id=290, refresh_interval=5)
        PrimaryHeatExchanger = Feature(id=320, refresh_interval=5)
        Room1 = Feature(id=334, refresh_interval=5)
        Room2 = Feature(id=335, refresh_interval=5)
        Room3 = Feature(id=336, refresh_interval=5)
        Room4 = Feature(id=337, refresh_interval=5)
        SecondaryHeatExchanger = Feature(id=355, refresh_interval=5)
        ProgramsCircuit1 = Feature(id=424, refresh_interval=30)
        ProgramsCircuit2 = Feature(id=426, refresh_interval=30)
        ProgramsCircuit3 = Feature(id=428, refresh_interval=30)
        ProgramsCircuit4 = Feature(id=430, refresh_interval=30)

    class Pressure:
        Water = Feature(id=318, refresh_interval=15)

    class Energy:
        CentralHeating = Feature(id=548, refresh_interval=300)
        DomesticHotWater = Feature(id=565, refresh_interval=300)
        Cooling = Feature(id=566, refresh_interval=300)

    class Power:
        Fan = Feature(id=1775, refresh_interval=30)
        ElectricalHeater = Feature(id=2487, refresh_interval=5)
        System = Feature(id=2488, refresh_interval=5)

    class State:
        Hvac = Feature(id=1415, refresh_interval=30)
        Heater = Feature(id=2352, refresh_interval=30)
        DomesticHotWater = Feature(id=531, refresh_interval=30)
        DomesticHotWaterEfficiency = Feature(id=3029, refresh_interval=30)

    class Speed:
        CentralHeatingPump = Feature(id=381, refresh_interval=10)
