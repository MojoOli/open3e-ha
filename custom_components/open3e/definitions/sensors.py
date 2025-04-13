from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, UnitOfPressure, UnitOfEnergy, PERCENTAGE, UnitOfPower
from homeassistant.util.json import json_loads

from .entity_description import Open3eEntityDescription
from .features import Features


class SensorDataRetriever:
    """Retriever functions for MQTT sensor data."""

    ACTUAL = lambda data: json_loads(data)["Actual"]
    MINIMUM = lambda data: json_loads(data)["Minimum"]
    MAXIMUM = lambda data: json_loads(data)["Maximum"]
    AVERAGE = lambda data: json_loads(data)["Average"]
    TODAY = lambda data: json_loads(data)["Today"]
    CURRENT_MONTH = lambda data: json_loads(data)["CurrentMonth"]
    CURRENT_YEAR = lambda data: json_loads(data)["CurrentYear"]
    BATTERY_CHARGE_TODAY = lambda data: json_loads(data)["BatteryChargeToday"]
    BATTERY_CHARGE_WEEK = lambda data: json_loads(data)["BatteryChargeWeek"]
    BATTERY_CHARGE_MONTH = lambda data: json_loads(data)["BatteryChargeMonth"]
    BATTERY_CHARGE_YEAR = lambda data: json_loads(data)["BatteryChargeYear"]
    BATTERY_CHARGE_TOTAL = lambda data: json_loads(data)["BatteryChargeTotal"]
    BATTERY_DISCHARGE_TODAY = lambda data: json_loads(data)["BatteryDischargeToday"]
    BATTERY_DISCHARGE_WEEK = lambda data: json_loads(data)["BatteryDischargeWeek"]
    BATTERY_DISCHARGE_MONTH = lambda data: json_loads(data)["BatteryDischargeMonth"]
    BATTERY_DISCHARGE_YEAR = lambda data: json_loads(data)["BatteryDischargeYear"]
    BATTERY_DISCHARGE_TOTAL = lambda data: json_loads(data)["BatteryDischargeTotal"]
    PV_ENERGY_PRODUCTION_TODAY = lambda data: json_loads(data)["PhotovoltaicProductionToday"]
    PV_ENERGY_PRODUCTION_WEEK = lambda data: json_loads(data)["PhotovoltaicProductionWeek"]
    PV_ENERGY_PRODUCTION_MONTH = lambda data: json_loads(data)["PhotovoltaicProductionMonth"]
    PV_ENERGY_PRODUCTION_YEAR = lambda data: json_loads(data)["PhotovoltaicProductionYear"]
    PV_ENERGY_PRODUCTION_TOTAL = lambda data: json_loads(data)["PhotovoltaicProductionTotal"]
    PV_POWER_STRING_1 = lambda data: (lambda val: val if val < 65000 else 0)(json_loads(data)["String1"])
    PV_POWER_STRING_2 = lambda data: (lambda val: val if val < 65000 else 0)(json_loads(data)["String2"])
    PV_POWER_STRING_3 = lambda data: (lambda val: val if val < 65000 else 0)(json_loads(data)["String3"])
    RAW = lambda data: data
    """The data state represents a raw value without any encapsulation."""


@dataclass(frozen=True)
class Open3eSensorEntityDescription(
    Open3eEntityDescription, SensorEntityDescription
):
    """Default sensor entity description for open3e."""
    domain: str = "sensor"
    data_retriever: Callable[[Any], Any] | None = None


SENSORS: tuple[Open3eSensorEntityDescription, ...] = (

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
        poll_data_features=[Features.Speed.CentralHeatingPump],
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        key="central_heating_pump_speed_percentage",
        translation_key="central_heating_pump_speed_percentage",
        data_retriever=SensorDataRetriever.ACTUAL
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
        data_retriever=SensorDataRetriever.BATTERY_CHARGE_WEEK,
        entity_registry_enabled_default=False
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
        entity_registry_enabled_default=False
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
        entity_registry_enabled_default=False
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
        data_retriever=SensorDataRetriever.BATTERY_DISCHARGE_WEEK,
        entity_registry_enabled_default=False
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
        entity_registry_enabled_default=False
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
        entity_registry_enabled_default=False
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
        data_retriever=SensorDataRetriever.PV_ENERGY_PRODUCTION_WEEK,
        entity_registry_enabled_default=False
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
        entity_registry_enabled_default=False
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
        entity_registry_enabled_default=False
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
)
