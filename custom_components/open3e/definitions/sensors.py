from dataclasses import dataclass
from typing import Callable, Any, List

from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, UnitOfEnergy, PERCENTAGE, UnitOfPower, \
    EntityCategory, UnitOfPressure, UnitOfVolumeFlowRate, UnitOfTime
from homeassistant.util.json import json_loads

from .devices import Open3eDevices
from .entity_description import Open3eEntityDescription
from .features import Features
from .subfeatures.connection_status import ConnectionStatus, get_connection_status
from .subfeatures.energy_management_mode import ENERGY_MANAGEMENT_MODES_MAP, EnergyManagementMode
from .subfeatures.four_three_way_valve_position import FOUR_THREE_WAY_VALVE_POSITION_MAP, FourThreeWayValvePosition
from ..capability.capability import Capability


class SensorDataRetriever:
    """Retriever functions for MQTT sensor data."""

    ACTUAL = lambda data: float(json_loads(data)["Actual"])
    MINIMUM = lambda data: float(json_loads(data)["Minimum"])
    MAXIMUM = lambda data: float(json_loads(data)["Maximum"])
    AVERAGE = lambda data: float(json_loads(data)["Average"])
    ACTIVE_POWER = lambda data: float(json_loads(data)["ActivePower"])
    TODAY = lambda data: float(json_loads(data)["Today"])
    CURRENT_MONTH = lambda data: float(json_loads(data)["CurrentMonth"])
    CURRENT_YEAR = lambda data: float(json_loads(data)["CurrentYear"])
    PAST_YEAR = lambda data: float(json_loads(data)["PastYear"])
    BATTERY_CHARGE_TODAY = lambda data: float(json_loads(data)["BatteryChargeToday"])
    BATTERY_CHARGE_WEEK = lambda data: float(json_loads(data)["BatteryChargeWeek"])
    BATTERY_CHARGE_MONTH = lambda data: float(json_loads(data)["BatteryChargeMonth"])
    BATTERY_CHARGE_YEAR = lambda data: float(json_loads(data)["BatteryChargeYear"])
    BATTERY_CHARGE_TOTAL = lambda data: float(json_loads(data)["BatteryChargeTotal"])
    BATTERY_DISCHARGE_TODAY = lambda data: float(json_loads(data)["BatteryDischargeToday"])
    BATTERY_DISCHARGE_WEEK = lambda data: float(json_loads(data)["BatteryDischargeWeek"])
    BATTERY_DISCHARGE_MONTH = lambda data: float(json_loads(data)["BatteryDischargeMonth"])
    BATTERY_DISCHARGE_YEAR = lambda data: float(json_loads(data)["BatteryDischargeYear"])
    BATTERY_DISCHARGE_TOTAL = lambda data: float(json_loads(data)["BatteryDischargeTotal"])
    PV_ENERGY_PRODUCTION_TODAY = lambda data: float(json_loads(data)["PhotovoltaicProductionToday"])
    PV_ENERGY_PRODUCTION_WEEK = lambda data: float(json_loads(data)["PhotovoltaicProductionWeek"])
    PV_ENERGY_PRODUCTION_MONTH = lambda data: float(json_loads(data)["PhotovoltaicProductionMonth"])
    PV_ENERGY_PRODUCTION_YEAR = lambda data: float(json_loads(data)["PhotovoltaicProductionYear"])
    PV_ENERGY_PRODUCTION_TOTAL = lambda data: float(json_loads(data)["PhotovoltaicProductionTotal"])
    TEMPERATURE = lambda data: float(json_loads(data)["Temperature"])
    PV_POWER_CUMULATED = lambda data: float(json_loads(data)["ActivePower cumulated"])
    PV_POWER_STRING_1 = lambda data: float(json_loads(data)["ActivePower String A"])
    PV_POWER_STRING_2 = lambda data: float(json_loads(data)["ActivePower String B"])
    PV_POWER_STRING_3 = lambda data: float(json_loads(data)["ActivePower String C"])
    STARTS = lambda data: int(json_loads(data)["starts"])
    HOURS = lambda data: int(json_loads(data)["hours"])
    TARGET_FLOW = lambda data: float(json_loads(data)["TargetFlow"])
    UNKNOWN = lambda data: float(json_loads(data)["Unknown"])
    RAW = lambda data: float(data)
    """The data state represents a raw value without any encapsulation."""


