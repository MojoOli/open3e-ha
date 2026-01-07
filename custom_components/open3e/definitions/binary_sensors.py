from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription, BinarySensorDeviceClass
from homeassistant.util.json import json_loads

from .devices import Open3eDevices
from .entity_description import Open3eEntityDescription
from .features import Features
from ..capability.capability import Capability


class BinarySensorDataTransform:
    """Data transform functions for MQTT binary on/off state."""

    POWERSTATE = lambda data: json_loads(data)["PowerState"] > 0
    STATE = lambda data: json_loads(data)["State"] > 0
    HYGIENE_ACTIVE = lambda data: json_loads(data)["HygenieActive"] > 0
    BACKUP_BOX_INSTALLED = lambda data: json_loads(data)["Unknown"] > 0 #TODO: Needs to be renamed when open3e is updated to BackUpBoxInstalled
    HEX_ON = lambda data: data != "000000"  # on
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
        poll_data_features=[Features.State.AdditionalHeater],
        key="additional_heater_active",
        translation_key="additional_heater_active",
        icon="mdi:power",
        data_transform=BinarySensorDataTransform.POWERSTATE,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.HeatPumpCompressor],
        key="heat_pump_compressor_active",
        translation_key="heat_pump_compressor_active",
        icon="mdi:power",
        data_transform=BinarySensorDataTransform.POWERSTATE,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.CircuitFrostProtection],
        key="circuit_frost_protection",
        translation_key="circuit_frost_protection",
        icon="mdi:snowflake-melt",
        data_transform=BinarySensorDataTransform.STATE,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.CentralHeatingPump],
        key="circuit_pump",
        translation_key="circuit_pump",
        icon="mdi:water-sync",
        data_transform=BinarySensorDataTransform.STATE,
        required_device=Open3eDevices.Vitocal
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.Circuit1Pump],
        key="circuit_1_pump",
        translation_key="circuit_1_pump",
        icon="mdi:water-sync",
        data_transform=BinarySensorDataTransform.POWERSTATE,
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.Circuit2Pump],
        key="circuit_2_pump",
        translation_key="circuit_2_pump",
        icon="mdi:water-sync",
        data_transform=BinarySensorDataTransform.POWERSTATE,
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.Circuit3Pump],
        key="circuit_3_pump",
        translation_key="circuit_3_pump",
        icon="mdi:water-sync",
        data_transform=BinarySensorDataTransform.POWERSTATE,
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.Circuit4Pump],
        key="circuit_4_pump",
        translation_key="circuit_4_pump",
        icon="mdi:water-sync",
        data_transform=BinarySensorDataTransform.POWERSTATE,
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        poll_data_features=[Features.State.DomesticHotWaterCirculationPumpMode],
        key="hot_water_circulation_pump_hygiene",
        translation_key="hot_water_circulation_pump_hygiene",
        icon="mdi:bacteria-outline",
        data_transform=BinarySensorDataTransform.HYGIENE_ACTIVE,
        required_device=Open3eDevices.Vitocal
    ),
    
    ##################
    ### VITOCHARGE ###
    ##################

    Open3eBinarySensorEntityDescription(
        #device_class=None,
        poll_data_features=[Features.State.BackUpBox],
        key="backup_box_installed",
        translation_key="backup_box_installed",
        icon="mdi:power-plug-battery",
        data_transform=BinarySensorDataTransform.BACKUP_BOX_INSTALLED,
        required_device=Open3eDevices.Vitocharge
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
        data_transform=BinarySensorDataTransform.HEX_ON,
        required_device=Open3eDevices.Vitoair
    ),
)
