"""
Custom integration to integrate open3e with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/integration_blueprint
"""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import Open3eMqttClient
from .const import MQTT_CMD_KEY, MQTT_TOPIC_KEY
from .ha_data import Open3eDataConfigEntry, Open3eData
from .ha_data import Open3eDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.WATER_HEATER
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    client = Open3eMqttClient(
        mqtt_topic=entry.data[MQTT_TOPIC_KEY],
        mqtt_cmd=entry.data[MQTT_CMD_KEY]
    )

    coordinator = Open3eDataUpdateCoordinator(
        hass=hass,
        client=client,
        entry_id=entry.entry_id
    )

    entry.runtime_data = Open3eData(
        client=client,
        coordinator=coordinator
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