class SensorDataDeriver:

    @staticmethod
    def calculate_cop(thermals: tuple[float, ...], electrics: tuple[float, ...]) -> float:
        total_thermal = sum(thermals)
        total_electric = sum(electrics)

        if total_thermal <= 0 or total_electric <= 0:
            return 0.0

        return round(min(total_thermal / total_electric, 10.0), 1)


@dataclass(frozen=True)
class Open3eSensorEntityDescription(
    Open3eEntityDescription, SensorEntityDescription
):
    """Default sensor entity description for open3e."""
    domain: str = "sensor"
    data_retriever: Callable[[Any], Any] | None = None


@dataclass(frozen=True)
class Open3eDerivedSensorEntityDescription(
    Open3eEntityDescription, SensorEntityDescription
):
    """
    Derived sensor entity description for open3e.

    Attributes:
        data_retrievers: A list of callables that each take the data object
                         and return a feature value. Allows multiple
                         component sensors to feed into the derived computation.
        compute_value: A callable that receives all values returned by
                       data_retrievers (via *args) and computes the final
                       derived sensor value.
    """
    domain: str = "sensor"
    data_retrievers: List[Callable[[Any], Any]] | None = None
    """
        List of functions to retrieve feature values. Each function takes
        the data object and returns a value to be used in the derived computation.
        This list needs to be aligned with poll_data_features.
        """
    compute_value: Callable[..., Any] | None = None
    """
        Function to compute the derived sensor value. Receives *args corresponding
        to the outputs of data_retrievers. Can handle any number of parameters.
        The params need to aligned with poll_data_features.
        """


