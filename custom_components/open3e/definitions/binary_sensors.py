from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription, BinarySensorDeviceClass
from homeassistant.util.json import json_loads

from .entity_description import Open3eEntityDescription
from .features import Features


class BinarySensorDataTransform:
    """Data transform functions for MQTT binary on/off state."""

    POWERSTATE = lambda data: json_loads(data)["PowerState"] > 0
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
)
