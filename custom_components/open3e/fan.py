"""Water heater platform for open3e."""

from __future__ import annotations

import asyncio
from typing import cast

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.json import json_loads
from homeassistant.util.percentage import ranged_value_to_percentage, percentage_to_ranged_value
from homeassistant.util.scaling import int_states_in_range

from .coordinator import Open3eDataUpdateCoordinator
from .definitions.fan import FAN, Open3eFanEntityDescription
from .definitions.open3e_data import Open3eDataDevice
from .definitions.subfeatures.ventilation_mode import VentilationMode
from .entity import Open3eEntity
from .ha_data import Open3eDataConfigEntry
from .util import map_devices_to_entities

VENTILATION_SPEED_RANGE = (1, 4)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    device_fan_map = map_devices_to_entities(
        entry.runtime_data.coordinator,
        FAN
    )

    # Add entities for each device
    for device, fans in device_fan_map.items():
        async_add_entities(
            Open3eFan(
                coordinator=entry.runtime_data.coordinator,
                description=cast(Open3eFanEntityDescription, fan),
                device=device
            )
            for fan in fans
        )


class Open3eFan(Open3eEntity, FanEntity):
    """Open3e Fan"""
    entity_description: Open3eFanEntityDescription
    current_speed_level: int | None
    current_mode: VentilationMode | None

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eFanEntityDescription,
            device: Open3eDataDevice
    ):
        super().__init__(coordinator, description, device)
        self._attr_supported_features = (
                FanEntityFeature.SET_SPEED
                | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = int_states_in_range(VENTILATION_SPEED_RANGE)
        self._attr_preset_modes = list(VentilationMode)
        self.current_speed_level = None
        self.current_mode = None

    @property
    def percentage(self) -> int | None:
        """Return the current percentage of the fan."""
        return ranged_value_to_percentage(VENTILATION_SPEED_RANGE, self.current_speed_level)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the fan's current speed."""
        # Percentage can only be set in continuous mode
        if self.current_mode != VentilationMode.Continuous:
            await self.async_set_ventilation_mode(VentilationMode.Continuous)
            # Wait for program to be set
            await asyncio.sleep(1)

        level = percentage_to_ranged_value(VENTILATION_SPEED_RANGE, percentage)
        await self.coordinator.async_set_ventilation_level(
            feature_id=self.entity_description.speed_level_feature.id,
            level=level,
            device=self.device
        )

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode"""
        return self.current_mode

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self.async_set_ventilation_mode(VentilationMode.from_str(preset_mode))

    async def async_set_ventilation_mode(self, mode: VentilationMode) -> None:
        await self.coordinator.async_set_ventilation_mode(
            feature_id=self.entity_description.mode_feature.id,
            mode=mode,
            device=self.device
        )

    @property
    def is_on(self) -> bool | None:
        return self.current_speed_level is not None

    @property
    def available(self):
        return self.current_speed_level is not None and self.current_speed_level < 255

    async def async_on_data(self, feature_id: int):
        """Handle updated data from MQTT."""
        match feature_id:
            case self.entity_description.speed_level_feature.id:
                self.current_speed_level = int(json_loads(self.data[feature_id])["Acutual"])  # intended, typo on Open3e

            case self.entity_description.mode_feature.id:
                self.current_mode = VentilationMode.from_operation_mode(
                    json_loads(self.data[feature_id])["Mode"])

        self.async_write_ha_state()
