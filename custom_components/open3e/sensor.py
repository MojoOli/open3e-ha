"""Sensor platform for open3e."""

from __future__ import annotations

from typing import Any, cast

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import VIESSMANN_UNAVAILABLE_VALUE

from .coordinator import Open3eDataUpdateCoordinator
from .definitions.open3e_data import Open3eDataDevice
from .definitions.sensors import Open3eSensorEntityDescription, DERIVED_SENSORS, Open3eDerivedSensorEntityDescription
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

    device_derived_sensor_map = map_devices_to_entities(
        entry.runtime_data.coordinator,
        DERIVED_SENSORS
    )

    for device, sensors in device_derived_sensor_map.items():
        async_add_entities(
            Open3eDerivedSensor(
                coordinator=entry.runtime_data.coordinator,
                description=cast(Open3eDerivedSensorEntityDescription, sensor),
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

        return True

    async def async_on_data(self, feature_id: int) -> None:
        """Handle updated data from MQTT."""
        self._attr_native_value = self.__filter_data(self.data[feature_id])
        self.async_write_ha_state()

    def __filter_data(self, data: Any):
        return self.entity_description.data_retriever(data)


class Open3eDerivedSensor(Open3eEntity, SensorEntity):
    entity_description: Open3eDerivedSensorEntityDescription

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eDerivedSensorEntityDescription,
            device: Open3eDataDevice
    ):
        super().__init__(coordinator, description, device)
        # store a temporary buffer for incoming feature data
        self.__pending_data: dict[int, Any] = {}

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._attr_native_value is not None

    async def async_on_data(self, feature_id: int) -> None:
        """Handle updated data from MQTT."""
        # store the raw data in the buffer
        self.__pending_data[feature_id] = self.data[feature_id]

        # check if we have all required features
        required_features = self.entity_description.poll_data_features or []

        if all(feature.id in self.__pending_data for feature in required_features):
            # apply all data_retrievers to transform the data
            transformed_values = [
                retriever(self.__pending_data[feature.id])
                for retriever, feature in zip(
                    self.entity_description.data_retrievers or [],
                    required_features
                )
            ]

            # compute the derived value
            if self.entity_description.compute_value:
                self._attr_native_value = self.entity_description.compute_value(*transformed_values)
            else:
                self._attr_native_value = transformed_values[0] if transformed_values else None

            # write the state to HA and reset state
            self.async_write_ha_state()
            self.__pending_data = {}
