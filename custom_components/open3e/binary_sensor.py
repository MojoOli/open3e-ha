"""Sensor platform for open3e."""

from __future__ import annotations

from typing import Any, cast

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import Open3eDataUpdateCoordinator
from .definitions.binary_sensors import BINARY_SENSORS, Open3eBinarySensorEntityDescription
from .definitions.open3e_data import Open3eDataDevice
from .entity import Open3eEntity
from .ha_data import Open3eDataConfigEntry
from .util import map_devices_to_entities


async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    device_binary_sensor_map = map_devices_to_entities(
        entry.runtime_data.coordinator,
        BINARY_SENSORS
    )

    for device, binary_sensors in device_binary_sensor_map.items():
        async_add_entities(
            Open3eBinarySensor(
                coordinator=entry.runtime_data.coordinator,
                description=cast(Open3eBinarySensorEntityDescription, bs),
                device=device
            )
            for bs in binary_sensors
        )


class Open3eBinarySensor(Open3eEntity, BinarySensorEntity):
    entity_description: Open3eBinarySensorEntityDescription

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eBinarySensorEntityDescription,
            device: Open3eDataDevice
    ):
        super().__init__(coordinator, description, device)

    @property
    def available(self):
        """Return True if entity is available."""
        return self._attr_is_on is not None

    async def async_on_data(self, feature_id: int) -> None:
        """Handle updated data from MQTT."""
        self._attr_is_on = self.__transform_data(self.data[feature_id])
        self.async_write_ha_state()

    def __transform_data(self, data: Any):
        return self.entity_description.data_transform(data)
