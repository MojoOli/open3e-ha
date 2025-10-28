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
        FlowCircuit1Target = Feature(id=987, refresh_interval=30)
        FlowCircuit2Target = Feature(id=988, refresh_interval=30)
        FlowCircuit3Target = Feature(id=989, refresh_interval=30)
        FlowCircuit4Target = Feature(id=990, refresh_interval=30)
        PrimaryHeatExchanger = Feature(id=320, refresh_interval=5)
        CompressorInlet = Feature(id=321, refresh_interval=5)
        CompressorOutlet = Feature(id=324, refresh_interval=5)
        Room1 = Feature(id=334, refresh_interval=5)
        Room2 = Feature(id=335, refresh_interval=5)
        Room3 = Feature(id=336, refresh_interval=5)
        Room4 = Feature(id=337, refresh_interval=5)
        SecondaryHeatExchanger = Feature(id=355, refresh_interval=5)
        ProgramsCircuit1 = Feature(id=424, refresh_interval=30)
        ProgramsCircuit2 = Feature(id=426, refresh_interval=30)
        ProgramsCircuit3 = Feature(id=428, refresh_interval=30)
        ProgramsCircuit4 = Feature(id=430, refresh_interval=30)
        PrimaryInlet = Feature(id=1769, refresh_interval=5)
        SecondaryOutlet = Feature(id=1769, refresh_interval=5)
        EngineRoom = Feature(id=1771, refresh_interval=30)
        CompressorOil = Feature(id=1772, refresh_interval=30)
        EconomizerLiquid = Feature(id=2333, refresh_interval=30)
        EvaporationVapor = Feature(id=2334, refresh_interval=30)
        SmartGridTemperatureOffsets = Feature(id=2543, refresh_interval=5)
        FlowCircuit1Cooling = Feature(id=2405, refresh_interval=30)
        FlowCircuit1Hysteresis = Feature(id=2413, refresh_interval=30)
        BufferMinMax = Feature(id=3106, refresh_interval=30)
        OutdoorAir = Feature(id=327, refresh_interval=5)
        SupplyAir = Feature(id=328, refresh_interval=5)
        ExtractAir = Feature(id=329, refresh_interval=5)
        ExhaustAir = Feature(id=330, refresh_interval=5)
        InverterAmbient = Feature(id=1684, refresh_interval=30)
        Battery = Feature(id=2240, refresh_interval=30)
        HeatingCoolingBuffer = Feature(id=3018, refresh_interval=30)
        DomesticHotWaterHysteresis = Feature(id=1085, refresh_interval=30)

    class Humidity:
        Outdoor = Feature(id=419, refresh_interval=5)
        SupplyAir = Feature(id=420, refresh_interval=5)
        ExtractAir = Feature(id=421, refresh_interval=5)
        ExhaustAir = Feature(id=422, refresh_interval=5)

    class Pressure:
        Water = Feature(id=318, refresh_interval=15)
        CompressorInlet = Feature(id=322, refresh_interval=15)
        CompressorOutlet = Feature(id=325, refresh_interval=15)

    class Energy:
        CentralHeating = Feature(id=548, refresh_interval=300)
        DomesticHotWater = Feature(id=565, refresh_interval=300)
        Cooling = Feature(id=566, refresh_interval=300)
        Battery = Feature(id=1801, refresh_interval=300)
        PV = Feature(id=1802, refresh_interval=300)
        HeatingOutput = Feature(id=1211, refresh_interval=30)
        WarmWaterOutput = Feature(id=1391, refresh_interval=30)
        CoolingOutput = Feature(id=2529, refresh_interval=30)
        DesiredThermalCapacity = Feature(id=2629, refresh_interval=30)
        DesiredThermalEnergyDefrost = Feature(id=2256, refresh_interval=30)

    class Power:
        Fan1 = Feature(id=1775, refresh_interval=5)
        Fan2 = Feature(id=1776, refresh_interval=5)
        RefrigerantCircuit = Feature(id=2486, refresh_interval=5)
        ElectricalHeater = Feature(id=2487, refresh_interval=5)
        System = Feature(id=2488, refresh_interval=5)
        ThermalCapacitySystem = Feature(id=2496, refresh_interval=5)
        Battery = Feature(id=1836, refresh_interval=5)
        PV = Feature(id=1690, refresh_interval=5)
        MaxElectricalHeater = Feature(id=2626, refresh_interval=5)
        Grid = Feature(id=1603, refresh_interval=5)

    class State:
        Hvac = Feature(id=1415, refresh_interval=30)
        AdditionalHeater = Feature(id=2352, refresh_interval=30)
        DomesticHotWater = Feature(id=531, refresh_interval=30)
        DomesticHotWaterEfficiency = Feature(id=3029, refresh_interval=30)
        Battery = Feature(id=1664, refresh_interval=30)
        Allengra = Feature(id=1043, refresh_interval=30)
        HeatPumpCompressor = Feature(id=2351, refresh_interval=30)
        Buffer = Feature(id=3070, refresh_interval=30)
        CircuitFrostProtection = Feature(id=2855, refresh_interval=30)
        CentralHeatingPump = Feature(id=381, refresh_interval=10)
        HotWaterCirculationPump = Feature(id=491, refresh_interval=30)
        DomesticHotWaterCirculationPumpMode = Feature(id=497, refresh_interval=30)
        TargetQuickMode = Feature(id=1006, refresh_interval=30)
        FrostProtection = Feature(id=2489, refresh_interval=30)
        EnergyManagement = Feature(id=2350, refresh_interval=30)
        FlowCircuit1HeatingCurve = Feature(id=880, refresh_interval=30)
        FlowCircuit2HeatingCurve = Feature(id=881, refresh_interval=30)
        FlowCircuit3HeatingCurve = Feature(id=882, refresh_interval=30)
        FlowCircuit4HeatingCurve = Feature(id=883, refresh_interval=30)

    class Speed:
        CompressorPercent = Feature(id=2346, refresh_interval=10)
        CompressorRps = Feature(id=2569, refresh_interval=10)

    class Position:
        ExpansionValve1 = Feature(id=389, refresh_interval=30)
        ExpansionValve2 = Feature(id=391, refresh_interval=30)
        FourThreeWayValve = Feature(id=2735, refresh_interval=30)

    class Misc:
        CompressorStatistics = Feature(id=2369, refresh_interval=120)
        AdditionalHeaterStatistics = Feature(id=2370, refresh_interval=120)
