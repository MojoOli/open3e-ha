"""Sample API Client."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.components import mqtt
from homeassistant.components.mqtt import ReceiveMessage
from homeassistant.core import HomeAssistant
from homeassistant.helpers.json import json_dumps
from homeassistant.util.json import json_loads

from .const import MQTT_CONFIG_TOPIC, MQTT_CONFIG_PAYLOAD
from .definitions.open3e_data import Open3eDataConfig

_LOGGER = logging.getLogger(__name__)


class Open3eApiClientError(Exception):
    """Exception to indicate a general API error."""


class Open3eClientCommunicationError(
    Open3eApiClientError,
):
    """Exception to indicate a communication error."""


class Open3eClientMQTTCommunicationError(
    Open3eApiClientError,
):
    """Exception to indicate a MQTT communication error."""


class Open3eMqttClient:
    """Open3e Mqtt Client."""

    __mqtt_cmd: str
    __config: Open3eDataConfig = {}

    def __init__(
            self,
            mqtt_cmd: str
    ) -> None:
        self.__mqtt_cmd = mqtt_cmd

    async def async_get_open3e_config(self, hass: HomeAssistant):
        if self.__config:
            return self.__config

        try:
            subscription = await mqtt.async_subscribe(
                hass=hass,
                topic=MQTT_CONFIG_TOPIC,
                msg_callback=self._set_config
            )

            # Subscribing takes a bit longer than waiting for the async method,
            # so wait for 1 second just to be sure that we are subscribed
            await asyncio.sleep(1)

            await mqtt.async_publish(hass=hass, topic=self.__mqtt_cmd, payload=MQTT_CONFIG_PAYLOAD)
        except Exception as exception:
            raise Open3eClientMQTTCommunicationError(f"Couldn't communicate with MQTT server.") from exception

        # Wait until data was sent, or we time out after 10 seconds
        timeout = 0

        while not self.__config and timeout < 10:
            await asyncio.sleep(1)
            timeout = timeout + 1

        # Remove subscription
        subscription()

        if not self.__config:
            raise Open3eClientCommunicationError(
                f"Couldn't communicate with Open3e server via MQTT {self.__mqtt_cmd}."
            )

        return self.__config

    def _set_config(self, message: ReceiveMessage):
        self.__config = Open3eDataConfig.from_dict(json_loads(message.payload))

    async def async_request_data(self, hass: HomeAssistant, ids: list[int]):
        try:
            data = ",".join(map(str, ids))
            await mqtt.async_publish(hass=hass, topic=self.__mqtt_cmd,
                                     payload=f'{{"mode": "read-json", "data":[{data}]}}')
        except Exception as exception:
            raise Open3eClientMQTTCommunicationError(f"Couldn't communicate with MQTT server.") from exception

    async def async_set_programs(
            self,
            hass: HomeAssistant,
            set_programs_feature_id: int,
            programs
    ):
        try:
            _LOGGER.debug(f"Setting programs of feature ID {set_programs_feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self._write_json_payload(
                    feature_id=set_programs_feature_id,
                    data=programs
                )
            )
        except Exception as exception:
            raise Open3eClientMQTTCommunicationError(f"Couldn't communicate with MQTT server.") from exception

    async def async_turn_hvac_on(self, hass: HomeAssistant, power_hvac_feature_id: int):
        try:
            _LOGGER.debug(f"Turning HVAC off with feature ID {power_hvac_feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self._write_raw_payload(
                    feature_id=power_hvac_feature_id,
                    data="0102"
                )
            )
        except Exception as exception:
            raise Open3eClientMQTTCommunicationError(f"Couldn't communicate with MQTT server.") from exception

    async def async_turn_hvac_off(self, hass: HomeAssistant, power_hvac_feature_id: int):
        try:
            _LOGGER.debug(f"Turning HVAC off with feature ID {power_hvac_feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self._write_raw_payload(
                    feature_id=power_hvac_feature_id,
                    data="0000"
                )
            )
        except Exception as exception:
            raise Open3eClientMQTTCommunicationError(f"Couldn't communicate with MQTT server.") from exception

    @staticmethod
    def _request_json_payload(feature_ids: list[int]):
        return json_dumps({"mode": "read-json", "data": feature_ids})

    @staticmethod
    def _write_json_payload(feature_id: int, data: any):
        return json_dumps({"mode": "write", "data": [[feature_id, json_dumps(data)]]})

    @staticmethod
    def _write_raw_payload(feature_id: int, data: str):
        return json_dumps({"mode": "write-raw", "data": [[feature_id, data]]})
