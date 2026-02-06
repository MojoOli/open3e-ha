from dataclasses import dataclass
from typing import Callable, Any, List

from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, UnitOfEnergy, PERCENTAGE, UnitOfPower, \
    EntityCategory, UnitOfPressure, UnitOfVolume, UnitOfVolumeFlowRate, UnitOfTime
from homeassistant.util.json import json_loads
from homeassistant.util.dt import parse_time
from datetime import datetime

from .devices import Open3eDevices
from .entity_description import Open3eEntityDescription
from .features import Features
from .subfeatures.connection_status import ConnectionStatus, get_connection_status
from .subfeatures.energy_management_mode import ENERGY_MANAGEMENT_MODES_MAP, EnergyManagementMode
from .subfeatures.four_three_way_valve_position import FOUR_THREE_WAY_VALVE_POSITION_MAP, FourThreeWayValvePosition
from .subfeatures.legionella_protection import LegionellaProtectionWeekday, get_lp_weekday #, ConcStrLPWeekDay
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
    GRID_FEED_IN_ENERGY = lambda data: float(json_loads(data)["GridFeedInEnergy"])
    GRID_SUPPLIED_ENERGY = lambda data: float(json_loads(data)["GridSuppliedEnergy"])
    TEMPERATURE = lambda data: float(json_loads(data)["Temperature"])
    TIME = lambda data: parse_time(str(data[1:][:-1]))
    STANDARD =  lambda data: float(json_loads(data)["Standard"])
    PV_POWER_CUMULATED = lambda data: float(json_loads(data)["ActivePower cumulated"])
    PV_POWER_STRING_1 = lambda data: float(json_loads(data)["ActivePower String A"])
    PV_POWER_STRING_2 = lambda data: float(json_loads(data)["ActivePower String B"])
    PV_POWER_STRING_3 = lambda data: float(json_loads(data)["ActivePower String C"])
    STARTS = lambda data: int(json_loads(data)["starts"])
    HOURS = lambda data: int(json_loads(data)["hours"])
    TARGET_FLOW = lambda data: float(json_loads(data)["TargetFlow"])
    TEXT = lambda data: str(json_loads(data)["Text"])
    UNKNOWN = lambda data: float(json_loads(data)["Unknown"])
    RAWSTR = lambda data: str(data[1:][:-1])
    RAW = lambda data: float(data)
    """The data state represents a raw value without any encapsulation."""

    @staticmethod
    def cleaned_ip(ip_str: str) -> str:
        """Clean-up the IP-adress string by removing leading zeros from each octet. 
           This is necessary because the Viessmann CAN Bus returns IPs with leading zeros."""
        try:
            return ".".join(str(int(octet)) for octet in ip_str.split('.'))
        except ValueError:  # If ip_str did not match format
            return '-'

    @staticmethod
    def parse_date_vitodensstr(dt_str: str) -> str:
        """Convert a date string to a date object and output as string."""
        try:
            return datetime.strptime(dt_str, "%d.%m.%Y").date().strftime("%d.%m.%Y")
        except ValueError:  # If dt_str did not match our format
            return '-'


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
            {e["Error"]["Text"] for e in json_loads(data).get("ListEntries", [])}) or "-"
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

    ################
    ### VITODENS ###
    ################

    ######### ENERGY-SENSORS #########
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.EnergyConsumptionCentralHeating],
        device_class=SensorDeviceClass.ENERGY,
        key="EnergyConsumptionCentralHeating",
        translation_key="EnergyConsumptionCentralHeating",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        data_retriever=SensorDataRetriever.TODAY,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.EnergyConsumptionDomesticHotWater],
        device_class=SensorDeviceClass.ENERGY,
        key="EnergyConsumptionDomesticHotWater",
        translation_key="EnergyConsumptionDomesticHotWater",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        data_retriever=SensorDataRetriever.TODAY,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.GeneratedCentralHeatingOutput],
        device_class=SensorDeviceClass.ENERGY,
        key="GeneratedCentralHeatingOutput",
        translation_key="GeneratedCentralHeatingOutput",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        data_retriever=SensorDataRetriever.TODAY,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.GeneratedDomesticHotWaterOutput],
        device_class=SensorDeviceClass.ENERGY,
        key="GeneratedDomesticHotWaterOutput",
        translation_key="GeneratedDomesticHotWaterOutput",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        data_retriever=SensorDataRetriever.TODAY,
        required_device=Open3eDevices.Vitodens
    ),

    ######### PRESSURE-SENSORS #########
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Pressure.WaterPressureSensor],
        device_class=SensorDeviceClass.PRESSURE,
        key="WaterPressureSensor",
        translation_key="WaterPressureSensor",
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitodens
    ),

    ######### TEMPERATURE-SENSORS #########
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="FlowTemperatureSensor",
        translation_key="FlowTemperatureSensor",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.DomesticHotWaterSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="DomesticHotWaterSensor",
        translation_key="DomesticHotWaterSensor",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.OutsideTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="OutsideTemperatureSensor",
        translation_key="OutsideTemperatureSensor",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerOneCircuitFlowTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerOneCircuitFlowTemperatureSensor",
        translation_key="MixerOneCircuitFlowTemperatureSensor",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerTwoCircuitFlowTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerTwoCircuitFlowTemperatureSensor",
        translation_key="MixerTwoCircuitFlowTemperatureSensor",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerThreeCircuitFlowTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerThreeCircuitFlowTemperatureSensor",
        translation_key="MixerThreeCircuitFlowTemperatureSensor",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerFourCircuitFlowTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerFourCircuitFlowTemperatureSensor",
        translation_key="MixerFourCircuitFlowTemperatureSensor",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlueGasTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="FlueGasTemperatureSensor",
        translation_key="FlueGasTemperatureSensor",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerOneCircuitRoomTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerOneCircuitRoomTemperatureSensor",
        translation_key="MixerOneCircuitRoomTemperatureSensor",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerTwoCircuitRoomTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerTwoCircuitRoomTemperatureSensor",
        translation_key="MixerTwoCircuitRoomTemperatureSensor",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerThreeCircuitRoomTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerThreeCircuitRoomTemperatureSensor",
        translation_key="MixerThreeCircuitRoomTemperatureSensor",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerFourCircuitRoomTemperatureSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerFourCircuitRoomTemperatureSensor",
        translation_key="MixerFourCircuitRoomTemperatureSensor",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.DomesticHotWaterOutletSensor],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="DomesticHotWaterOutletSensor",
        translation_key="DomesticHotWaterOutletSensor",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.DomesticHotWaterTemperatureSetpoint],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="DomesticHotWaterTemperatureSetpoint",
        translation_key="DomesticHotWaterTemperatureSetpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerOneCircuitRoomTemperatureSetpoint],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerOneCircuitRoomTemperatureSetpoint",
        translation_key="MixerOneCircuitRoomTemperatureSetpoint",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.STANDARD,
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerTwoCircuitRoomTemperatureSetpoint],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerTwoCircuitRoomTemperatureSetpoint",
        translation_key="MixerTwoCircuitRoomTemperatureSetpoint",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.STANDARD,
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerThreeCircuitRoomTemperatureSetpoint],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerThreeCircuitRoomTemperatureSetpoint",
        translation_key="MixerThreeCircuitRoomTemperatureSetpoint",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.STANDARD,
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerFourCircuitRoomTemperatureSetpoint],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerFourCircuitRoomTemperatureSetpoint",
        translation_key="MixerFourCircuitRoomTemperatureSetpoint",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.STANDARD,
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowTemperatureTargetSetpoint],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="FlowTemperatureTargetSetpoint",
        translation_key="FlowTemperatureTargetSetpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerOneCircuitFlowTemperatureTargetSetpoint],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerOneCircuitFlowTemperatureTargetSetpoint",
        translation_key="MixerOneCircuitFlowTemperatureTargetSetpoint",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerTwoCircuitFlowTemperatureTargetSetpoint],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerTwoCircuitFlowTemperatureTargetSetpoint",
        translation_key="MixerTwoCircuitFlowTemperatureTargetSetpoint",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerThreeCircuitFlowTemperatureTargetSetpoint],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerThreeCircuitFlowTemperatureTargetSetpoint",
        translation_key="MixerThreeCircuitFlowTemperatureTargetSetpoint",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.MixerFourCircuitFlowTemperatureTargetSetpoint],
        device_class=SensorDeviceClass.TEMPERATURE,
        key="MixerFourCircuitFlowTemperatureTargetSetpoint",
        translation_key="MixerFourCircuitFlowTemperatureTargetSetpoint",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitodens
    ),

    ######### FLOW-RATE-SENSORS #########
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Volume.AllengraSensor],
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        key="AllengraSensor",
        translation_key="AllengraSensor",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitodens
    ),

    ######### TIME/DATE-SENSORS #########
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Time.HeatEngineStatistical],
        device_class=SensorDeviceClass.DURATION,
        key="HeatEngineStatisticalOperatingHours",
        translation_key="HeatEngineStatisticalOperatingHours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        data_retriever=lambda data: int(json_loads(data)["OperatingHours"]),
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Time.HeatEngineStatistical],
        device_class=SensorDeviceClass.DURATION,
        key="HeatEngineStatisticalBurnerHours",
        translation_key="HeatEngineStatisticalBurnerHours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        data_retriever=lambda data: int(json_loads(data)["BurnerHours"]),
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Time.LegionellaProtectionStartTime],
        device_class=SensorDeviceClass.DATE,
        key="LegionellaProtectionStartTime",
        translation_key="LegionellaProtectionStartTime",
        entity_registry_enabled_default=False,
        icon="mdi:water-plus",
        data_retriever=SensorDataRetriever.TIME,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Time.LegionellaProtectionWeekday],
        device_class=SensorDeviceClass.ENUM,
        key="LegionellaProtectionWeekday",
        translation_key="LegionellaProtectionWeekday",
        entity_registry_enabled_default=False,
        icon="mdi:water-plus",
        data_retriever=lambda data: get_lp_weekday(int(data)),
        options=[wday for wday in LegionellaProtectionWeekday],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Time.ServiceDateNext],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="ServiceDateNext",
        translation_key="ServiceDateNext",
        entity_registry_enabled_default=False,
        icon="mdi:calendar",