SENSORS: tuple[Open3eSensorEntityDescription, ...] = (

    ###############
    ### GENERAL ###
    ###############

    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.ServiceManagerIsRequired],
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:account-wrench",
        key="service_manager_required",
        translation_key="service_manager_required",
        data_retriever=lambda data: bool(int(data))
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.MalfunctionIdentification],
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:file-document-alert",
        key="malfunction_id",
        translation_key="malfunction_id",
        data_retriever=lambda data: int(data)
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.ErrorDtcList],
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:file-document-alert",
        key="error_dtc_list",
        translation_key="error_dtc_list",
        data_retriever=lambda data: ", ".join(
            {e["Error"]["Text"] for e in json_loads(data).get("ListEntries", [])}) or "-",
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.BackendConnectionStatus],
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:lan-connect",
        key="connection_status",
        translation_key="connection_status",
        data_retriever=lambda data: get_connection_status(int(data)),
        options=[mode for mode in ConnectionStatus]
    ),

    ###############
    ### VITOCAL ###
    ###############

    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Flow],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_temperature",
        translation_key="flow_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Return],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="return_temperature",
        translation_key="return_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.DomesticHotWater],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="domestic_hot_water_temperature",
        translation_key="domestic_hot_water_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.DomesticHotWaterTarget],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="domestic_hot_water_temperature",
        translation_key="domestic_hot_water_temperature",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Pressure.Water],
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        key="water_pressure",
        translation_key="water_pressure",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.System],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        key="power_consumption_system",
        translation_key="power_consumption_system",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.ElectricalHeater],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        key="power_consumption_electric_heater",
        translation_key="power_consumption_electric_heater",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.RefrigerantCircuit],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        key="power_consumption_refrigerant_circuit",
        translation_key="power_consumption_refrigerant_circuit",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.ThermalCapacitySystem],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        key="thermal_power",
        translation_key="thermal_power",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CentralHeating],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_central_heating_today",
        translation_key="energy_consumption_central_heating_today",
        data_retriever=SensorDataRetriever.TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CentralHeating],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_central_heating_current_month",
        translation_key="energy_consumption_central_heating_current_month",
        data_retriever=SensorDataRetriever.CURRENT_MONTH
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CentralHeating],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_central_heating_current_year",
        translation_key="energy_consumption_central_heating_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CentralHeating],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_central_heating_past_year",
        translation_key="energy_consumption_central_heating_past_year",
        data_retriever=SensorDataRetriever.PAST_YEAR,
        entity_registry_enabled_default=False
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.DomesticHotWater],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_domestic_hot_water_today",
        translation_key="energy_consumption_domestic_hot_water_today",
        data_retriever=SensorDataRetriever.TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.DomesticHotWater],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_domestic_hot_water_current_month",
        translation_key="energy_consumption_domestic_hot_water_current_month",
        data_retriever=SensorDataRetriever.CURRENT_MONTH
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.DomesticHotWater],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_domestic_hot_water_current_year",
        translation_key="energy_consumption_domestic_hot_water_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.DomesticHotWater],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_domestic_hot_water_past_year",
        translation_key="energy_consumption_domestic_hot_water_past_year",
        data_retriever=SensorDataRetriever.PAST_YEAR,
        entity_registry_enabled_default=False
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Cooling],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_cooling_today",
        translation_key="energy_consumption_cooling_today",
        data_retriever=SensorDataRetriever.TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Cooling],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_cooling_current_month",
        translation_key="energy_consumption_cooling_current_month",
        data_retriever=SensorDataRetriever.CURRENT_MONTH
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Cooling],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_cooling_current_year",
        translation_key="energy_consumption_cooling_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Cooling],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_cooling_past_year",
        translation_key="energy_consumption_cooling_past_year",
        data_retriever=SensorDataRetriever.PAST_YEAR,
        entity_registry_enabled_default=False
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Outside],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="outside_temperature",
        translation_key="outside_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.PrimaryHeatExchanger],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="primary_heat_exchanger_temperature",
        translation_key="primary_heat_exchanger_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.SecondaryHeatExchanger],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="secondary_heat_exchanger_temperature",
        translation_key="secondary_heat_exchanger_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.State.CentralHeatingPump],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="central_heating_pump_speed_percentage",
        translation_key="central_heating_pump_speed_percentage",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit1],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit1_temperature",
        translation_key="flow_circuit1_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit2],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit2_temperature",
        translation_key="flow_circuit2_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit3],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit3_temperature",
        translation_key="flow_circuit3_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit4],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit4_temperature",
        translation_key="flow_circuit4_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.CompressorInlet],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_inlet_temperature",
        translation_key="compressor_inlet_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Pressure.CompressorInlet],
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_inlet_pressure",
        translation_key="compressor_inlet_pressure",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.CompressorOutlet],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_outlet_temperature",
        translation_key="compressor_outlet_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Pressure.CompressorOutlet],
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_outlet_pressure",
        translation_key="compressor_outlet_pressure",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Room1],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="room1_temperature",
        translation_key="room1_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Room1Temperature]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Room2],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="room2_temperature",
        translation_key="room2_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Room2Temperature]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Room3],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="room3_temperature",
        translation_key="room3_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Room3Temperature]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Room4],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="room4_temperature",
        translation_key="room4_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Room4Temperature]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Position.ExpansionValve1],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="expansion_valve1_position",
        translation_key="expansion_valve1_position",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Position.ExpansionValve2],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="expansion_valve2_position",
        translation_key="expansion_valve2_position",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.State.Allengra],
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        key="allengra_flow_rate",
        translation_key="allengra_flow_rate",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.State.Allengra],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="allengra_temperature",
        translation_key="allengra_temperature",
        data_retriever=SensorDataRetriever.TEMPERATURE
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.PrimaryInlet],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="primary_inlet_temperature",
        translation_key="primary_inlet_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.SecondaryOutlet],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="secondary_outlet_temperature",
        translation_key="secondary_outlet_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.EngineRoom],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="engine_room_temperature",
        translation_key="engine_room_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.CompressorOil],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_oil_temperature",
        translation_key="compressor_oil_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.Fan1],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="fan1_power",
        translation_key="fan1_power",
        icon="mdi:fan",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.Fan2],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="fan2_power",
        translation_key="fan2_power",
        icon="mdi:fan",
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Fan2]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.EconomizerLiquid],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="economizer_liquid_temperature",
        translation_key="economizer_liquid_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.EvaporationVapor],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="evaporation_vapor_temperature",
        translation_key="evaporation_vapor_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Speed.CompressorPercent],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_speed_percentage",
        translation_key="compressor_speed_percentage",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.HeatingOutput],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="thermal_output_today",
        translation_key="thermal_output_today",
        data_retriever=SensorDataRetriever.TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CoolingOutput],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="cooling_output_today",
        translation_key="cooling_output_today",
        data_retriever=SensorDataRetriever.TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.WarmWaterOutput],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="warm_water_output_today",
        translation_key="warm_water_output_today",
        data_retriever=SensorDataRetriever.TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit1Target],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit_1_supply_temp_setpoint",
        translation_key="flow_circuit_1_supply_temp_setpoint",
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit2Target],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit_2_supply_temp_setpoint",
        translation_key="flow_circuit_2_supply_temp_setpoint",
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit3Target],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit_3_supply_temp_setpoint",
        translation_key="flow_circuit_3_supply_temp_setpoint",
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit4Target],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit_4_supply_temp_setpoint",
        translation_key="flow_circuit_4_supply_temp_setpoint",
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Speed.CompressorRps],
        native_unit_of_measurement="rps",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        key="compressor_speed_rpm",
        translation_key="compressor_speed_rpm",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.HeatingBuffer],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="heating_buffer_temperature",
        translation_key="heating_buffer_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.CoolingBuffer],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="cooling_buffer_temperature",
        translation_key="cooling_buffer_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.HeatingCoolingBuffer],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="heating_cooling_buffer_temperature",
        translation_key="heating_cooling_buffer_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.State.EnergyManagement],
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:home-battery-outline",
        key="energy_management_mode",
        translation_key="energy_management_mode",
        data_retriever=lambda data: ENERGY_MANAGEMENT_MODES_MAP.get(int(data)),
        options=[mode for mode in EnergyManagementMode]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Position.FourThreeWayValve],
        device_class=SensorDeviceClass.ENUM,
        key="four_three_way_valve_position",
        translation_key="four_three_way_valve_position",
        icon="mdi:valve",
        data_retriever=lambda data: FOUR_THREE_WAY_VALVE_POSITION_MAP.get(int(data)),
        options=[mode for mode in FourThreeWayValvePosition]
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.DesiredThermalCapacity],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="desired_thermal_capacity",
        translation_key="desired_thermal_capacity",
        icon="mdi:heat-wave",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.DesiredThermalEnergyDefrost],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="desired_thermal_energy_defrost",
        translation_key="desired_thermal_energy_defrost",
        icon="mdi:snowflake-melt",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.AdditionalHeaterStatistics],
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="additional_heater_operating_hours",
        translation_key="additional_heater_operating_hours",
        data_retriever=SensorDataRetriever.HOURS
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.AdditionalHeaterStatistics],
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:counter",
        key="additional_heater_starts",
        translation_key="additional_heater_starts",
        data_retriever=SensorDataRetriever.STARTS
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.CompressorStatistics],
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="compressor_operating_hours",
        translation_key="compressor_operating_hours",
        data_retriever=SensorDataRetriever.HOURS
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.CompressorStatistics],
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:counter",
        key="compressor_starts",
        translation_key="compressor_starts",
        data_retriever=SensorDataRetriever.STARTS
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Cop],
        native_unit_of_measurement="COP",
        icon="mdi:leaf",
        key="cop_total_current_year",
        translation_key="cop_total_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CopHeating],
        native_unit_of_measurement="COP",
        icon="mdi:leaf",
        key="cop_heating_current_year",
        translation_key="cop_heating_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CopDhw],
        native_unit_of_measurement="COP",
        icon="mdi:leaf",
        key="cop_dhw_current_year",
        translation_key="cop_dhw_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR
    ),

    ##################
    ### VitoCharge ###
    ##################

    Open3eSensorEntityDescription(
        poll_data_features=[Features.State.Battery],
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="battery_state_percentage",
        translation_key="battery_state_percentage",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_charge_today",
        translation_key="battery_charge_today",
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_charge_week",
        translation_key="battery_charge_week",
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_WEEK
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_charge_month",
        translation_key="battery_charge_month",
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_MONTH
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_charge_year",
        translation_key="battery_charge_year",
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_YEAR
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_charge_total",
        translation_key="battery_charge_total",
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_TOTAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_discharge_today",
        translation_key="battery_discharge_today",
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_discharge_week",
        translation_key="battery_discharge_week",
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_WEEK
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_discharge_month",
        translation_key="battery_discharge_month",
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_MONTH
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_discharge_year",
        translation_key="battery_discharge_year",
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_YEAR
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_discharge_total",
        translation_key="battery_discharge_total",
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_TOTAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.Grid],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="grid_power_current",
        translation_key="grid_power_current",
        data_retriever=SensorDataRetriever.ACTIVE_POWER
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.Battery],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="battery_power_current",
        translation_key="battery_power_current",
        data_retriever=SensorDataRetriever.RAW
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.PV],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="pv_power_current",
        translation_key="pv_power_current",
        data_retriever=SensorDataRetriever.PV_POWER_CUMULATED
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.PV],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="pv_power_string_1_current",
        translation_key="pv_power_string_1_current",
        data_retriever=SensorDataRetriever.PV_POWER_STRING_1
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.PV],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="pv_power_string_2_current",
        translation_key="pv_power_string_2_current",
        data_retriever=SensorDataRetriever.PV_POWER_STRING_2
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.PV],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="pv_power_string_3_current",
        translation_key="pv_power_string_3_current",
        data_retriever=SensorDataRetriever.PV_POWER_STRING_3
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.PV],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="pv_energy_production_today",
        translation_key="pv_energy_production_today",
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.PV],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="pv_energy_production_week",
        translation_key="pv_energy_production_week",
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_WEEK
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.PV],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="pv_energy_production_month",
        translation_key="pv_energy_production_month",
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_MONTH
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.PV],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="pv_energy_production_year",
        translation_key="pv_energy_production_year",
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_YEAR
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.PV],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="pv_energy_production_total",
        translation_key="pv_energy_production_total",
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_TOTAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.InverterAmbient],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="inverter_ambient_temperature",
        translation_key="inverter_ambient_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Battery],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="battery_temperature",
        translation_key="battery_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),

    ###############
    ### VitoAir ###
    ###############

    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.OutdoorAir],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="outdoor_air_temperature",
        translation_key="outdoor_air_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.SupplyAir],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="supply_air_temperature",
        translation_key="supply_air_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.ExtractAir],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="extract_air_temperature",
        translation_key="extract_air_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.ExhaustAir],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="exhaust_air_temperature",
        translation_key="exhaust_air_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Humidity.Outdoor],
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="outdoor_air_humidity",
        translation_key="outdoor_air_humidity",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Humidity.SupplyAir],
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="supply_air_humidity",
        translation_key="supply_air_humidity",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Humidity.ExtractAir],
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="extract_air_humidity",
        translation_key="extract_air_humidity",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Humidity.ExhaustAir],
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="exhaust_air_humidity",
        translation_key="exhaust_air_humidity",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Speed.SupplyAirFan],
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        key="supply_air_fan_speed",
        translation_key="supply_air_fan_speed",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Speed.ExhaustAirFan],
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        key="exhaust_air_fan_speed",
        translation_key="exhaust_air_fan_speed",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Volume.Ventilation],
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        key="ventilation_supply_air_volume",
        translation_key="ventilation_supply_air_volume",
        data_retriever=SensorDataRetriever.TARGET_FLOW,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Volume.Ventilation],
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        key="ventilation_exhaust_air_volume",
        translation_key="ventilation_exhaust_air_volume",
        data_retriever=SensorDataRetriever.UNKNOWN,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.State.VentilationLevel],
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-speed-1",
        key="ventilation_level",
        translation_key="ventilation_level",
        data_retriever=lambda data: float(json_loads(data)["Acutual"]),
        # Acutual intended, typo on Open3e for VentilationLevel (533)
        required_device=Open3eDevices.Vitoair
    ),
)

