"""Sample API Client."""

from __future__ import annotations

import asyncio
import logging
from typing import Callable, Any

import async_timeout
from homeassistant.components import mqtt
from homeassistant.components.mqtt import ReceiveMessage
from homeassistant.core import HomeAssistant
from homeassistant.helpers.json import json_dumps
from homeassistant.util.json import json_loads

from custom_components.open3e.definitions.subfeatures.buffer import Buffer
from custom_components.open3e.definitions.subfeatures.dmw_mode import DmwMode
from custom_components.open3e.definitions.subfeatures.hysteresis import Hysteresis
from custom_components.open3e.definitions.subfeatures.program import Program
from custom_components.open3e.definitions.subfeatures.smart_grid_temperature_offsets import SmartGridTemperatureOffsets
from custom_components.open3e.definitions.subfeatures.temperature_cooling import TemperatureCooling
from .capability.capability import DEVICE_CAPABILITIES, CapabilityFeature
from .const import MQTT_SYSTEM_TOPIC, MQTT_SYSTEM_PAYLOAD
from .definitions.devices import Open3eDevices
from .definitions.open3e_data import Open3eDataSystemInformation, Open3eDataDeviceFeature, Open3eDataDevice
from .definitions.subfeatures.buffer_mode import BufferMode
from .definitions.subfeatures.dhw_hysteresis import DhwHysteresis
from .definitions.subfeatures.heating_curve import HeatingCurve
from .definitions.subfeatures.hvac_mode import HvacMode
from .definitions.subfeatures.ventilation_mode import VentilationMode
from .definitions.subfeatures.vitoair_quick_mode import VitoairQuickMode
from .errors import Open3eServerTimeoutError, Open3eError, Open3eServerUnavailableError

_LOGGER = logging.getLogger(__name__)