#        data_retriever=lambda data: SensorDataRetriever.parse_date_vitodensstr("01.01.2026"),
        data_retriever=lambda data: SensorDataRetriever.parse_date_vitodensstr(json_loads(data)["Date"]),
        required_device=Open3eDevices.Vitodens
    ),

    ######### MISC-SENSORS #########
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.ScaldProtection],
        key="ScaldProtection",
        translation_key="ScaldProtection",
        icon="mdi:shield-star",
        entity_registry_enabled_default=False,
        data_retriever=SensorDataRetriever.RAWSTR,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.Date],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="VitodensDate",
        translation_key="VitodensDate",
        icon="mdi:calendar",
        entity_registry_enabled_default=False,
#        data_retriever=lambda data: SensorDataRetriever.parse_date_vitodensstr("01.01.2026"),
        data_retriever=lambda data: SensorDataRetriever.parse_date_vitodensstr(data[1:][:-1]),
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.Time],
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.DATE,
        key="VitodensTime",
        translation_key="VitodensTime",
        icon="mdi:clock",
        entity_registry_enabled_default=False,
        data_retriever=SensorDataRetriever.TIME,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.GatewayMac],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="GatewayMac",
        translation_key="GatewayMac",
        icon="mdi:ethernet",
        data_retriever=SensorDataRetriever.RAWSTR,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.GatewayRemoteLocalNetworkStatus],
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:access-point-network",
        entity_registry_enabled_default=False,
        key="GatewayRemoteLocalNetworkStatus",
        translation_key="GatewayRemoteLocalNetworkStatus",
        data_retriever=lambda data: get_connection_status(int(data)),
        options=[mode for mode in ConnectionStatus],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.GatewayRemoteIp],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="GatewayRemoteIp",
        translation_key="GatewayRemoteIp",
        icon="mdi:ip-network",
        entity_registry_enabled_default=False,
        data_retriever=lambda data: SensorDataRetriever.cleaned_ip(json_loads(data)["WLAN_IP-Address"]),
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.GatewayRemoteSignalStrength],
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dB",
        key="GatewayRemoteSignalStrength",
        translation_key="GatewayRemoteSignalStrength",
        icon="mdi:wifi",
        entity_registry_enabled_default=False,
        data_retriever=lambda data: int(data),
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.CentralHeatingOneCircuitName],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="CentralHeatingOneCircuitName",
        translation_key="CentralHeatingOneCircuitName",
        entity_registry_enabled_default=False,
        data_retriever=SensorDataRetriever.RAWSTR,
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.CentralHeatingTwoCircuitName],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="CentralHeatingTwoCircuitName",
        translation_key="CentralHeatingTwoCircuitName",
        entity_registry_enabled_default=False,
        data_retriever=SensorDataRetriever.RAWSTR,
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.CentralHeatingThreeCircuitName],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="CentralHeatingThreeCircuitName",
        translation_key="CentralHeatingThreeCircuitName",
        entity_registry_enabled_default=False,
        data_retriever=SensorDataRetriever.RAWSTR,
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.CentralHeatingFourCircuitName],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="CentralHeatingFourCircuitName",
        translation_key="CentralHeatingFourCircuitName",
        entity_registry_enabled_default=False,
        data_retriever=SensorDataRetriever.RAWSTR,
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.MixerOneCircuitCentralHeatingCurve],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="MixerOneCircuitCentralHeatingCurve",
        translation_key="MixerOneCircuitCentralHeatingCurve",
        entity_registry_enabled_default=False,
        data_retriever=lambda data: float(json_loads(data)["Gradient"]),
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.MixerTwoCircuitCentralHeatingCurve],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="MixerTwoCircuitCentralHeatingCurve",
        translation_key="MixerTwoCircuitCentralHeatingCurve",
        entity_registry_enabled_default=False,
        data_retriever=lambda data: float(json_loads(data)["Gradient"]),
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.MixerThreeCircuitCentralHeatingCurve],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="MixerThreeCircuitCentralHeatingCurve",
        translation_key="MixerThreeCircuitCentralHeatingCurve",
        entity_registry_enabled_default=False,
        data_retriever=lambda data: float(json_loads(data)["Gradient"]),
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.MixerFourCircuitCentralHeatingCurve],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="MixerFourCircuitCentralHeatingCurve",
        translation_key="MixerFourCircuitCentralHeatingCurve",
        entity_registry_enabled_default=False,
        data_retriever=lambda data: float(json_loads(data)["Gradient"]),
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.BuildingType],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="BuildingType",
        translation_key="BuildingType",
        data_retriever=SensorDataRetriever.TEXT,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.ElectronicTraceabilityNumber],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="ElectronicTraceabilityNumber",
        translation_key="ElectronicTraceabilityNumber",
        data_retriever=SensorDataRetriever.RAWSTR,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.GasType],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="GasType",
        translation_key="GasType",
        data_retriever=SensorDataRetriever.TEXT,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.CentralHeatingRegulationMode],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="CentralHeatingRegulationMode",
        translation_key="CentralHeatingRegulationMode",
        data_retriever=SensorDataRetriever.TEXT,
        required_device=Open3eDevices.Vitodens
    ),
