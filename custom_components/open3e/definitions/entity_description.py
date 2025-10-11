from dataclasses import dataclass

from homeassistant.helpers.entity import EntityDescription

from .devices import Device
from .features import Feature


@dataclass(frozen=True)
class Open3eEntityDescription(EntityDescription):
    """Generic entity description for Open3e devices."""
    domain: str = "generic"
    poll_data_features: list[Feature] | None = None
    required_device: Device | None = None
    """Defines which features should be polled on a regular basis."""
