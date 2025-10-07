"""Number platform for open3e."""

from __future__ import annotations

from typing import cast

from homeassistant.components.number import NumberEntity
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
            Open3eNumber(
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
