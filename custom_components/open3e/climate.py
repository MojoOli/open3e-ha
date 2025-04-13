"""Climate platform for open3e."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode, HVACAction
from homeassistant.const import UnitOfTemperature, PRECISION_TENTHS, PRECISION_WHOLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.json import json_loads

from .const import VIESSMANN_TEMP_HEATING_MIN, VIESSMANN_TEMP_HEATING_MAX
from .coordinator import Open3eDataUpdateCoordinator
from .definitions.climate import Open3eClimateEntityDescription, CLIMATE
from .definitions.program import Program
from .entity import Open3eEntity
from .ha_data import Open3eDataConfigEntry


async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        Open3eClimate(
            coordinator=entry.runtime_data.coordinator,
            description=description
        )
        for description in CLIMATE
        if description.has_features(entry.runtime_data.coordinator.system_information)
    )


class Open3eClimate(Open3eEntity, ClimateEntity):
    _attr_precision = PRECISION_TENTHS
    _attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = VIESSMANN_TEMP_HEATING_MIN
    _attr_max_temp = VIESSMANN_TEMP_HEATING_MAX
    _attr_target_temperature_step = PRECISION_WHOLE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO]

    __current_hvac_actions: list[HVACAction]

    __current_room_temperature: float | None = None
    __current_flow_temperature: float | None = None

    __current_program: Program | None = None
    __programs: Any | None = None

    entity_description: Open3eClimateEntityDescription

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eClimateEntityDescription
    ):
        super().__init__(coordinator, description)

        self._attr_preset_modes = [
            Program.Reduced.to_ha_preset_mode(),
            Program.Standard.to_ha_preset_mode(),
            Program.Comfort.to_ha_preset_mode()
        ]
        self._attr_preset_mode = Program.Standard.to_ha_preset_mode()
        self._attr_hvac_mode = HVACMode.AUTO
        self.__current_hvac_actions = [HVACAction.IDLE]

    @property
    def available(self):
        """Return True if the current flow temperature
        is not -3276.8 which is used when the circuit is not connected
        """
        return self.__current_flow_temperature > -1000

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running hvac operation if supported."""
        if HVACAction.OFF in self.__current_hvac_actions:
            return HVACAction.OFF

        if HVACAction.HEATING in self.__current_hvac_actions:
            return HVACAction.HEATING

        if HVACAction.FAN in self.__current_hvac_actions:
            return HVACAction.FAN

        return HVACAction.IDLE

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if self.__current_room_temperature is not None and self.__current_room_temperature > -100:
            return self.__current_room_temperature

        if self.__current_flow_temperature is not None and self.__current_flow_temperature > -100:
            return self.__current_flow_temperature

        return None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode, e.g., home, away, temp.

        Requires ClimateEntityFeature.PRESET_MODE.
        """
        if self.__current_program is None:
            return None

        return self.__current_program.to_ha_preset_mode()

    @property
    def target_temperature(self) -> str | None:
        """Return the current preset mode, e.g., home, away, temp.

        Requires ClimateEntityFeature.PRESET_MODE.
        """
        if self.__current_program is None or self.__programs is None:
            return None

        return self.__programs[self.__current_program]

    def set_preset_mode(self, preset_mode: str) -> None:
        """Setting the preset mode is not supported."""

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs["temperature"]
        self.__programs[self.__current_program] = temperature

        await self.coordinator.async_set_program_temperature(
            set_programs_feature_id=self.entity_description.programs_temperature_feature.id,
            program=self.__current_program,
            temperature=temperature
        )

    async def async_turn_on(self):
        """Turn the entity on."""
        await self.coordinator.async_turn_hvac_on(self.entity_description.hvac_mode_feature.id)

    async def async_turn_off(self):
        """Turn the entity off."""
        await self.coordinator.async_turn_hvac_off(self.entity_description.hvac_mode_feature.id)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
        else:
            await self.async_turn_on()

    async def async_on_data(self, feature_id: int):
        """Handle updated data from MQTT."""
        match feature_id:
            case self.entity_description.hvac_mode_feature.id:
                hvac_mode = json_loads(self.data[feature_id])

                self.__current_program = Program.from_text(hvac_mode["State"]["Text"])

                if hvac_mode["Mode"]["ID"] == 0:
                    self._attr_hvac_mode = HVACMode.OFF
                    self.__add_hvac_action(HVACAction.OFF)
                else:
                    self._attr_hvac_mode = HVACMode.AUTO
                    self.__remove_hvac_action(HVACAction.OFF)

            case self.entity_description.flow_temperature_feature.id:
                self.__current_flow_temperature = json_loads(self.data[feature_id])["Actual"]

            case self.entity_description.room_temperature_feature.id:
                self.__current_room_temperature = json_loads(self.data[feature_id])["Actual"]

            case self.entity_description.fan_power_state_feature.id:
                power_state = float(self.data[feature_id])

                if power_state == 0:
                    self.__remove_hvac_action(HVACAction.FAN)
                else:
                    self.__add_hvac_action(HVACAction.FAN)

            case self.entity_description.heater_state_feature.id:
                power_state = json_loads(self.data[feature_id])["PowerState"]

                if power_state == 0:
                    self.__remove_hvac_action(HVACAction.HEATING)
                else:
                    self.__add_hvac_action(HVACAction.HEATING)

            case self.entity_description.programs_temperature_feature.id:
                self.__programs = json_loads(self.data[feature_id])

        self.async_write_ha_state()

    def __remove_hvac_action(self, hvac_action: HVACAction):
        if hvac_action in self.__current_hvac_actions:
            self.__current_hvac_actions.remove(hvac_action)

    def __add_hvac_action(self, hvac_action: HVACAction):
        if hvac_action not in self.__current_hvac_actions:
            self.__current_hvac_actions.append(hvac_action)