#    Open3eSensorEntityDescription(
#        poll_data_features=[Features.Misc.TargetQuickMode],
#        key="TargetQuickMode",
#        translation_key="TargetQuickMode",
#        data_retriever=SensorDataRetriever.xxx,
#        required_device=Open3eDevices.Vitodens
#    ),
#    Open3eSensorEntityDescription(
#        poll_data_features=[Features.Misc.CurrentQuickMode],
#        key="CurrentQuickMode",
#        translation_key="CurrentQuickMode",
#        data_retriever=SensorDataRetriever.RAWSTR,
#        required_device=Open3eDevices.Vitodens
#    ),
#    Open3eSensorEntityDescription(
#        poll_data_features=[Features.Misc.DomesticHotWaterHysteresis],
#        key="DomesticHotWaterHysteresis",
#        translation_key="DomesticHotWaterHysteresis",
#        data_retriever=SensorDataRetriever.xxx,
#        required_device=Open3eDevices.Vitodens
#    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.TimeSettingSource],
        entity_category=EntityCategory.DIAGNOSTIC,
        key="TimeSettingSource",
        translation_key="TimeSettingSource",
        data_retriever=SensorDataRetriever.TEXT,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.ChimneySweeperTestMode],
        key="ChimneySweeperTestMode",
        translation_key="ChimneySweeperTestMode",
        data_retriever=SensorDataRetriever.RAWSTR,
        required_device=Open3eDevices.Vitodens
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
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Return],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="return_temperature",
        translation_key="return_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.DomesticHotWater],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="domestic_hot_water_temperature",
        translation_key="domestic_hot_water_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.DomesticHotWaterTarget],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="domestic_hot_water_temperature",
        translation_key="domestic_hot_water_temperature",
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Pressure.Water],
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        key="water_pressure",
        translation_key="water_pressure",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
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
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
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
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
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
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
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
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CentralHeating],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_central_heating_today",
        translation_key="energy_consumption_central_heating_today",
        data_retriever=SensorDataRetriever.TODAY,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CentralHeating],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_central_heating_current_month",
        translation_key="energy_consumption_central_heating_current_month",
        data_retriever=SensorDataRetriever.CURRENT_MONTH,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CentralHeating],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_central_heating_current_year",
        translation_key="energy_consumption_central_heating_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CentralHeating],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_central_heating_past_year",
        translation_key="energy_consumption_central_heating_past_year",
        data_retriever=SensorDataRetriever.PAST_YEAR,
        entity_registry_enabled_default=False,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.DomesticHotWater],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_domestic_hot_water_today",
        translation_key="energy_consumption_domestic_hot_water_today",
        data_retriever=SensorDataRetriever.TODAY,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.DomesticHotWater],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_domestic_hot_water_current_month",
        translation_key="energy_consumption_domestic_hot_water_current_month",
        data_retriever=SensorDataRetriever.CURRENT_MONTH,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.DomesticHotWater],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_domestic_hot_water_current_year",
        translation_key="energy_consumption_domestic_hot_water_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.DomesticHotWater],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_domestic_hot_water_past_year",
        translation_key="energy_consumption_domestic_hot_water_past_year",
        data_retriever=SensorDataRetriever.PAST_YEAR,
        entity_registry_enabled_default=False,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Cooling],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_cooling_today",
        translation_key="energy_consumption_cooling_today",
        data_retriever=SensorDataRetriever.TODAY,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Cooling],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_cooling_current_month",
        translation_key="energy_consumption_cooling_current_month",
        data_retriever=SensorDataRetriever.CURRENT_MONTH,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Cooling],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_cooling_current_year",
        translation_key="energy_consumption_cooling_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Cooling],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_cooling_past_year",
        translation_key="energy_consumption_cooling_past_year",
        data_retriever=SensorDataRetriever.PAST_YEAR,
        entity_registry_enabled_default=False,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Outside],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="outside_temperature",
        translation_key="outside_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.PrimaryHeatExchanger],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="primary_heat_exchanger_temperature",
        translation_key="primary_heat_exchanger_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.SecondaryHeatExchanger],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="secondary_heat_exchanger_temperature",
        translation_key="secondary_heat_exchanger_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.State.CentralHeatingPump],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="central_heating_pump_speed_percentage",
        translation_key="central_heating_pump_speed_percentage",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit1],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit1_temperature",
        translation_key="flow_circuit1_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit2],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit2_temperature",
        translation_key="flow_circuit2_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit3],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit3_temperature",
        translation_key="flow_circuit3_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit4],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit4_temperature",
        translation_key="flow_circuit4_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.CompressorInlet],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_inlet_temperature",
        translation_key="compressor_inlet_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Pressure.CompressorInlet],
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_inlet_pressure",
        translation_key="compressor_inlet_pressure",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.CompressorOutlet],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_outlet_temperature",
        translation_key="compressor_outlet_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Pressure.CompressorOutlet],
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_outlet_pressure",
        translation_key="compressor_outlet_pressure",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Room1],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="room1_temperature",
        translation_key="room1_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Room1Temperature],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Room2],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="room2_temperature",
        translation_key="room2_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Room2Temperature],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Room3],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="room3_temperature",
        translation_key="room3_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Room3Temperature],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Room4],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="room4_temperature",
        translation_key="room4_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_capabilities=[Capability.Room4Temperature],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Position.ExpansionValve1],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="expansion_valve1_position",
        translation_key="expansion_valve1_position",
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Position.ExpansionValve2],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="expansion_valve2_position",
        translation_key="expansion_valve2_position",
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.State.Allengra],
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        key="allengra_flow_rate",
        translation_key="allengra_flow_rate",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.State.Allengra],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="allengra_temperature",
        translation_key="allengra_temperature",
        data_retriever=SensorDataRetriever.TEMPERATURE,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.PrimaryInlet],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="primary_inlet_temperature",
        translation_key="primary_inlet_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.SecondaryOutlet],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="secondary_outlet_temperature",
        translation_key="secondary_outlet_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.EngineRoom],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="engine_room_temperature",
        translation_key="engine_room_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.CompressorOil],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_oil_temperature",
        translation_key="compressor_oil_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.Fan1],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="fan1_power",
        translation_key="fan1_power",
        icon="mdi:fan",
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
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
        required_capabilities=[Capability.Fan2],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.EconomizerLiquid],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="economizer_liquid_temperature",
        translation_key="economizer_liquid_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.EvaporationVapor],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="evaporation_vapor_temperature",
        translation_key="evaporation_vapor_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Speed.CompressorPercent],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="compressor_speed_percentage",
        translation_key="compressor_speed_percentage",
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.HeatingOutput],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="thermal_output_today",
        translation_key="thermal_output_today",
        data_retriever=SensorDataRetriever.TODAY,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CoolingOutput],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="cooling_output_today",
        translation_key="cooling_output_today",
        data_retriever=SensorDataRetriever.TODAY,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.WarmWaterOutput],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="warm_water_output_today",
        translation_key="warm_water_output_today",
        data_retriever=SensorDataRetriever.TODAY,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit1Target],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit_1_supply_temp_setpoint",
        translation_key="flow_circuit_1_supply_temp_setpoint",
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit2Target],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit_2_supply_temp_setpoint",
        translation_key="flow_circuit_2_supply_temp_setpoint",
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit3Target],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit_3_supply_temp_setpoint",
        translation_key="flow_circuit_3_supply_temp_setpoint",
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit4Target],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_circuit_4_supply_temp_setpoint",
        translation_key="flow_circuit_4_supply_temp_setpoint",
        data_retriever=SensorDataRetriever.RAW,
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Speed.CompressorRps],
        native_unit_of_measurement="rps",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        key="compressor_speed_rpm",
        translation_key="compressor_speed_rpm",
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.HeatingBuffer],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="heating_buffer_temperature",
        translation_key="heating_buffer_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.CoolingBuffer],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="cooling_buffer_temperature",
        translation_key="cooling_buffer_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.HeatingCoolingBuffer],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="heating_cooling_buffer_temperature",
        translation_key="heating_cooling_buffer_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.State.EnergyManagement],
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:home-battery-outline",
        key="energy_management_mode",
        translation_key="energy_management_mode",
        data_retriever=lambda data: ENERGY_MANAGEMENT_MODES_MAP.get(int(data)),
        options=[mode for mode in EnergyManagementMode],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Position.FourThreeWayValve],
        device_class=SensorDeviceClass.ENUM,
        key="four_three_way_valve_position",
        translation_key="four_three_way_valve_position",
        icon="mdi:valve",
        data_retriever=lambda data: FOUR_THREE_WAY_VALVE_POSITION_MAP.get(int(data)),
        options=[mode for mode in FourThreeWayValvePosition],
        required_device=Open3eDevices.Vitocal
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
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
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
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.AdditionalHeaterStatistics],
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="additional_heater_operating_hours",
        translation_key="additional_heater_operating_hours",
        data_retriever=SensorDataRetriever.HOURS,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.AdditionalHeaterStatistics],
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:counter",
        key="additional_heater_starts",
        translation_key="additional_heater_starts",
        data_retriever=SensorDataRetriever.STARTS,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.CompressorStatistics],
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="compressor_operating_hours",
        translation_key="compressor_operating_hours",
        data_retriever=SensorDataRetriever.HOURS,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Misc.CompressorStatistics],
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:counter",
        key="compressor_starts",
        translation_key="compressor_starts",
        data_retriever=SensorDataRetriever.STARTS,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Cop],
        native_unit_of_measurement="COP",
        icon="mdi:leaf",
        key="cop_total_current_year",
        translation_key="cop_total_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CopHeating],
        native_unit_of_measurement="COP",
        icon="mdi:leaf",
        key="cop_heating_current_year",
        translation_key="cop_heating_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.CopDhw],
        native_unit_of_measurement="COP",
        icon="mdi:leaf",
        key="cop_dhw_current_year",
        translation_key="cop_dhw_current_year",
        data_retriever=SensorDataRetriever.CURRENT_YEAR,
        required_device=Open3eDevices.Vitocal
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
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_charge_today",
        translation_key="battery_charge_today",
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_TODAY,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_charge_week",
        translation_key="battery_charge_week",
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_WEEK,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_charge_month",
        translation_key="battery_charge_month",
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_MONTH,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_charge_year",
        translation_key="battery_charge_year",
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_YEAR,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_charge_total",
        translation_key="battery_charge_total",
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_TOTAL,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_discharge_today",
        translation_key="battery_discharge_today",
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_TODAY,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_discharge_week",
        translation_key="battery_discharge_week",
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_WEEK,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_discharge_month",
        translation_key="battery_discharge_month",
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_MONTH,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_discharge_year",
        translation_key="battery_discharge_year",
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_YEAR,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Battery],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="battery_discharge_total",
        translation_key="battery_discharge_total",
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_TOTAL,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.Grid],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="grid_power_current",
        translation_key="grid_power_current",
        data_retriever=SensorDataRetriever.ACTIVE_POWER,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.Battery],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="battery_power_current",
        translation_key="battery_power_current",
        data_retriever=SensorDataRetriever.RAW,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.PV],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="pv_power_current",
        translation_key="pv_power_current",
        data_retriever=SensorDataRetriever.PV_POWER_CUMULATED,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.PV],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="pv_power_string_1_current",
        translation_key="pv_power_string_1_current",
        data_retriever=SensorDataRetriever.PV_POWER_STRING_1,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.PV],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="pv_power_string_2_current",
        translation_key="pv_power_string_2_current",
        data_retriever=SensorDataRetriever.PV_POWER_STRING_2,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Power.PV],
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        key="pv_power_string_3_current",
        translation_key="pv_power_string_3_current",
        data_retriever=SensorDataRetriever.PV_POWER_STRING_3,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.PV],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="pv_energy_production_today",
        translation_key="pv_energy_production_today",
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_TODAY,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.PV],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="pv_energy_production_week",
        translation_key="pv_energy_production_week",
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_WEEK,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.PV],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="pv_energy_production_month",
        translation_key="pv_energy_production_month",
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_MONTH,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.PV],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="pv_energy_production_year",
        translation_key="pv_energy_production_year",
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_YEAR,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.PV],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="pv_energy_production_total",
        translation_key="pv_energy_production_total",
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_TOTAL,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Grid],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="grid_feed_in_energy",
        translation_key="grid_feed_in_energy",
        data_retriever=SensorDataRetriever.GRID_FEED_IN_ENERGY,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.Grid],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="grid_supplied_energy",
        translation_key="grid_supplied_energy",
        data_retriever=SensorDataRetriever.GRID_SUPPLIED_ENERGY,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.InverterAmbient],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="inverter_ambient_temperature",
        translation_key="inverter_ambient_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocharge
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.Battery],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="battery_temperature",
        translation_key="battery_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitocharge
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
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.SupplyAir],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="supply_air_temperature",
        translation_key="supply_air_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.ExtractAir],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="extract_air_temperature",
        translation_key="extract_air_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.ExhaustAir],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="exhaust_air_temperature",
        translation_key="exhaust_air_temperature",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Humidity.Outdoor],
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="outdoor_air_humidity",
        translation_key="outdoor_air_humidity",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Humidity.SupplyAir],
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="supply_air_humidity",
        translation_key="supply_air_humidity",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Humidity.ExtractAir],
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="extract_air_humidity",
        translation_key="extract_air_humidity",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Humidity.ExhaustAir],
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="exhaust_air_humidity",
        translation_key="exhaust_air_humidity",
        data_retriever=SensorDataRetriever.ACTUAL,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Speed.SupplyAirFan],
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        key="supply_air_fan_speed",
        translation_key="supply_air_fan_speed",
        data_retriever=lambda data: float(json_loads(data)["Actual"]) * 10,
        required_device=Open3eDevices.Vitoair
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Speed.ExhaustAirFan],
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        key="exhaust_air_fan_speed",
        translation_key="exhaust_air_fan_speed",
        data_retriever=lambda data: float(json_loads(data)["Actual"]) * 10,
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
        icon="mdi:fan",
        key="ventilation_level",
        translation_key="ventilation_level",
        data_retriever=lambda data: float(json_loads(data)["Acutual"]),
        # Acutual intended, typo on Open3e for VentilationLevel (533)
        required_device=Open3eDevices.Vitoair
    ),
)

