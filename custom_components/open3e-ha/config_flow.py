"""Adds config flow for open3e."""

from __future__ import annotations

import asyncio

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .api import (
    Open3eMqttClient,
)
from .const import DOMAIN, MQTT_CMD, MQTT_CMD_DEFAULT


class Open3eFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""
    mqtt_config_task: asyncio.Task | None = None
    was_config_sent: bool = False

    VERSION = 1

    async def async_step_user(
            self,
            user_input: dict | None = None,
    ):
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            if not self.mqtt_config_task:
                self.mqtt_config_task = asyncio.create_task(
                    self._test_mqtt(
                        hass=self.hass,
                        mqtt_cmd=user_input[MQTT_CMD],
                    )
                )
            if not self.mqtt_config_task.done():
                return self.async_show_progress(
                    progress_action="mqtt_config_task",
                    progress_task=self.mqtt_config_task,
                )
        # try:
        # except IntegrationBlueprintApiClientAuthenticationError as exception:
        #     LOGGER.warning(exception)
        #     _errors["base"] = "auth"
        # except IntegrationBlueprintApiClientCommunicationError as exception:
        #     LOGGER.error(exception)
        #     _errors["base"] = "connection"
        # except IntegrationBlueprintApiClientError as exception:
        #     LOGGER.exception(exception)
        #     _errors["base"] = "unknown"
        # else:
        #     await self.async_set_unique_id(
        #         ## Do NOT use this in production code
        #         ## The unique_id should never be something that can change
        #         ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
        #         unique_id=slugify(user_input[CONF_USERNAME])
        #     )
        #     self._abort_if_unique_id_configured()
        #     return self.async_create_entry(
        #         title=user_input[CONF_USERNAME],
        #         data=user_input,
        #     )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(
                    "mqtt_cmnd",
                    default=(user_input or {MQTT_CMD: MQTT_CMD_DEFAULT}).get(MQTT_CMD, vol.UNDEFINED),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT
                    )
                )
            }),
            errors=_errors
        )

    async def _test_mqtt(self, hass: HomeAssistant, mqtt_cmd: str):
        """Validate credentials."""
        client = Open3eMqttClient(mqtt_cmd=mqtt_cmd)
        await client.async_request_config(hass=hass, config_callback=self._set_was_config_sent)

        # while self.was_config_sent:
        #     await asyncio.sleep(1)

    def _set_was_config_sent(self):
        self.was_config_sent = True
