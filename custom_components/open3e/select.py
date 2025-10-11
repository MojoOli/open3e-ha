"""Number platform for open3e."""

from __future__ import annotations

from typing import cast

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.json import json_loads

from .coordinator import Open3eDataUpdateCoordinator
from .definitions.open3e_data import Open3eDataDevice
from .definitions.select import Open3eSelectEntityDescription, SELECTS
from .entity import Open3eEntity
from .ha_data import Open3eDataConfigEntry
from .util import map_devices_to_entities


async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    device_select_map = map_devices_to_entities(
        entry.runtime_data.coordinator,
        SELECTS
    )

    for device, selects in device_select_map.items():
        async_add_entities(
            Open3eSelect(
                coordinator=entry.runtime_data.coordinator,
                description=cast(Open3eSelectEntityDescription, select),
                device=device
            )
            for select in selects
        )


class Open3eSelect(Open3eEntity, SelectEntity):
    entity_description: Open3eSelectEntityDescription

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eSelectEntityDescription,
            device: Open3eDataDevice
    ):
        super().__init__(coordinator, description, device)
        self._attr_current_option = None

    @property
    def available(self):
        """Return True if entity is available."""
        return self._attr_current_option is not None

    async def async_select_option(self, option: str) -> None:
        """Set new value."""
        if self.entity_description.set_option is None:
            return

        await self.entity_description.set_option(option, self.device, self.coordinator)

    async def async_on_data(self, feature_id: int) -> None:
        """Handle updated data from MQTT."""
        if self.entity_description.get_option is None:
            return

        self._attr_current_option = self.entity_description.get_option(json_loads(self.data[feature_id]))
        self.async_write_ha_state()
