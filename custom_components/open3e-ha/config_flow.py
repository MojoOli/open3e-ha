"""Adds config flow for open3e."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .api import (
    Open3eMqttClient, Open3eClientCommunicationError, Open3eClientMQTTCommunicationError,
)
from .const import DOMAIN, MQTT_CMD_KEY, MQTT_CMD_DEFAULT

_LOGGER = logging.getLogger(__name__)


class Open3eFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""
    _errors = {}

    VERSION = 1

    async def async_step_user(
            self,
            user_input: dict | None = None,
    ):
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = {}

            try:
                client = Open3eMqttClient(mqtt_cmd=user_input[MQTT_CMD_KEY])
                await client.async_get_open3e_config(hass=self.hass)
            except Open3eClientCommunicationError as exception:
                _LOGGER.exception(exception)
                errors["base"] = "communication"
            except Open3eClientMQTTCommunicationError as exception:
                _LOGGER.exception(exception)
                errors["base"] = "mqtt"

            if not errors:
                return self.async_create_entry(title="Open3e", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(
                    "mqtt_cmnd",
                    default=(user_input or {MQTT_CMD_KEY: MQTT_CMD_DEFAULT}).get(MQTT_CMD_KEY, vol.UNDEFINED),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT
                    )
                )
            }),
            errors=errors
        )