## Sensors which are derived by calculation
DERIVED_SENSORS: tuple[Open3eDerivedSensorEntityDescription, ...] = (

    ###############
    ### VITOCAL ###
    ###############

    Open3eDerivedSensorEntityDescription(
        poll_data_features=[Features.Energy.CentralHeating, Features.Energy.Cooling, Features.Energy.DomesticHotWater],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_total_today",
        translation_key="energy_consumption_total_today",
        data_retrievers=[SensorDataRetriever.TODAY] * 3,
        compute_value=lambda heating, cooling, dhw: heating + cooling + dhw
    ),
    Open3eDerivedSensorEntityDescription(
        poll_data_features=[Features.Power.ThermalCapacitySystem, Features.Power.System],
        native_unit_of_measurement="COP",
        state_class=SensorStateClass.MEASUREMENT,
        key="cop_currently",
        translation_key="cop_currently",
        icon="mdi:leaf",
        data_retrievers=[SensorDataRetriever.RAW] * 2,
        compute_value=lambda thermal, electric: SensorDataDeriver.calculate_cop(
            thermals=(thermal,),
            electrics=(electric,)
        )
    ),
    Open3eDerivedSensorEntityDescription(
        poll_data_features=[Features.Energy.HeatingOutput, Features.Energy.CentralHeating],
        native_unit_of_measurement="COP",
        state_class=SensorStateClass.MEASUREMENT,
        key="cop_heating_today",
        translation_key="cop_heating_today",
        icon="mdi:leaf",
        data_retrievers=[SensorDataRetriever.TODAY] * 2,
        compute_value=lambda thermal, electric: SensorDataDeriver.calculate_cop(
            thermals=(thermal,),
            electrics=(electric,)
        ),
    ),
    Open3eDerivedSensorEntityDescription(
        poll_data_features=[Features.Energy.CoolingOutput, Features.Energy.Cooling],
        native_unit_of_measurement="COP",
        state_class=SensorStateClass.MEASUREMENT,
        key="cop_cooling_today",
        translation_key="cop_cooling_today",
        icon="mdi:leaf",
        data_retrievers=[SensorDataRetriever.TODAY] * 2,
        compute_value=lambda thermal, electric: SensorDataDeriver.calculate_cop(
            thermals=(thermal,),
            electrics=(electric,)
        )
    ),
    Open3eDerivedSensorEntityDescription(
        poll_data_features=[Features.Energy.WarmWaterOutput, Features.Energy.DomesticHotWater],
        native_unit_of_measurement="COP",
        state_class=SensorStateClass.MEASUREMENT,
        key="cop_dhw_today",
        translation_key="cop_dhw_today",
        icon="mdi:leaf",
        data_retrievers=[SensorDataRetriever.TODAY] * 2,
        compute_value=lambda thermal, electric: SensorDataDeriver.calculate_cop(
            thermals=(thermal,),
            electrics=(electric,)
        )
    ),
    Open3eDerivedSensorEntityDescription(
        poll_data_features=[
            Features.Energy.HeatingOutput,
            Features.Energy.CoolingOutput,
            Features.Energy.WarmWaterOutput,
            Features.Energy.CentralHeating,
            Features.Energy.Cooling,
            Features.Energy.DomesticHotWater
        ],
        native_unit_of_measurement="COP",
        state_class=SensorStateClass.MEASUREMENT,
        key="cop_total_today",
        translation_key="cop_total_today",
        icon="mdi:leaf",
        data_retrievers=[SensorDataRetriever.TODAY] * 6,
        compute_value=lambda heating_t, cooling_t, dhw_t, heating_e, cooling_e, dhw_e: SensorDataDeriver.calculate_cop(
            thermals=(heating_t, cooling_t, dhw_t),
            electrics=(heating_e, cooling_e, dhw_e)
        )
    )
)
