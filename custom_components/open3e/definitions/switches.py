from dataclasses import dataclass
from typing import Awaitable, Any

from habluetooth.models import Callable
from homeassistant.components.switch import SwitchEntityDescription, SwitchDeviceClass

from .devices import Open3eDevices
from .entity_description import Open3eEntityDescription
from .features import Features
from .open3e_data import Open3eDataDevice
from .. import Open3eDataUpdateCoordinator


@dataclass(frozen=True)
class Open3eSwitchEntityDescription(
    Open3eEntityDescription, SwitchEntityDescription
):
    """Default number entity description for open3e."""
    domain: str = "switch"
    is_on_state: Callable[[Any], bool] = None
    turn_on: Callable[[Open3eDataDevice, Open3eDataUpdateCoordinator], Awaitable[None]] = None
    turn_off: Callable[[Open3eDataDevice, Open3eDataUpdateCoordinator], Awaitable[None]] = None


SWITCHES: tuple[Open3eSwitchEntityDescription, ...] = (

    ###############
    ### VITOCAL ###
    ###############

    Open3eSwitchEntityDescription(
        poll_data_features=[Features.State.TargetQuickMode],
        required_device=Open3eDevices.Vitocal,
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:shower-head",
        key="i_want_hot_water",
        translation_key="i_want_hot_water",
        is_on_state=lambda data: data["Required"] == "on",
        turn_on=lambda device, coordinator: coordinator.async_set_hot_water_quickmode(
            feature_id=Features.State.TargetQuickMode.id,
            is_on=True,
            device=device
        ),
        turn_off=lambda device, coordinator: coordinator.async_set_hot_water_quickmode(
            feature_id=Features.State.TargetQuickMode.id,
            is_on=False,
            device=device
        )
    ),
    Open3eSwitchEntityDescription(
        poll_data_features=[Features.State.HotWaterCirculationPump],
        device_class=SwitchDeviceClass.SWITCH,
        key="hot_water_circulation_pump",
        translation_key="hot_water_circulation_pump",
        icon="mdi:water-sync",
        is_on_state=lambda data: data["State"] == 1,
        turn_on=lambda device, coordinator: coordinator.async_set_hot_water_circulation_pump(
            feature_id=Features.State.HotWaterCirculationPump.id,
            is_on=True,
            device=device
        ),
        turn_off=lambda device, coordinator: coordinator.async_set_hot_water_circulation_pump(
            feature_id=Features.State.HotWaterCirculationPump.id,
            is_on=False,
            device=device
        )
    ),
)
