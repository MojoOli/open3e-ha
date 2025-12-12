"""DataUpdateCoordinator for open3e."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.open3e.definitions.subfeatures.buffer import Buffer
from custom_components.open3e.definitions.subfeatures.dmw_mode import DmwMode
from custom_components.open3e.definitions.subfeatures.hysteresis import Hysteresis
from custom_components.open3e.definitions.subfeatures.program import Program
from custom_components.open3e.definitions.subfeatures.smart_grid_temperature_offsets import SmartGridTemperatureOffsets
from .api import Open3eMqttClient
from .const import DOMAIN
from .definitions.open3e_data import Open3eDataSystemInformation, Open3eDataDevice
from .definitions.subfeatures.buffer_mode import BufferMode
from .definitions.subfeatures.dhw_hysteresis import DhwHysteresis
from .definitions.subfeatures.heating_curve import HeatingCurve
from .definitions.subfeatures.hvac_mode import HvacMode
from .definitions.subfeatures.ventilation_mode import VentilationMode
from .definitions.subfeatures.vitoair_quick_mode import VitoairQuickMode
from .errors import Open3eCoordinatorUpdateFailed

_LOGGER = logging.getLogger(__name__)

from homeassistant.helpers import device_registry
from .definitions.features import Feature


@dataclass
class CoordinatorEndpoint:
    __last_refresh: float = -1
    __entities_subscribed: int = 1

    def __init__(self, refresh_interval: int):
        self.refresh_interval = refresh_interval

    def add_entity_subscription(self):
        self.__entities_subscribed += 1

    def remove_entity_subscription(self):
        self.__entities_subscribed -= 1
        return self.__entities_subscribed <= 0

    def set_refresh_interval(self, refresh_interval):
        if refresh_interval < self.refresh_interval:
            self.refresh_interval = refresh_interval

    def should_refresh(self, now: float):
        return now - self.__last_refresh > self.refresh_interval - 0.5  # let's use a range so we can make sure it gets refreshed

    def update_last_refresh(self, now: float):
        self.__last_refresh = now


class Open3eDataUpdateCoordinator(DataUpdateCoordinator):
    """
    Class to manage requesting for MQTT updates.
    MQTT updates subscriptions are retrieved in the entities rather than in this class.
    """

    __client: Open3eMqttClient
    __server_available: bool | None

    system_information: Open3eDataSystemInformation
    __device_registry: DeviceRegistry
    __entry_id: str

    __endpoints: dict[tuple[int, int], CoordinatorEndpoint]

    def __init__(self, hass, client: Open3eMqttClient, entry_id: str):
        super().__init__(
            hass,
            _LOGGER,
            name="Open3eDataUpdateCoordinator",
            update_interval=timedelta(seconds=5),
            always_update=True
        )
        self.__client = client
        self.__device_registry = device_registry.async_get(hass)
        self.__entry_id = entry_id
        self.__endpoints = {}
        self.__server_available = None

    async def _async_setup(self):
        """Set up the coordinator

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        await self.__client.async_check_availability(self.hass)
        await self.__client.async_subscribe_to_availability(
            hass=self.hass,
            callback=self.__on_availability_update
        )

        self.system_information = await self.__client.async_get_system_information(self.hass)
        for device in self.system_information.devices:

            # Check if multiple devices have the same name
            duplicate_count = sum(1 for d in self.system_information.devices if d.name == device.name)
            name_suffix = ""
            if duplicate_count > 1:
                # Add last 4 digits of serial number to differentiate in UI
                name_suffix = f" ({device.serial_number[-4:]})"

            self.__device_registry.async_get_or_create(
                config_entry_id=self.__entry_id,
                identifiers={(DOMAIN, device.serial_number)},
                manufacturer=device.manufacturer,
                serial_number=device.serial_number,
                sw_version=device.software_version,
                hw_version=device.hardware_version,
                name=device.name + name_suffix,
                model=device.name,
            )

    def __on_availability_update(self, available: bool):
        self.__server_available = available

    async def _async_update_data(self) -> bool:
        """Update data."""
        if self.__server_available is None:
            return True

        if not self.__server_available:
            raise Open3eCoordinatorUpdateFailed()

        now = time.time()
        device_features: dict[int, list[int]] = {}

        for (device_id, feature_id), endpoint in self.__endpoints.items():
            if endpoint.should_refresh(now):
                device_features.setdefault(device_id, []).append(feature_id)
                endpoint.update_last_refresh(now)

        if not device_features:
            return True

        _LOGGER.debug(f"Requesting data update for features {device_features}")
        await self.__client.async_request_data(self.hass, device_features)

        return True

    async def on_entity_added(self, features: list[Feature], device: Open3eDataDevice):
        """Called when an entity is added."""
        for feature in features:
            key = (device.id, feature.id)
            endpoint = self.__endpoints.get(key)
            if endpoint is None:
                self.__endpoints[key] = CoordinatorEndpoint(
                    refresh_interval=feature.refresh_interval
                )
            else:
                endpoint.add_entity_subscription()
                endpoint.set_refresh_interval(feature.refresh_interval)

    def on_entity_removed(self, features: list[Feature], device: Open3eDataDevice):
        """Called when an entity is removed."""
        _LOGGER.debug("Entity was removed from Coordinator")
        for feature in features:
            key = (device.id, feature.id)
            endpoint = self.__endpoints.get(key)
            if endpoint and endpoint.remove_entity_subscription():
                del self.__endpoints[key]

    def get_mqtt_topics_for_features(self, features: list[Feature], device: Open3eDataDevice):
        """Return MQTT topics matching a list of features for a device."""
        return [
            mqtt_topic for feature in features
            for mqtt_topic in device.features
            if mqtt_topic.id == feature.id
        ]

    async def async_set_program_temperature(
            self,
            set_programs_feature_id: int,
            program: Program,
            temperature: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_program_temperature(
            hass=self.hass,
            set_programs_feature_id=set_programs_feature_id,
            program=program,
            temperature=temperature,
            device_id=device.id
        )

        self.async_refresh_feature(device, [set_programs_feature_id])

    async def async_set_program_temperature_cooling(
            self,
            set_programs_feature_id: int,
            program: Program,
            temperature: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_program_temperature_cooling(
            hass=self.hass,
            set_programs_feature_id=set_programs_feature_id,
            program=program,
            temperature=temperature,
            device_id=device.id
        )

        self.async_refresh_feature(device, [set_programs_feature_id])

    async def async_set_hot_water_temperature(
            self,
            feature_id: int,
            temperature: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_hot_water_temperature(
            hass=self.hass,
            feature_id=feature_id,
            temperature=temperature,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_hvac_mode(self, mode: HvacMode, hvac_mode_feature_id: int, device: Open3eDataDevice):
        await self.__client.async_set_hvac_mode(self.hass, mode, hvac_mode_feature_id, device.id)
        # Wait for 4 seconds to request hvac mode
        # this takes a bit longer hence the longer wait time

        self.async_refresh_feature(device, [hvac_mode_feature_id])

    async def async_set_hot_water_mode(
            self,
            mode: DmwMode,
            dmw_state_feature_id: int,
            dmw_efficiency_mode_feature_id: int,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_dmw_mode(
            hass=self.hass,
            mode=mode,
            dmw_state_feature_id=dmw_state_feature_id,
            dmw_efficiency_mode_feature_id=dmw_efficiency_mode_feature_id,
            device_id=device.id
        )

        self.async_refresh_feature(device, [dmw_state_feature_id, dmw_efficiency_mode_feature_id])

    async def async_set_max_power_electrical_heater(
            self,
            feature_id: int,
            max_power: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_max_power_electrical_heater(
            hass=self.hass,
            feature_id=feature_id,
            max_power=max_power,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_smart_grid_temperature_offset(
            self,
            feature_id: int,
            offset: SmartGridTemperatureOffsets,
            value: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_smart_grid_temperature_offset(
            hass=self.hass,
            feature_id=feature_id,
            offset=offset,
            value=value,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_temperature_cooling(
            self,
            feature_id: int,
            value: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_temperature_cooling(
            hass=self.hass,
            feature_id=feature_id,
            value=value,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_hysteresis(
            self,
            feature_id: int,
            hysteresis: Hysteresis,
            value: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_hysteresis(
            hass=self.hass,
            feature_id=feature_id,
            hysteresis=hysteresis,
            value=value,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_buffer_temperature(
            self,
            feature_id: int,
            buffer: Buffer,
            value: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_buffer_temperature(
            hass=self.hass,
            feature_id=feature_id,
            buffer=buffer,
            value=value,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_frost_protection_temperature(
            self,
            feature_id: int,
            value: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_frost_protection_temperature(
            hass=self.hass,
            feature_id=feature_id,
            value=value,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_heating_curve(
            self,
            feature_id: int,
            heating_curve: HeatingCurve,
            value: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_heating_curve(
            hass=self.hass,
            feature_id=feature_id,
            heating_curve=heating_curve,
            value=value,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_dhw_hysteresis(
            self,
            feature_id: int,
            hysteresis: DhwHysteresis,
            value: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_dhw_hysteresis(
            hass=self.hass,
            feature_id=feature_id,
            hysteresis=hysteresis,
            value=value,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_buffer_mode(
            self,
            feature_id: int,
            mode: BufferMode,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_buffer_mode(
            hass=self.hass,
            feature_id=feature_id,
            mode=mode,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_hot_water_quickmode(
            self,
            feature_id: int,
            is_on: bool,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_hot_water_quickmode(
            hass=self.hass,
            feature_id=feature_id,
            is_on=is_on,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_vitoair_quick_mode(
            self,
            refresh_feature_id: int,
            set_feature_id: int,
            mode: VitoairQuickMode,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_vitoair_quick_mode(
            hass=self.hass,
            feature_id=set_feature_id,
            mode=mode,
            device_id=device.id
        )

        self.async_refresh_feature(device, [refresh_feature_id])

    async def async_set_hot_water_circulation_pump(
            self,
            feature_id: int,
            is_on: bool,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_hot_water_circulation_pump(
            hass=self.hass,
            feature_id=feature_id,
            is_on=is_on,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_ventilation_level(
            self,
            feature_id: int,
            level: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_ventilation_level(
            hass=self.hass,
            feature_id=feature_id,
            level=level,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_ventilation_mode(
            self,
            feature_id: int,
            mode: VentilationMode,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_ventilation_mode(
            hass=self.hass,
            feature_id=feature_id,
            mode=mode,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    async def async_set_circuit_pump_speed(
            self,
            feature_id: int,
            speed: float,
            device: Open3eDataDevice
    ):
        await self.__client.async_set_circuit_pump_speed(
            hass=self.hass,
            feature_id=feature_id,
            speed=speed,
            device_id=device.id
        )

        self.async_refresh_feature(device, [feature_id])

    def async_refresh_feature(self, device: Open3eDataDevice, feature_ids: list[int]):
        async def delayed_refresh():
            # Wait for 2 seconds to request new states
            await asyncio.sleep(2)
            await self.__client.async_request_data(self.hass, {device.id: feature_ids})

        asyncio.create_task(delayed_refresh())
