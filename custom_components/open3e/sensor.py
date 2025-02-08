"""Sensor platform for open3e."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import Open3eDataUpdateCoordinator
from .definitions.sensors import Open3eSensorEntityDescription
from .definitions.sensors import SENSORS
from .entity import Open3eEntity
from .ha_data import Open3eDataConfigEntry


async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        Open3eSensor(
            coordinator=entry.runtime_data.coordinator,
            description=description
        )
        for description in SENSORS
        if description.has_features(entry.runtime_data.coordinator.config)
    )


class Open3eSensor(Open3eEntity, SensorEntity):
    entity_description: Open3eSensorEntityDescription

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eSensorEntityDescription
    ):
        super().__init__(coordinator, description)

    @property
    def available(self):
        """Return True if entity is available."""
        return self._attr_native_value is not None

    async def async_on_data(self, feature_id: int) -> None:
        """Handle updated data from MQTT."""
        self._attr_native_value = self.__filter_data(self.data[feature_id])
        self.async_write_ha_state()

    def __filter_data(self, data: Any):
        return self.entity_description.data_retriever(data)
