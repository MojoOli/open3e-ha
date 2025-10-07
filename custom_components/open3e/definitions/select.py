from dataclasses import dataclass
from typing import Callable, Any, Awaitable

from homeassistant.components.select import SelectEntityDescription

from .entity_description import Open3eEntityDescription
from .features import Features
from .open3e_data import Open3eDataDevice
from .subfeatures.buffer_mode import BufferMode
from .. import Open3eDataUpdateCoordinator


@dataclass(frozen=True)
class Open3eSelectEntityDescription(
    Open3eEntityDescription, SelectEntityDescription
):
    """Default number entity description for open3e."""
    domain: str = "select"
    get_option: Callable[[Any], str] = None
    set_option: Callable[[str, Open3eDataDevice, Open3eDataUpdateCoordinator], Awaitable[None]] = None


SELECTS: tuple[Open3eSelectEntityDescription, ...] = (
    Open3eSelectEntityDescription(
        poll_data_features=[Features.State.Buffer],
        options=[BufferMode.Heating, BufferMode.Cooling],
        get_option=lambda data: BufferMode.from_operation_mode(data),
        set_option=lambda option, device, coordinator: coordinator.async_set_buffer_mode(
            feature_id=Features.State.Buffer.id,
            mode=BufferMode.from_str(option),
            device=device
        ),
        key="buffer_operation_mode",
        translation_key="buffer_operation_mode"
    ),
)
