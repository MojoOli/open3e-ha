from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription, BinarySensorDeviceClass
from homeassistant.util.json import json_loads

from .entity_description import Open3eEntityDescription
from .features import Features


class BinarySensorDataTransform:
    """Data transform functions for MQTT binary on/off state."""

    POWERSTATE = lambda data: json_loads(data)["PowerState"] > 0
    STATE = lambda data: json_loads(data)["State"] > 0
    HYGIENE_ACTIVE = lambda data: json_loads(data)["HygenieActive"] > 0
    HEX_ON = lambda data: data == "011400"  # on
    RAW = lambda data: data
    """The data state represents a raw value without any encapsulation."""


@dataclass(frozen=True)
class Open3eBinarySensorEntityDescription(
    Open3eEntityDescription, BinarySensorEntityDescription
):
    """Default binary sensor entity description for open3e."""
    domain: str = "binary_sensor"
    data_transform: Callable[[Any], Any] | None = None


BINARY_SENSORS: tuple[Open3eBinarySensorEntityDescription, ...] = (

    ###############
    ### VITOCAL ###
    ###############

    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.Heater],
        key="heater_active",
        translation_key="heater_active",
        icon="mdi:power",
        data_transform=BinarySensorDataTransform.POWERSTATE
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.HeatPumpCompressor],
        key="heat_pump_compressor_active",
        translation_key="heat_pump_compressor_active",
        icon="mdi:power",
        data_transform=BinarySensorDataTransform.POWERSTATE
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.CircuitFrostProtection],
        key="circuit_frost_protection",
        translation_key="circuit_frost_protection",
        icon="mdi:snowflake-melt",
        data_transform=BinarySensorDataTransform.STATE
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.CentralHeatingPump],
        key="circuit_pump",
        translation_key="circuit_pump",
        icon="mdi:water-sync",
        data_transform=BinarySensorDataTransform.STATE
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.HotWaterCirculationPump],
        key="hot_water_circulation_pump",
        translation_key="hot_water_circulation_pump",
        icon="mdi:water-sync",
        data_transform=BinarySensorDataTransform.STATE
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.DomesticHotWaterCirculationPumpMode],
        key="hot_water_circulation_pump_hygiene",
        translation_key="hot_water_circulation_pump_hygiene",
        icon="mdi:bacteria-outline",
        data_transform=BinarySensorDataTransform.HYGIENE_ACTIVE
    ),

    ###############
    ### VitoAir ###
    ###############

    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.FrostProtection],
        key="frost_protection",
        translation_key="frost_protection",
        icon="mdi:snowflake-melt",
        data_transform=BinarySensorDataTransform.HEX_ON
    ),
)
