"""
Custom integration to integrate open3e with Home Assistant.

For more details about this integration, please refer to
https://github.com/MojoOli/open3e-ha
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import Platform, EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.util import slugify

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from .api import Open3eMqttClient
from .const import MQTT_CMD_KEY, MQTT_TOPIC_KEY, DOMAIN
from .ha_data import Open3eData, Open3eDataConfigEntry, Open3eDataUpdateCoordinator
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.WATER_HEATER
]


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
        entry: Open3eDataConfigEntry
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_migrate_entry(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry
):
    """Migrate Open3e devices to use serial_number identifiers safely."""
    current_version = entry.version or 1
    new_version = 2  # Increment for future migrations

    if current_version >= new_version:
        return True

    _LOGGER.info("Migrating Open3e config entry from version %s to %s", current_version, new_version)

    dev_reg = dr.async_get(hass)

    for device in dr.async_entries_for_config_entry(dev_reg, entry.entry_id):
        identifiers = set(device.identifiers)
        new_identifiers = set()
        changed = False

        for domain, identifier in identifiers:
            if domain != DOMAIN:
                # Keep other integrations' identifiers untouched
                new_identifiers.add((domain, identifier))
                continue

            # Old identifier: non-numeric names (device.name)
            if identifier and not identifier.isdigit():
                new_id = device.serial_number

                # Include BOTH old + new identifiers temporarily
                new_identifiers.add((DOMAIN, identifier))  # old
                new_identifiers.add((DOMAIN, new_id))  # new

                _LOGGER.debug(
                    "Migrating device %s identifiers: keeping '%s', adding '%s'",
                    device.id,
                    identifier,
                    new_id,
                )
                changed = True
            else:
                # Already using numeric/serial, keep as is
                new_identifiers.add((DOMAIN, identifier))

        if changed:
            device = dev_reg.async_update_device(
                device_id=device.id,
                new_identifiers=new_identifiers,
            )

        async_migrate_entities(hass, entry, device)

    # Mark migration complete
    hass.config_entries.async_update_entry(entry, version=new_version)
    _LOGGER.info("Open3e config entry migration complete")

    return True


def async_migrate_entities(
        hass: HomeAssistant,
        entry: Open3eDataConfigEntry,
        device: DeviceEntry
):
    """Migrate entity unique IDs from old pattern to new pattern."""
    ent_reg = er.async_get(hass)

    device_entities = [
        e for e in ent_reg.entities.values()
        if e.device_id == device.id
    ]

    for entity in device_entities:
        unique_id = entity.unique_id

        if device.serial_number in unique_id:
            continue

        # Parse description key from old unique_id
        if unique_id.startswith(f"{DOMAIN}_"):
            description_key = unique_id[len(f"{DOMAIN}_"):]
        else:
            description_key = unique_id  # fallback

        # Build new unique_id
        slug = slugify(f"{device.name}_{device.serial_number}_{description_key}".replace("-", "_"))

        new_unique_id = f"{DOMAIN}_{slug}"
        new_entity_id = f"{entity.domain}.{slug}"

        # Update entity registry
        ent_reg.async_update_entity(
            entity_id=entity.entity_id,
            new_unique_id=new_unique_id,
            new_entity_id=new_entity_id,
        )

        _LOGGER.debug(
            "Migrated entity %s from '%s' to '%s'",
            entity.entity_id,
            unique_id,
            new_unique_id
        )
