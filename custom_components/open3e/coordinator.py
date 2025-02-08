"""DataUpdateCoordinator for open3e."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import Open3eMqttClient
from .const import DOMAIN
from .definitions.open3e_data import Open3eDataConfig

_LOGGER = logging.getLogger(__name__)

from homeassistant.helpers import device_registry
from .definitions.open3e_data import Open3eDataDeviceFeature
from .definitions.features import Feature


@dataclass
class CoordinatorEndpoint:
    last_refresh: float = -1
    entities_subscribed: int = 1

    def __init__(self, refresh_interval: int):
        self.refresh_interval = refresh_interval

    def add_entity_subscription(self):
        self.entities_subscribed = self.entities_subscribed + 1

    def remove_entity_subscription(self):
        self.entities_subscribed = self.entities_subscribed - 1
        if self.entities_subscribed <= 0:
            return True
        else:
            return False

    def set_refresh_interval(self, refresh_interval):
        if refresh_interval < self.refresh_interval:
            self.refresh_interval = refresh_interval

    def should_refresh(self, now: float):
        return now - self.last_refresh > self.refresh_interval - 0.5  # let's use a range so we can make sure it gets refreshed

    def update_last_refresh(self, now: float):
        self.last_refresh = now


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class Open3eDataUpdateCoordinator(DataUpdateCoordinator):
    """
    Class to manage requesting for MQTT updates.
    MQTT updates subscriptions are retrieved in the entities rather than in this class.
    """

    __client: Open3eMqttClient
    config: Open3eDataConfig
    __device_registry: DeviceRegistry
    __entry_id: str

    _endpoints: dict[int, CoordinatorEndpoint] = {}

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

    async def _async_setup(self):
        """Set up the coordinator

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        self.config = await self.__client.async_get_open3e_config(self.hass)
        for device in self.config.devices:
            self.__device_registry.async_get_or_create(
                config_entry_id=self.__entry_id,
                identifiers={(DOMAIN, device.name)},
                manufacturer=device.manufacturer,
                serial_number=device.serial_number,
                sw_version=device.software_version,
                hw_version=device.hardware_version,
                name="Vitocal",
                model="Vitocal",
            )

    async def _async_update_data(self) -> Any:
        """Update data."""
        now = time.time()

        ids = list()

        for id in self._endpoints.keys():
            if self._endpoints[id].should_refresh(now):
                ids.append(id)
                self._endpoints[id].update_last_refresh(now)

        if len(ids) == 0:
            return True

        _LOGGER.debug(f"Requesting data update for features {ids}")

        await self.__client.async_request_data(self.hass, ids)

        return True

    async def on_entity_added(self, features: list[Feature]):
        _LOGGER.debug("Entity was added to Coordinator")
        for feature in features:
            if feature.id not in self._endpoints:
                self._endpoints[feature.id] = CoordinatorEndpoint(
                    refresh_interval=feature.refresh_interval
                )
            else:
                self._endpoints[feature.id].add_entity_subscription()
                self._endpoints[feature.id].set_refresh_interval(feature.refresh_interval)

    def on_entity_removed(self, features: list[Feature]):
        _LOGGER.debug("Entity was removed from Coordinator")
        for feature in features:
            if feature.id in self._endpoints:
                if self._endpoints[feature.id].remove_entity_subscription():
                    del self._endpoints[feature.id]

    def get_mqtt_topics_for_features(self, features: list[Feature]):
        mqtt_topics: list[Open3eDataDeviceFeature] = []

        for feature in features:
            for device in self.config.devices:
                for mqtt_topic in device.features:
                    if mqtt_topic.id == feature.id:
                        mqtt_topics.append(mqtt_topic)
                        break

        return mqtt_topics

    def get_device_for_features(self, features: list[Feature]):
        for feature in features:
            for device in self.config.devices:
                if feature.id in map(lambda entity: entity.id, device.features):
                    return device

        return None

    async def async_set_target_temperature(self, set_target_temperature_feature_id: int, temperature: float,
                                           target_temperature_feature_id: int):
        await self.__client.async_set_target_temperature(self.hass, set_target_temperature_feature_id, temperature)
        # Wait for 2 seconds to request temperature
        await asyncio.sleep(2)
        await self.__client.async_request_data(self.hass, [target_temperature_feature_id])

    async def async_turn_hvac_on(self, power_hvac_feature_id: int):
        await self.__client.async_turn_hvac_on(self.hass, power_hvac_feature_id)
        # Wait for 2 seconds to request hvac state
        await asyncio.sleep(2)

    async def async_turn_hvac_off(self, power_hvac_feature_id: int):
        await self.__client.async_turn_hvac_off(self.hass, power_hvac_feature_id)
        # Wait for 2 seconds to request hvac state
        await asyncio.sleep(2)
