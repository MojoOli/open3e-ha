"""Open3e entity class."""

from __future__ import annotations

from typing import Callable, Any

from homeassistant.components import mqtt
from homeassistant.components.mqtt import ReceiveMessage
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN
from .coordinator import Open3eDataUpdateCoordinator
from .definitions.entity_description import Open3eEntityDescription
from .definitions.open3e_data import Open3eDataDevice, Open3eDataDeviceFeature


class Open3eEntity(CoordinatorEntity, Entity):
    """Common Open3e entity."""

    coordinator: Open3eDataUpdateCoordinator
    entity_description: Open3eEntityDescription

    device: Open3eDataDevice
    __mqtt_topics: list[Open3eDataDeviceFeature]
    __mqtt_subscriptions: list[Callable] = []

    data: dict[int, Any] = {}

    def __init__(
            self,
            coordinator: Open3eDataUpdateCoordinator,
            description: Open3eEntityDescription,
            device: Open3eDataDevice
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self.coordinator = coordinator

        self.device = device

        self.__mqtt_topics = coordinator.get_mqtt_topics_for_features(
            features=description.poll_data_features
        )

        slug = slugify(f'{DOMAIN}_{description.key}'.replace("-", "_"))
        self.entity_id = f'{description.domain}.{slug}'
        self._attr_unique_id = slug
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device.name)},
        )
        self._attr_has_entity_name = True
        self.entity_description = description

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        await self.coordinator.on_entity_added(self.entity_description.poll_data_features, self.device)

        for mqtt_topic in self.__mqtt_topics:
            await self._async_register_callback(mqtt_topic=mqtt_topic)

    async def _async_register_callback(self, mqtt_topic: Open3eDataDeviceFeature):
        async def msg_callback(message: any):
            await self._prepare_data(mqtt_topic.id, message)

        self.__mqtt_subscriptions.append(
            await mqtt.async_subscribe(
                hass=self.hass,
                topic=mqtt_topic.topic,
                msg_callback=msg_callback
            )
        )

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity about to be added to hass."""
        self.coordinator.on_entity_removed(self.entity_description.poll_data_features)

        for sub in self.__mqtt_subscriptions:
            sub()
        self.__mqtt_subscriptions.clear()

    @callback
    def _handle_coordinator_update(self) -> None:
        """We are not updating via coordinator as we are using MQTT custom update"""

    async def _prepare_data(self, feature_id: int, message: ReceiveMessage):
        """Prepares data when received from MQTT endpoint"""
        self.data[feature_id] = message.payload
        await self.async_on_data(feature_id)

    async def async_on_data(self, feature_id: int):
        """Run when new data has been received from any MQTT endpoint.

        To be extended by specific entities.
        """
