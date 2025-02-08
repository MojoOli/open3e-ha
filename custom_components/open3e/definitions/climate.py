from dataclasses import dataclass

from homeassistant.components.climate import ClimateEntityDescription

from .entity_description import Open3eEntityDescription
from .features import Features, Feature


@dataclass(frozen=True)
class Open3eClimateEntityDescription(
    Open3eEntityDescription, ClimateEntityDescription
):
    """Default climate entity description for open3e."""
    domain: str = "climate"
    hvac_mode_feature: Feature | None = None
    flow_temperature_feature: Feature | None = None
    room_temperature_feature: Feature | None = None
    target_temperature_feature: Feature | None = None
    set_target_temperature_feature: Feature | None = None
    fan_power_state_feature: Feature | None = None
    heater_state_feature: Feature | None = None


CLIMATE: tuple[Open3eClimateEntityDescription, ...] = (
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowCircuit1Temperature,
            Features.Temperature.Room1Temperature,
            Features.State.Hvac,
            Features.Temperature.TargetTemperature,
            Features.Power.FanPower,
            Features.State.Heater
        ],
        hvac_mode_feature=Features.State.Hvac,
        flow_temperature_feature=Features.Temperature.FlowCircuit1Temperature,
        room_temperature_feature=Features.Temperature.Room1Temperature,
        target_temperature_feature=Features.Temperature.TargetTemperature,
        set_target_temperature_feature=Features.Temperature.SetTargetTemperature,
        fan_power_state_feature=Features.Power.FanPower,
        heater_state_feature=Features.State.Heater,
        key="climate_circuit_1",
        translation_key="climate_circuit_1"
    ),
)
