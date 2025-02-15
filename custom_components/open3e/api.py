"""Sample API Client."""

from __future__ import annotations

import asyncio
import logging
from typing import Callable

import async_timeout
from homeassistant.components import mqtt
from homeassistant.components.mqtt import ReceiveMessage
from homeassistant.core import HomeAssistant
from homeassistant.helpers.json import json_dumps
from homeassistant.util.json import json_loads

from .const import MQTT_CONFIG_TOPIC, MQTT_CONFIG_PAYLOAD
from .definitions.open3e_data import Open3eDataConfig
from .definitions.program import Program
from .errors import Open3eServerTimeoutError, Open3eError, Open3eServerUnavailableError

_LOGGER = logging.getLogger(__name__)


class Open3eMqttClient:
    """Open3e Mqtt Client."""

    __mqtt_cmd: str
    __mqtt_topic: str
    __config: Open3eDataConfig = {}

    def __init__(
            self,
            mqtt_topic: str,
            mqtt_cmd: str
    ) -> None:
        self.__mqtt_topic = mqtt_topic
        self.__mqtt_cmd = mqtt_cmd

    __available = None
    """Only used to return availability"""

    async def async_check_availability(self, hass: HomeAssistant):
        subscription = None

        try:
            def on_availability(msg: ReceiveMessage):
                self.__available = msg.payload == "online"

            subscription = await mqtt.async_subscribe(
                hass=hass,
                topic=f"{self.__mqtt_topic}/LWT",
                msg_callback=on_availability
            )

            async with async_timeout.timeout(10):
                while self.__available is None:
                    await asyncio.sleep(0.25)

            if not self.__available:
                self.__available = None
                raise Open3eServerUnavailableError()

        except asyncio.TimeoutError:
            raise Open3eServerTimeoutError()

        except Exception as exception:
            raise Open3eError(exception)

        finally:
            if subscription is not None:
                subscription()

    async def async_subscribe_to_availability(self, hass: HomeAssistant, callback: Callable[[bool], None]):
        try:
            def on_availability(msg: ReceiveMessage):
                callback(msg.payload == "online")

            return await mqtt.async_subscribe(
                hass=hass,
                topic=f"{self.__mqtt_topic}/LWT",
                msg_callback=on_availability
            )

        except Exception as exception:
            raise Open3eError(exception)

    def __on_availability_changed(self, message: ReceiveMessage):
        self.open3e_connected = bool(message.payload)

    async def async_get_open3e_config(self, hass: HomeAssistant):
        if self.__config:
            return self.__config

        subscription = None

        try:
            subscription = await mqtt.async_subscribe(
                hass=hass,
                topic=f"{self.__mqtt_topic}/{MQTT_CONFIG_TOPIC}",
                msg_callback=self.__set_config
            )

            # Subscribing takes a bit longer than waiting for the async method,
            # so wait for 1 second just to be sure that we are subscribed
            await asyncio.sleep(1)

            await mqtt.async_publish(hass=hass, topic=self.__mqtt_cmd, payload=MQTT_CONFIG_PAYLOAD)

            # Wait until data was sent, or we time out after 10 seconds
            async with async_timeout.timeout(10):
                while not self.__config:
                    await asyncio.sleep(0.25)

            return self.__config

        except asyncio.TimeoutError:
            raise Open3eServerTimeoutError()

        except Exception as exception:
            raise Open3eError(exception)

        finally:
            if subscription is not None:
                subscription()

    async def async_request_data(self, hass: HomeAssistant, ids: list[int]):
        try:
            data = ",".join(map(str, ids))
            await mqtt.async_publish(hass=hass, topic=self.__mqtt_cmd,
                                     payload=f'{{"mode": "read-json", "data":[{data}]}}')
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_program_temperature(
            self,
            hass: HomeAssistant,
            set_programs_feature_id: int,
            program: Program,
            temperature: float
    ):
        try:
            _LOGGER.debug(f"Setting programs of feature ID {set_programs_feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=set_programs_feature_id,
                    sub_feature=program.name,
                    data=temperature
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_turn_hvac_on(self, hass: HomeAssistant, power_hvac_feature_id: int):
        try:
            _LOGGER.debug(f"Turning HVAC off with feature ID {power_hvac_feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_raw_payload(
                    feature_id=power_hvac_feature_id,
                    data="0102"
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_turn_hvac_off(self, hass: HomeAssistant, power_hvac_feature_id: int):
        try:
            _LOGGER.debug(f"Turning HVAC off with feature ID {power_hvac_feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_raw_payload(
                    feature_id=power_hvac_feature_id,
                    data="0000"
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    @staticmethod
    def __request_json_payload(feature_ids: list[int]):
        return json_dumps({"mode": "read-json", "data": feature_ids})

    @staticmethod
    def __write_json_payload(feature_id: int, sub_feature: str | None, data: any):
        if sub_feature is None:
            return json_dumps({"mode": "write", "data": [[feature_id, json_dumps(data)]]})

        return json_dumps({"mode": "write", "data": [[f"{feature_id}.{sub_feature}", json_dumps(data)]]})

    @staticmethod
    def __write_raw_payload(feature_id: int, data: str):
        return json_dumps({"mode": "write-raw", "data": [[feature_id, data]]})

    def __set_config(self, message: ReceiveMessage):
        self.__config = Open3eDataConfig.from_dict(json_loads(message.payload))
