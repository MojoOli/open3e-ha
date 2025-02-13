from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, UnitOfPressure, UnitOfEnergy, UnitOfSpeed, PERCENTAGE
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
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.FlowTemperature],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="flow_temperature",
        translation_key="flow_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.ReturnTemperature],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="return_temperature",
        translation_key="return_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.DomesticHotWaterTemperature],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="domestic_hot_water_temperature",
        translation_key="domestic_hot_water_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Pressure.WaterPressure],
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        key="water_pressure",
        translation_key="water_pressure",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.EnergyConsumptionCentralHeatingToday],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_central_heating_today",
        translation_key="energy_consumption_central_heating_today",
        data_retriever=SensorDataRetriever.TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.EnergyConsumptionDomesticHotWaterToday],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_domestic_hot_water_today",
        translation_key="energy_consumption_domestic_hot_water_today",
        data_retriever=SensorDataRetriever.TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Energy.EnergyConsumptionCoolingToday],
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        key="energy_consumption_cooling_today",
        translation_key="energy_consumption_cooling_today",
        data_retriever=SensorDataRetriever.TODAY
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.OutsideTemperature],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="outside_temperature",
        translation_key="outside_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.PrimaryHeatExchangerTemperature],
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        key="primary_heat_exchanger_temperature",
        translation_key="primary_heat_exchanger_temperature",
        data_retriever=SensorDataRetriever.ACTUAL
    ),
    Open3eSensorEntityDescription(
        poll_data_features=[Features.Temperature.SecondaryHeatExchangerTemperature],
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
)
