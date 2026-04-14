from dataclasses import dataclass
from typing import Callable, Any, Awaitable

from homeassistant.components.select import SelectEntityDescription

from .devices import Open3eDevices
from .entity_description import Open3eEntityDescription
from .features import Features
from .open3e_data import Open3eDataDevice
from .subfeatures.buffer_mode import BufferMode
from .subfeatures.bypass_operation_state import BypassOperationState, get_bypass_operation_state
from .. import Open3eDataUpdateCoordinator


@dataclass(frozen=True)
class Open3eSelectEntityDescription(
    Open3eEntityDescription, SelectEntityDescription
):
    """Default number entity description for open3e."""
    domain: str = "select"
    get_option: Callable[[Any], str | None] = None
    set_option: Callable[[str, Open3eDataDevice, Open3eDataUpdateCoordinator], Awaitable[None]] = None


SELECTS: tuple[Open3eSelectEntityDescription, ...] = (

    ###############
    ### VITOCAL ###
    ###############

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
        translation_key="buffer_operation_mode",
        required_device=Open3eDevices.Vitocal
    ),

    ###############
    ### VITOAIR ###
    ###############

    Open3eSelectEntityDescription(
        poll_data_features=[Features.State.BypassOperationState],
        options=[BypassOperationState.Closed, BypassOperationState.Automatic, BypassOperationState.Open,
                 BypassOperationState.TransitionError],
        get_option=lambda data: get_bypass_operation_state(data),
        set_option=lambda option, device, coordinator: coordinator.async_set_bypass_operation_state(
            feature_id=Features.State.BypassOperationState.id,
            state=BypassOperationState.from_str(option),
            device=device
        ),
        icon="mdi:valve-open",
        key="ventilation_bypass_operation_state",
        translation_key="ventilation_bypass_operation_state",
        required_device=Open3eDevices.Vitoair
    ),

    # Open3eSelectEntityDescription(
    #     poll_data_features=[Features.State.CurrentQuickMode],
    #     options=[VitoairQuickMode.Intensive, VitoairQuickMode.ReducedNoise, VitoairQuickMode.Off,
    #              VitoairQuickMode.Nothing],
    #     get_option=lambda data: VitoairQuickMode.from_operation_mode(data["OpMode"]),
    #     set_option=lambda option, device, coordinator: coordinator.async_set_vitoair_quick_mode(
    #         refresh_feature_id=Features.State.CurrentQuickMode.id,
    #         set_feature_id=Features.State.TargetQuickMode.id,
    #         mode=VitoairQuickMode.from_str(option),
    #         device=device
    #     ),
    #     icon="mdi:fan-chevron-up",
    #     key="quick_operation_mode",
    #     translation_key="quick_operation_mode",
    #     required_device=Open3eDevices.Vitoair
    # ),
)