class Open3eMqttClient:
    """Open3e Mqtt Client."""

    __mqtt_cmd: str
    __mqtt_topic: str
    """Only used to return availability"""

    def __init__(
            self,
            mqtt_topic: str,
            mqtt_cmd: str
    ) -> None:
        self.__mqtt_topic = mqtt_topic
        self.__mqtt_cmd = mqtt_cmd

    async def async_check_availability(self, hass: HomeAssistant) -> bool:
        """
        Check if the device is available via its MQTT LWT topic.
        Returns True if online, raises an exception if unavailable or timed out.
        """
        event = asyncio.Event()
        available: bool | None = None
        subscription = None

        def on_availability(msg: ReceiveMessage):
            nonlocal available
            available = msg.payload == "online"
            hass.loop.call_soon_threadsafe(event.set)

        try:
            topic = f"{self.__mqtt_topic}/LWT"
            subscription = await mqtt.async_subscribe(
                hass=hass,
                topic=topic,
                msg_callback=on_availability
            )

            # Wait for availability message or timeout
            async with async_timeout.timeout(10):
                await event.wait()

            if not available:
                raise Open3eServerUnavailableError()

            return True

        except asyncio.TimeoutError:
            raise Open3eServerTimeoutError()
        except Exception as exc:
            raise Open3eError(exc)
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

    async def async_get_system_information(self, hass: HomeAssistant) -> Open3eDataSystemInformation:
        """
        Request system information via MQTT and return it.
        """
        event = asyncio.Event()
        system_information: Open3eDataSystemInformation | None = None

        def message_callback(message: ReceiveMessage):
            nonlocal system_information
            system_information = Open3eDataSystemInformation.from_dict(json_loads(message.payload))
            hass.loop.call_soon_threadsafe(event.set)  # Signal that data has been received

        subscription = None
        try:
            _LOGGER.debug("Requesting system information")
            topic = f"{self.__mqtt_topic}/{MQTT_SYSTEM_TOPIC}"
            subscription = await mqtt.async_subscribe(
                hass=hass,
                topic=topic,
                msg_callback=message_callback
            )

            # Ensure subscription is active
            await asyncio.sleep(1)

            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=MQTT_SYSTEM_PAYLOAD
            )

            await asyncio.wait_for(event.wait(), timeout=10)
            _LOGGER.info("System information successfully received")

            _LOGGER.debug("Setting device capabilities for received system information")
            await self.__set_devices_capabilities(hass=hass, system_information=system_information)

            return system_information

        except asyncio.TimeoutError:
            raise Open3eServerTimeoutError()
        except Exception as exc:
            raise Open3eError(exc)
        finally:
            if subscription:
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
                    sub_feature=program.map_to_api_heating(),
                    data=temperature,
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_program_temperature_cooling(
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
                    sub_feature=program.map_to_api_cooling(),
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

    async def async_set_hvac_mode(
            self,
            hass: HomeAssistant,
            mode: HvacMode,
            hvac_mode_feature_id: int,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting HVAC mode {mode} of feature ID {hvac_mode_feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=hvac_mode_feature_id,
                    data=mode.to_api(),
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

    async def async_set_frost_protection_temperature(
            self,
            hass: HomeAssistant,
            feature_id: int,
            value: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting {value} temperature of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=value,
                    sub_feature="Temperature",
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_heating_curve(
            self,
            hass: HomeAssistant,
            feature_id: int,
            heating_curve: HeatingCurve,
            value: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting {heating_curve} temperature of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=value,
                    sub_feature=heating_curve,
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_dhw_hysteresis(
            self,
            hass: HomeAssistant,
            feature_id: int,
            hysteresis: DhwHysteresis,
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

    async def async_set_buffer_mode(
            self,
            hass: HomeAssistant,
            feature_id: int,
            mode: BufferMode,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting buffer mode to {mode} of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=mode.map_to_api(),
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_hot_water_quickmode(
            self,
            hass: HomeAssistant,
            feature_id: int,
            is_on: bool,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting hot water quickmode to {is_on} of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data={"OpMode": 2, "Required": "on" if is_on else "off", "Unknown": "0000"},
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_vitoair_quick_mode(
            self,
            hass: HomeAssistant,
            feature_id: int,
            mode: VitoairQuickMode,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting quickmode to {mode} of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data={"OpMode": mode.map_to_api(), "Required": "on", "Unknown": "3c00"},  # 3c00 -> 60mins
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_hot_water_circulation_pump(
            self,
            hass: HomeAssistant,
            feature_id: int,
            is_on: bool,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting hot water pump to {is_on} of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    sub_feature="State",
                    data=1 if is_on else 0,
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_ventilation_level(
            self,
            hass: HomeAssistant,
            feature_id: int,
            level: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting level to {level} of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=level,
                    sub_feature="Acutual",
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_ventilation_mode(
            self,
            hass: HomeAssistant,
            feature_id: int,
            mode: VentilationMode,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting mode to {mode} of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=mode.map_to_api(),
                    sub_feature="Mode",
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)

    async def async_set_circuit_pump_speed(
            self,
            hass: HomeAssistant,
            feature_id: int,
            speed: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting pump speed to {speed} of feature ID {feature_id}")
            await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data=speed,
                    sub_feature="Setpoint",
                    device_id=device_id
                )
            )
        except Exception as exception:
            raise Open3eError(exception)
        
    async def async_set_backup_box_discharge_limit_percentage(
            self,
            hass: HomeAssistant,
            feature_id: int,
            backup_box_discharge_limit_percentage: float,
            device_id: int
    ):
        try:
            _LOGGER.debug(f"Setting backup box discharge limit percentage to {backup_box_discharge_limit_percentage} of feature ID {feature_id}")
            await mqtt.async_publish(
                await mqtt.async_publish(
                hass=hass,
                topic=self.__mqtt_cmd,
                payload=self.__write_json_payload(
                    feature_id=feature_id,
                    data={"DischargeLimit": backup_box_discharge_limit_percentage, "Unknown": "1.0"}, #TODO: Unknown Needs to be renamed when open3e is updated to BackUpBoxIn
                    device_id=device_id
                )
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

    async def __set_devices_capabilities(
            self,
            hass: HomeAssistant,
            system_information: Open3eDataSystemInformation
    ):
        """
        Subscribe to all device feature topics, request data, and populate device capabilities
        when valid data is received. Invalid or unavailable values are skipped but still counted
        toward completion.
        """
        event = asyncio.Event()
        pending_features: dict[str, tuple[Open3eDataDeviceFeature, CapabilityFeature, Open3eDataDevice]] = {}
        subscriptions: list[Any] = []

        def message_callback(message: ReceiveMessage):
            topic = message.topic
            payload = message.payload

            entry = pending_features.get(topic)
            if not entry:
                _LOGGER.warning("Received message for unknown topic '%s'", topic)
                return

            feature, cap_feature, device = entry
            del pending_features[topic]

            # Evaluate using the CapabilityFeature
            if cap_feature.evaluate(json_loads(payload)):
                device.capabilities.add(cap_feature.capability)
                _LOGGER.info(
                    "Added capability '%s' to '%s'",
                    cap_feature.capability, device.name
                )
            else:
                _LOGGER.info(
                    "'%s' not capable of %s; payload '%s'",
                    device.name, cap_feature.capability, payload
                )

            if not pending_features:
                hass.loop.call_soon_threadsafe(event.set)

        try:
            for device in system_information.devices:
                # Find the capability device enum
                capability_device = next(
                    (dev for dev in Open3eDevices if dev.display_name in device.name),
                    None
                )
                if not capability_device:
                    _LOGGER.debug("No capability device found for system device '%s'", device.name)
                    continue

                device_features: list[Open3eDataDeviceFeature] = []

                for cap_feature in DEVICE_CAPABILITIES.get(capability_device, []):
                    feature_enum = cap_feature.feature
                    feature = next((f for f in device.features if f.id == feature_enum.id), None)
                    if feature is None:
                        _LOGGER.warning(
                            "Feature '%s' for capability '%s' not found in device '%s'",
                            feature_enum.id, cap_feature.capability, device.name
                        )
                        continue

                    device_features.append(feature)
                    pending_features[feature.topic] = (feature, cap_feature, device)

                    subscription = await mqtt.async_subscribe(
                        hass=hass,
                        topic=feature.topic,
                        msg_callback=message_callback
                    )
                    subscriptions.append(subscription)

                if device_features:
                    # Give subscriptions time to be ready
                    await asyncio.sleep(1)
                    _LOGGER.debug(
                        "Checking capabilities for device '%s'",
                        device.name
                    )
                    await self.async_request_data(
                        hass=hass,
                        device_features={device.id: [f.id for f in device_features]}
                    )

            if pending_features:
                _LOGGER.debug("Waiting for all capabilities to be processed...")
                await asyncio.wait_for(event.wait(), timeout=10)
                _LOGGER.info("All device capabilities processed successfully")

        except asyncio.TimeoutError:
            raise Open3eServerTimeoutError()
        except Exception as exc:
            raise Open3eError(exc)
        finally:
            # Clean up subscriptions
            for unsubscribe in subscriptions:
                unsubscribe()
