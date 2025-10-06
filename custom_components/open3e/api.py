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

from .const import MQTT_SYSTEM_TOPIC, MQTT_SYSTEM_PAYLOAD
from .definitions.buffer import Buffer
from .definitions.dmw_mode import DmwMode
from .definitions.hysteresis import Hysteresis
from .definitions.open3e_data import Open3eDataSystemInformation
from .definitions.program import Program
from .definitions.smart_grid_temperature_offsets import SmartGridTemperatureOffsets
from .definitions.temperature_cooling import TemperatureCooling
from .errors import Open3eServerTimeoutError, Open3eError, Open3eServerUnavailableError

_LOGGER = logging.getLogger(__name__)


class Open3eMqttClient:
    """Open3e Mqtt Client."""

    __mqtt_cmd: str
    __mqtt_topic: str
    __system_information: Open3eDataSystemInformation = {}

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

    async def async_get_system_information(self, hass: HomeAssistant):
        if self.__system_information:
            return self.__system_information

        subscription = None

        try:
            subscription = await mqtt.async_subscribe(
                hass=hass,
                topic=f"{self.__mqtt_topic}/{MQTT_SYSTEM_TOPIC}",
                msg_callback=self.__set_system
            )

            # Subscribing takes a bit longer than waiting for the async method,
            # so wait for 1 second just to be sure that we are subscribed
            await asyncio.sleep(1)

            await mqtt.async_publish(hass=hass, topic=self.__mqtt_cmd, payload=MQTT_SYSTEM_PAYLOAD)

            # Wait until data was sent, or we time out after 10 seconds
            async with async_timeout.timeout(10):
                while not self.__system_information:
                    await asyncio.sleep(0.25)

            return self.__system_information

        except asyncio.TimeoutError:
            raise Open3eServerTimeoutError()

        except Exception as exception:
            raise Open3eError(exception)

        finally:
            if subscription is not None:
                subscription()

    async def async_request_data(self, hass: HomeAssistant, device_features: dict[int, list[int]]):
        try:
            for device in device_features.keys():
                data = ",".join(map(str, device_features[device]))
                await mqtt.async_publish(hass=hass, topic=self.__mqtt_cmd,
                                         payload=f'{{"mode": "read-json", "addr": "{device}", "data":[{data}]}}')

        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_program_temperature(
            self,
            hass: HomeAssistant,
            set_programs_feature_id: int,
            program: Program,
            temperature: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting programs of feature ID {set_programs_feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=set_programs_feature_id,
                    sub_feature=program.map_to_api(),
                    data=temperature,
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_hot_water_temperature(
            self,
            hass: HomeAssistant,
            feature_id: int,
            temperature: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting hot water temperature of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=temperature,
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_turn_hvac_on(self, hass: HomeAssistant, power_hvac_feature_id: int, device_id: int):
        try:
            _LOGGER.debug(f"Turning HVAC off with feature ID {power_hvac_feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_raw_payload(
                    feature_id=power_hvac_feature_id,
                    data="0102",
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_turn_hvac_off(self, hass: HomeAssistant, power_hvac_feature_id: int, device_id: int):
        try:
            _LOGGER.debug(f"Turning HVAC off with feature ID {power_hvac_feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_raw_payload(
                    feature_id=power_hvac_feature_id,
                    data="0000",
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_dmw_mode(self, hass: HomeAssistant, mode: DmwMode, dmw_state_feature_id: int,
                                 dmw_efficiency_mode_feature_id: int, device_id: int):
        try:
            _LOGGER.debug(f"Setting DMW mode to {mode}")

            state_payload = None
            efficiency_payload = None

            match mode:
                case DmwMode.Eco:
                    state_payload = {"Mode": 1, "State": 1}
                    efficiency_payload = 0
                case DmwMode.Comfort:
                    state_payload = {"Mode": 1, "State": 1}
                    efficiency_payload = 2
                case DmwMode.Off:
                    state_payload = {"Mode": 0, "State": 0}

            if state_payload is not None:
                await mqtt.async_publish(
                    hass=hass,
                    topic=self.__mqtt_cmd,
                    payload=self.__write_json_payload(
                        feature_id=dmw_state_feature_id,
                        data=state_payload,
                        device_id=device_id
                    )
                )

            if efficiency_payload is not None:
                await mqtt.async_publish(
                    hass=hass,
                    topic=self.__mqtt_cmd,
                    payload=self.__write_json_payload(
                        feature_id=dmw_efficiency_mode_feature_id,
                        data=efficiency_payload,
                        device_id=device_id
                    )
                )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_max_power_electrical_heater(
            self,
            hass: HomeAssistant,
            feature_id: int,
            max_power: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting max power of electrical heater of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=max_power,
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_smart_grid_temperature_offset(
            self,
            hass: HomeAssistant,
            feature_id: int,
            offset: SmartGridTemperatureOffsets,
            value: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting {offset} of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=value,
                    sub_feature=offset,
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_temperature_cooling(
            self,
            hass: HomeAssistant,
            feature_id: int,
            value: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting {TemperatureCooling.EffectiveSetTemperature} of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=value,
                    sub_feature=TemperatureCooling.EffectiveSetTemperature,
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_hysteresis(
            self,
            hass: HomeAssistant,
            feature_id: int,
            hysteresis: Hysteresis,
            value: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting {hysteresis} of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=value,
                    sub_feature=hysteresis,
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_buffer_temperature(
            self,
            hass: HomeAssistant,
            feature_id: int,
            buffer: Buffer,
            value: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting {buffer} temperature of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=value,
                    sub_feature=buffer,
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    @staticmethod
    def __write_json_payload(feature_id: int, data: any, device_id: int, sub_feature: str | None = None):
        if sub_feature is None:
            return json_dumps({"mode": "write", "addr": device_id, "data": [[feature_id, json_dumps(data)]]})

        return json_dumps(
            {"mode": "write", "addr": device_id, "data": [[f"{feature_id}.{sub_feature}", json_dumps(data)]]})

    @staticmethod
    def __write_raw_payload(feature_id: int, data: str, device_id: int):
        return json_dumps({"mode": "write-raw", "addr": device_id, "data": [[feature_id, data]]})

    def __set_system(self, message: ReceiveMessage):
        self.__system_information = Open3eDataSystemInformation.from_dict(json_loads(message.payload))
