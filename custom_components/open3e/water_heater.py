"""Water heater platform for open3e."""

from __future__ import annotations

from typing import Any

from homeassistant.components.water_heater import WaterHeaterEntity, WaterHeaterEntityFeature
from homeassistant.const import UnitOfTemperature, PRECISION_TENTHS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.json import json_loads

from .const import VIESSMANN_TEMP_DHW_MIN, \
    VIESSMANN_TEMP_DHW_MAX
from .coordinator import Open3eDataUpdateCoordinator
from custom_components.open3e.definitions.subfeatures.dmw_mode import DmwMode
from .definitions.water_heater import WATER_HEATER, Open3eWaterHeaterEntityDescription
from .entity import Open3eEntity
from .ha_data import Open3eDataConfigEntry


async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        Open3eWaterHeater(
            coordinator=entry.runtime_data.coordinator,
            description=description
        )
        for description in WATER_HEATER
        if description.has_features(entry.runtime_data.coordinator.system_information)
    )


class Open3eWaterHeater(Open3eEntity, WaterHeaterEntity):
    """Open3e Water Heater"""
    _attr_precision = PRECISION_TENTHS
    _attr_supported_features = (
            WaterHeaterEntityFeature.TARGET_TEMPERATURE
            | WaterHeaterEntityFeature.OPERATION_MODE
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = VIESSMANN_TEMP_DHW_MIN
    _attr_max_temp = VIESSMANN_TEMP_DHW_MAX

    entity_description: Open3eWaterHeaterEntityDescription

    __currently_on: bool = True
    __current_efficiency_mode: int = 0

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eWaterHeaterEntityDescription
    ):
        super().__init__(coordinator, description)
        self._attr_current_operation = DmwMode.Eco.to_ha_preset_mode()
        self._attr_operation_list = [
            DmwMode.Eco.to_ha_preset_mode(),
            DmwMode.Comfort.to_ha_preset_mode(),
            DmwMode.Off.to_ha_preset_mode()
        ]

    @property
    def available(self):
        """Return True if entity has a target and current temperature"""
        return self.target_temperature is not None and self.current_temperature is not None

    async def async_on_data(self, feature_id: int):
        """Handle updated data from MQTT."""
        match feature_id:
            case self.entity_description.temperature_feature.id:
                temperature_state = json_loads(self.data[feature_id])

                self._attr_current_temperature = float(temperature_state["Actual"])
                self._attr_target_temperature_high = float(temperature_state["Maximum"])
                self._attr_target_temperature_low = float(temperature_state["Minimum"])

            case self.entity_description.temperature_target_feature.id:
                self._attr_target_temperature = float(self.data[feature_id])

            case self.entity_description.state_feature.id:
                self.__currently_on = json_loads(self.data[feature_id])["State"] == 1

            case self.entity_description.efficiency_mode_feature.id:
                self.__current_efficiency_mode = int(self.data[feature_id])

        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs["temperature"]
        await self.coordinator.async_set_hot_water_temperature(
            feature_id=self.entity_description.temperature_target_feature.id,
            temperature=temperature,
            device=self.device
        )

    @property
    def current_operation(self) -> str | None:
        """Return current operation ie. eco, electric, performance, ..."""
        if not self.__currently_on:
            return DmwMode.Off.to_ha_preset_mode()
        elif self.__current_efficiency_mode == 0:
            return DmwMode.Eco.to_ha_preset_mode()
        else:
            return DmwMode.Comfort.to_ha_preset_mode()

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""
        await self.coordinator.async_set_hot_water_mode(
            mode=DmwMode.from_ha_preset_mode(operation_mode),
            dmw_state_feature_id=self.entity_description.state_feature.id,
            dmw_efficiency_mode_feature_id=self.entity_description.efficiency_mode_feature.id,
            device=self.device
        )
