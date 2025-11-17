"""Adds config flow for open3e."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .api import (
    Open3eMqttClient
)
from .const import DOMAIN, MQTT_CMD_KEY, MQTT_CMD_DEFAULT, MQTT_TOPIC_KEY, MQTT_TOPIC_DEFAULT
from .errors import Open3eServerTimeoutError, Open3eServerUnavailableError, Open3eError

_LOGGER = logging.getLogger(__name__)


class Open3eFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""
    _errors = {}

    VERSION = 3

    async def async_step_user(
            self,
            user_input: dict | None = None,
    ):
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = {}

            try:
                client = Open3eMqttClient(mqtt_topic=user_input[MQTT_TOPIC_KEY], mqtt_cmd=user_input[MQTT_CMD_KEY])
                await client.async_check_availability(self.hass)
            except Open3eServerTimeoutError as exception:
                _LOGGER.exception(exception)
                errors["base"] = "timeout"
            except Open3eServerUnavailableError as exception:
                _LOGGER.exception(exception)
                errors["base"] = "unavailable"
            except Open3eError as exception:
                _LOGGER.exception(exception)
                errors["base"] = "general"

            if not errors:
                return self.async_create_entry(title="Open3e", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(
                    "mqtt_topic",
                    default=(user_input or {MQTT_TOPIC_KEY: MQTT_TOPIC_DEFAULT}).get(MQTT_TOPIC_KEY, vol.UNDEFINED),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT
                    )
                ),
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
