"""Climate platform for open3e."""

from __future__ import annotations

from typing import Any, cast

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode, HVACAction
from homeassistant.const import UnitOfTemperature, PRECISION_TENTHS, PRECISION_WHOLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.json import json_loads

from custom_components.open3e.definitions.subfeatures.program import Program
from .const import VIESSMANN_TEMP_HEATING_MIN, VIESSMANN_TEMP_HEATING_MAX, VIESSMANN_UNAVAILABLE_VALUE
from .coordinator import Open3eDataUpdateCoordinator
from .definitions.climate import Open3eClimateEntityDescription, CLIMATE
from .definitions.open3e_data import Open3eDataDevice
from .definitions.subfeatures.hvac_mode import HvacMode
from .entity import Open3eEntity
from .ha_data import Open3eDataConfigEntry
from .util import map_devices_to_entities


async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    device_climate_map = map_devices_to_entities(
        entry.runtime_data.coordinator,
        CLIMATE
    )

    for device, climates in device_climate_map.items():
        async_add_entities(
            Open3eClimate(
                coordinator=entry.runtime_data.coordinator,
                description=cast(Open3eClimateEntityDescription, climate),
                device=device
            )
            for climate in climates
        )


class Open3eClimate(Open3eEntity, ClimateEntity):
    __current_room_temperature: float | None
    __current_flow_temperature: float | None

    __current_program: Program | None
    __programs: Any | None

    entity_description: Open3eClimateEntityDescription

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eClimateEntityDescription,
            device: Open3eDataDevice
    ):
        super().__init__(coordinator, description, device)

        self._attr_preset_modes = list(Program)
        self._attr_preset_mode = Program.Normal
        self._attr_hvac_mode = HVACMode.AUTO
        self._attr_hvac_action = HVACAction.IDLE

        self._attr_precision = PRECISION_TENTHS
        self._attr_supported_features = (
                ClimateEntityFeature.TARGET_TEMPERATURE
                | ClimateEntityFeature.PRESET_MODE
                | ClimateEntityFeature.TURN_OFF
                | ClimateEntityFeature.TURN_ON
        )
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_min_temp = VIESSMANN_TEMP_HEATING_MIN
        self._attr_max_temp = VIESSMANN_TEMP_HEATING_MAX
        self._attr_target_temperature_step = PRECISION_WHOLE
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL]

        self.__current_room_temperature = None
        self.__current_flow_temperature = None

        self.__current_program = None
        self.__programs = None

    @property
    def available(self):
        """Return True if the current flow temperature
        is not -3276.8 which is used when the circuit is not connected
        """
        return self.__current_flow_temperature is not None and self.__current_flow_temperature > VIESSMANN_UNAVAILABLE_VALUE

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if self.__current_room_temperature is not None and self.__current_room_temperature > -100:
            return self.__current_room_temperature

        return None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode, e.g., home, away, temp.

        Requires ClimateEntityFeature.PRESET_MODE.
        """
        return self.__current_program

    @property
    def target_temperature(self) -> str | None:
        """Return the current preset mode, e.g., home, away, temp.

        Requires ClimateEntityFeature.PRESET_MODE.
        """
        if self.__current_program is None or self.__programs is None:
            return None

        return self.__programs[self.__current_program.map_to_api_heating()]

    def set_preset_mode(self, preset_mode: str) -> None:
        """Setting the preset mode is not possible."""

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs["temperature"]
        self.__programs[self.__current_program.map_to_api_heating()] = temperature

        await self.coordinator.async_set_program_temperature(
            set_programs_feature_id=self.entity_description.programs_temperature_feature.id,
            program=self.__current_program,
            temperature=temperature,
            device=self.device
        )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        """Set new target hvac mode."""
        await self.coordinator.async_set_hvac_mode(
            mode=HvacMode.from_ha_hvac_mode(hvac_mode),
            hvac_mode_feature_id=self.entity_description.hvac_mode_feature.id,
            device=self.device
        )

    async def async_on_data(self, feature_id: int):
        """Handle updated data from MQTT."""
        match feature_id:
            case self.entity_description.hvac_mode_feature.id:
                response = json_loads(self.data[feature_id])
                hvac_state = Program.from_operation_mode(response["State"]["ID"])
                hvac_mode = HvacMode.from_api(int(response["Mode"]["ID"]))

                self.__current_program = hvac_state
                self._attr_hvac_mode = HvacMode.to_ha_hvac_mode(hvac_mode)

                if hvac_mode == HvacMode.Off:
                    self._attr_hvac_action = HVACAction.OFF

            case self.entity_description.compressor_state_feature.id:
                power_state = json_loads(self.data[feature_id])["PowerState"]

                if self._attr_hvac_mode == HvacMode.Off:
                    self._attr_hvac_action = HVACAction.OFF
                else:
                    self._attr_hvac_action = HVACAction.IDLE if power_state == 0 else HVACAction.HEATING

            case self.entity_description.flow_temperature_feature.id:
                self.__current_flow_temperature = json_loads(self.data[feature_id])["Actual"]

            case self.entity_description.room_temperature_feature.id:
                self.__current_room_temperature = json_loads(self.data[feature_id])["Actual"]

            case self.entity_description.programs_temperature_feature.id:
                self.__programs = json_loads(self.data[feature_id])

        self.async_write_ha_state()
