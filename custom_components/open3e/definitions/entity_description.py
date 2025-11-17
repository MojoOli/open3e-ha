from dataclasses import dataclass

from homeassistant.helpers.entity import EntityDescription

from .devices import Device
from .features import Feature
from ..capability.capability import Capability


@dataclass(frozen=True)
class Open3eEntityDescription(EntityDescription):
    """Generic entity description for Open3e devices."""
    domain: str = "generic"
    poll_data_features: list[Feature] | None = None
    """Defines which features should be polled on a regular basis."""
    required_device: Device | None = None
    """Defines which device this requires. Some features can be used for multiple devices such as TargetQuickMode."""
    required_capabilities: list[Capability] | None = None
    """Defines which capabilities this requires. Some devices have optional features, such as multiple circuits on the Vitocal."""
