"""Sensor platform for open3e."""

from __future__ import annotations

from typing import Any, cast

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import VIESSMANN_UNAVAILABLE_VALUE

from .coordinator import Open3eDataUpdateCoordinator
from .definitions.open3e_data import Open3eDataDevice
from .definitions.sensors import Open3eSensorEntityDescription
from .definitions.sensors import SENSORS
from .entity import Open3eEntity
from .ha_data import Open3eDataConfigEntry
from .util import map_devices_to_entities


async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    device_sensor_map = map_devices_to_entities(
        entry.runtime_data.coordinator,
        SENSORS
    )

    for device, sensors in device_sensor_map.items():
        async_add_entities(
            Open3eSensor(
                coordinator=entry.runtime_data.coordinator,
                description=cast(Open3eSensorEntityDescription, sensor),
                device=device
            )
            for sensor in sensors
        )


class Open3eSensor(Open3eEntity, SensorEntity):
    entity_description: Open3eSensorEntityDescription

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eSensorEntityDescription,
            device: Open3eDataDevice
    ):
        super().__init__(coordinator, description, device)

    @property
    def available(self):
        """Return True if entity is available."""
        if self._attr_native_value is None:
            return False

        if isinstance(self._attr_native_value, (int, float)):
            if self.entity_description.device_class == SensorDeviceClass.TEMPERATURE and self._attr_native_value <= VIESSMANN_UNAVAILABLE_VALUE:
                return False
        return self.entity_description.is_available(self._attr_native_value)

    async def async_on_data(self, feature_id: int) -> None:
        """Handle updated data from MQTT."""
        self._attr_native_value = float(self.__filter_data(self.data[feature_id]))
        self.async_write_ha_state()

    def __filter_data(self, data: Any):
        return self.entity_description.data_retriever(data)
