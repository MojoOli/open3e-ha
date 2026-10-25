"""Number platform for open3e."""

from __future__ import annotations

from typing import cast

from homeassistant.components.number import NumberEntity, RestoreNumber
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.json import json_loads

from .coordinator import Open3eDataUpdateCoordinator
from .definitions.numbers import Open3eNumberEntityDescription, NUMBERS
from .definitions.open3e_data import Open3eDataDevice
from .entity import Open3eEntity
from .ha_data import Open3eDataConfigEntry
from .util import map_devices_to_entities


async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    device_number_map = map_devices_to_entities(
        entry.runtime_data.coordinator,
        NUMBERS
    )

    for device, numbers in device_number_map.items():
        async_add_entities(
            (Open3eNumber if number.local_default_value is None else Open3eLocalNumber)(
                coordinator=entry.runtime_data.coordinator,
                description=cast(Open3eNumberEntityDescription, number),
                device=device
            )
            for number in numbers
        )


class Open3eNumber(Open3eEntity, NumberEntity):
    entity_description: Open3eNumberEntityDescription

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eNumberEntityDescription,
            device: Open3eDataDevice
    ):
        super().__init__(coordinator, description, device)

    @property
    def available(self):
        """Return True if entity is available."""
        return self.native_value is not None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if self.entity_description.set_native_value is None:
            return

        await self.entity_description.set_native_value(value, self.device, self.coordinator)

    async def async_on_data(self, feature_id: int) -> None:
        """Handle updated data from MQTT."""
        if self.entity_description.get_native_value is None:
            return

        self._attr_native_value = self.entity_description.get_native_value(json_loads(self.data[feature_id]))
        self.async_write_ha_state()


class Open3eLocalNumber(Open3eNumber, RestoreNumber):
    """Number whose value only lives in HA because no DID holds it."""

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        last_number_data = await self.async_get_last_number_data()
        if last_number_data is not None and last_number_data.native_value is not None:
            self._attr_native_value = last_number_data.native_value
        else:
            self._attr_native_value = self.entity_description.local_default_value

        await self.entity_description.set_local_value(self._attr_native_value, None, self.device, self.coordinator)
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        self._attr_native_value = value
        self.async_write_ha_state()

        feature_id = self.entity_description.poll_data_features[0].id
        await self.entity_description.set_local_value(value, self.data.get(feature_id), self.device, self.coordinator)
