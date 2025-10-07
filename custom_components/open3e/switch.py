"""Number platform for open3e."""

from __future__ import annotations

from typing import cast, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.json import json_loads

from .coordinator import Open3eDataUpdateCoordinator
from .definitions.open3e_data import Open3eDataDevice
from .definitions.switches import Open3eSwitchEntityDescription, SWITCHES
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
        SWITCHES
    )

    for device, switches in device_number_map.items():
        async_add_entities(
            Open3eSwitch(
                coordinator=entry.runtime_data.coordinator,
                description=cast(Open3eSwitchEntityDescription, switch),
                device=device
            )
            for switch in switches
        )


class Open3eSwitch(Open3eEntity, SwitchEntity):
    entity_description: Open3eSwitchEntityDescription

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eSwitchEntityDescription,
            device: Open3eDataDevice
    ):
        super().__init__(coordinator, description, device)

    @property
    def available(self):
        """Return True if entity is available."""
        return self._attr_is_on is not None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if self.entity_description.turn_on is None:
            return

        await self.entity_description.turn_on(self.device, self.coordinator)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        if self.entity_description.turn_off is None:
            return

        await self.entity_description.turn_off(self.device, self.coordinator)

    async def async_on_data(self, feature_id: int) -> None:
        """Handle updated data from MQTT."""
        if self.entity_description.is_on_state is None:
            return

        self._attr_is_on = self.entity_description.is_on_state(json_loads(self.data[feature_id]))
        self.async_write_ha_state()
