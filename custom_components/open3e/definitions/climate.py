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
    programs_temperature_feature: Feature | None = None
    fan_power_state_feature: Feature | None = None
    heater_state_feature: Feature | None = None


CLIMATE: tuple[Open3eClimateEntityDescription, ...] = (
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowCircuit1,
            Features.Temperature.Room1,
            Features.State.Hvac,
            Features.Power.Fan1,
            Features.State.AdditionalHeater,
            Features.Temperature.ProgramsCircuit1
        ],
        hvac_mode_feature=Features.State.Hvac,
        flow_temperature_feature=Features.Temperature.FlowCircuit1,
        room_temperature_feature=Features.Temperature.Room1,
        programs_temperature_feature=Features.Temperature.ProgramsCircuit1,
        fan_power_state_feature=Features.Power.Fan1,
        heater_state_feature=Features.State.AdditionalHeater,
        key="climate_circuit_1",
        translation_key="climate_circuit_1"
    ),
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowCircuit2,
            Features.Temperature.Room2,
            Features.State.Hvac,
            Features.Power.Fan1,
            Features.State.AdditionalHeater,
            Features.Temperature.ProgramsCircuit2
        ],
        hvac_mode_feature=Features.State.Hvac,
        flow_temperature_feature=Features.Temperature.FlowCircuit2,
        room_temperature_feature=Features.Temperature.Room2,
        programs_temperature_feature=Features.Temperature.ProgramsCircuit2,
        fan_power_state_feature=Features.Power.Fan1,
        heater_state_feature=Features.State.AdditionalHeater,
        key="climate_circuit_2",
        translation_key="climate_circuit_2",
        entity_registry_enabled_default=False
    ),
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowCircuit3,
            Features.Temperature.Room3,
            Features.State.Hvac,
            Features.Power.Fan1,
            Features.State.AdditionalHeater,
            Features.Temperature.ProgramsCircuit3
        ],
        hvac_mode_feature=Features.State.Hvac,
        flow_temperature_feature=Features.Temperature.FlowCircuit3,
        room_temperature_feature=Features.Temperature.Room3,
        programs_temperature_feature=Features.Temperature.ProgramsCircuit3,
        fan_power_state_feature=Features.Power.Fan1,
        heater_state_feature=Features.State.AdditionalHeater,
        key="climate_circuit_3",
        translation_key="climate_circuit_3",
        entity_registry_enabled_default=False
    ),
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowCircuit4,
            Features.Temperature.Room4,
            Features.State.Hvac,
            Features.Power.Fan1,
            Features.State.AdditionalHeater,
            Features.Temperature.ProgramsCircuit4
        ],
        hvac_mode_feature=Features.State.Hvac,
        flow_temperature_feature=Features.Temperature.FlowCircuit4,
        room_temperature_feature=Features.Temperature.Room4,
        programs_temperature_feature=Features.Temperature.ProgramsCircuit4,
        fan_power_state_feature=Features.Power.Fan1,
        heater_state_feature=Features.State.AdditionalHeater,
        key="climate_circuit_4",
        translation_key="climate_circuit_4",
        entity_registry_enabled_default=False
    ),
)