## Sensors which are derived by calculation
DERIVED_SENSORS: tuple[Open3eDerivedSensorEntityDescription, ...] = (

    ################
    ### VITODENS ###
    ################

    ######### ENERGY-SENSORS #########
    Open3eDerivedSensorEntityDescription(
        poll_data_features=[
            Features.Energy.EnergyConsumptionCentralHeating, 
            Features.Energy.EnergyConsumptionDomesticHotWater
        ],
        device_class=SensorDeviceClass.ENERGY,
        key="EnergyConsumptionCentralTotalToday",
        translation_key="EnergyConsumptionCentralTotalToday",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        data_retrievers=[SensorDataRetriever.TODAY] * 2,
        compute_value=lambda heating, hotwater: heating + hotwater,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eDerivedSensorEntityDescription(
        poll_data_features=[
            Features.Energy.GeneratedCentralHeatingOutput, 
            Features.Energy.GeneratedDomesticHotWaterOutput
        ],
        device_class=SensorDeviceClass.ENERGY,
        key="GeneratedHeatingWaterOutputTotalToday",
        translation_key="GeneratedHeatingWaterOutputTotalToday",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        data_retrievers=[SensorDataRetriever.TODAY] * 2,
        compute_value=lambda heating, hotwater: heating + hotwater,
        required_device=Open3eDevices.Vitodens
    ),

    ######### TIME/DATE-SENSORS #########
# for future purposes, currently not used in code
#    Open3eDerivedSensorEntityDescription(
#        poll_data_features=[
#            Features.Time.LegionellaProtectionWeekday, 
#            Features.Time.LegionellaProtectionStartTime
#        ],
##        device_class=SensorDeviceClass.ENUM,
#        key="LegionellaProtectionWeekly",
#        translation_key="LegionellaProtectionWeekly",
#        icon="mdi:water-plus",
#        data_retrievers=[
#            lambda data: int(data),
#            SensorDataRetriever.TIME
#        ],
#        compute_value=lambda weekday, starttime: ConcStrLPWeekDay(weekday, starttime),
#        required_device=Open3eDevices.Vitodens
#    ),


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
        compute_value=lambda heating, cooling, dhw: heating + cooling + dhw,
        required_device=Open3eDevices.Vitocal
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
        ),
        required_device=Open3eDevices.Vitocal
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
        required_device=Open3eDevices.Vitocal
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
        ),
        required_device=Open3eDevices.Vitocal
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
        ),
        required_device=Open3eDevices.Vitocal
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
        ),
        required_device=Open3eDevices.Vitocal
    )
)
