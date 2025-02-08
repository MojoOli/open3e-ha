"""HA data types for open3e integration"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry

from .api import Open3eMqttClient
from .coordinator import Open3eDataUpdateCoordinator

type Open3eDataConfigEntry = ConfigEntry[Open3eData]


@dataclass(frozen=True)
class Open3eData:
    """Data for the Blueprint integration."""

    client: Open3eMqttClient
    coordinator: Open3eDataUpdateCoordinator
