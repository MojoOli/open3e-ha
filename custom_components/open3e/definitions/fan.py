from dataclasses import dataclass

from homeassistant.components.fan import FanEntityDescription

from .devices import Open3eDevices
from .entity_description import Open3eEntityDescription
from .features import Features, Feature


@dataclass(frozen=True)
class Open3eFanEntityDescription(
    Open3eEntityDescription, FanEntityDescription
):
    """Default fan entity description for open3e."""
    domain: str = "fan"
    speed_level_feature: Feature | None = None
    mode_feature: Feature | None = None


FAN: tuple[Open3eFanEntityDescription, ...] = (
    Open3eFanEntityDescription(
        poll_data_features=[
            Features.State.VentilationMode,
            Features.State.VentilationLevel
        ],
        speed_level_feature=Features.State.VentilationLevel,
        mode_feature=Features.State.VentilationMode,
        key="ventilation",
        translation_key="ventilation",
        required_device=Open3eDevices.Vitoair
    ),
)
