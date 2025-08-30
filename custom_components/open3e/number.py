"""Number platform for open3e."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.json import json_loads

from .coordinator import Open3eDataUpdateCoordinator
from .definitions.numbers import Open3eNumberEntityDescription, NUMBERS
from .entity import Open3eEntity
from .ha_data import Open3eDataConfigEntry


async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        Open3eNumber(
            coordinator=entry.runtime_data.coordinator,
            description=description
        )
        for description in NUMBERS
        if description.has_features(entry.runtime_data.coordinator.system_information)
    )


class Open3eNumber(Open3eEntity, NumberEntity):
    entity_description: Open3eNumberEntityDescription

    __programs: Any | None = None

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eNumberEntityDescription
    ):
        super().__init__(coordinator, description)

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        if self.__programs is None:
            return None

        return self.__programs[self.entity_description.program.map_to_api()]

    @property
    def available(self):
        """Return True if entity is available."""
        return self.native_value is not None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        self.__programs[self.entity_description.program.map_to_api()] = value

        await self.coordinator.async_set_program_temperature(
            set_programs_feature_id=self.entity_description.poll_data_features[0].id,
            program=self.entity_description.program,
            temperature=value
        )

    async def async_on_data(self, feature_id: int) -> None:
        """Handle updated data from MQTT."""
        self.__programs = json_loads(self.data[feature_id])
        self.async_write_ha_state()
