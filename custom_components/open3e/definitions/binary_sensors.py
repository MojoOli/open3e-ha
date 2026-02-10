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

    ################
    ### VITODENS ###
    ################

    Open3eBinarySensorEntityDescription(
        poll_data_features=[Features.State.Flame],
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:fire",
        key="flame",
        translation_key="flame",
        data_transform=BinarySensorDataTransform.STATE,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eBinarySensorEntityDescription(
        poll_data_features=[Features.State.CentralHeatingPump],
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:water-sync",
        key="central_heating_pump",
        translation_key="central_heating_pump",
        data_transform=BinarySensorDataTransform.STATE,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eBinarySensorEntityDescription(
        poll_data_features=[Features.State.DomesticHotWaterCirculationPump],
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:water-sync",
        key="domestic_hot_water_circulation_pump",
        translation_key="domestic_hot_water_circulation_pump",
        data_transform=BinarySensorDataTransform.STATE,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eBinarySensorEntityDescription(
        poll_data_features=[Features.State.DomesticHotWaterOperationState],
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:water-sync",
        key="domestic_hot_water_operation_state",
        translation_key="domestic_hot_water_operation_state",
        entity_registry_enabled_default=False,
        data_transform=BinarySensorDataTransform.STATE,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eBinarySensorEntityDescription(
        poll_data_features=[Features.State.LegionellaProtectionActivation],
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:water-plus",
        key="legionella_protection_activation",
        translation_key="legionella_protection_activation",
        data_transform=BinarySensorDataTransform.STATE,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eBinarySensorEntityDescription(
        poll_data_features=[Features.State.MalfunctionHeatingUnitBlocked],
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:water-sync",
        key="malfunction_heating_unit_blocked",
        translation_key="malfunction_heating_unit_blocked",
        entity_registry_enabled_default=False,
        data_transform=lambda data: int(data) > 0,
        required_device=Open3eDevices.Vitodens
    ),
    Open3eBinarySensorEntityDescription(
        poll_data_features=[Features.State.MixerOneCircuitOperationState],
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:water-sync",
        key="mixer_one_circuit_operation_state",
        translation_key="mixer_one_circuit_operation_state",
        entity_registry_enabled_default=False,
        data_transform=lambda data: int(json_loads(data)["State"]["ID"]) < 255,
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eBinarySensorEntityDescription(
        poll_data_features=[Features.State.MixerTwoCircuitOperationState],
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:water-sync",
        key="mixer_two_circuit_operation_state",
        translation_key="mixer_two_circuit_operation_state",
        entity_registry_enabled_default=False,
        data_transform=lambda data: int(json_loads(data)["State"]["ID"]) < 255,
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eBinarySensorEntityDescription(
        poll_data_features=[Features.State.MixerThreeCircuitOperationState],
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:water-sync",
        key="mixer_three_circuit_operation_state",
        translation_key="mixer_three_circuit_operation_state",
        entity_registry_enabled_default=False,
        data_transform=lambda data: int(json_loads(data)["State"]["ID"]) < 255,
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitodens
    ),
    Open3eBinarySensorEntityDescription(
        poll_data_features=[Features.State.MixerFourCircuitOperationState],
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:water-sync",
        key="mixer_four_circuit_operation_state",
        translation_key="mixer_four_circuit_operation_state",
        entity_registry_enabled_default=False,
        data_transform=lambda data: int(json_loads(data)["State"]["ID"]) < 255,
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitodens
    ),



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
