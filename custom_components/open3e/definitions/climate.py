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
            Features.Temperature.FlowTemperatureCircuit1,
            Features.Temperature.Room1Temperature,
            Features.State.Hvac,
            Features.Power.FanPower,
            Features.State.Heater,
            Features.Temperature.ProgramsTemperatureCircuit1
        ],
        hvac_mode_feature=Features.State.Hvac,
        flow_temperature_feature=Features.Temperature.FlowTemperatureCircuit1,
        room_temperature_feature=Features.Temperature.Room1Temperature,
        programs_temperature_feature=Features.Temperature.ProgramsTemperatureCircuit1,
        fan_power_state_feature=Features.Power.FanPower,
        heater_state_feature=Features.State.Heater,
        key="climate_circuit_1",
        translation_key="climate_circuit_1"
    ),
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowTemperatureCircuit2,
            Features.Temperature.Room2Temperature,
            Features.State.Hvac,
            Features.Power.FanPower,
            Features.State.Heater,
            Features.Temperature.ProgramsTemperatureCircuit2
        ],
        hvac_mode_feature=Features.State.Hvac,
        flow_temperature_feature=Features.Temperature.FlowTemperatureCircuit2,
        room_temperature_feature=Features.Temperature.Room2Temperature,
        programs_temperature_feature=Features.Temperature.ProgramsTemperatureCircuit2,
        fan_power_state_feature=Features.Power.FanPower,
        heater_state_feature=Features.State.Heater,
        key="climate_circuit_2",
        translation_key="climate_circuit_2",
        entity_registry_enabled_default=False
    ),
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowTemperatureCircuit3,
            Features.Temperature.Room3Temperature,
            Features.State.Hvac,
            Features.Power.FanPower,
            Features.State.Heater,
            Features.Temperature.ProgramsTemperatureCircuit3
        ],
        hvac_mode_feature=Features.State.Hvac,
        flow_temperature_feature=Features.Temperature.FlowTemperatureCircuit3,
        room_temperature_feature=Features.Temperature.Room3Temperature,
        programs_temperature_feature=Features.Temperature.ProgramsTemperatureCircuit3,
        fan_power_state_feature=Features.Power.FanPower,
        heater_state_feature=Features.State.Heater,
        key="climate_circuit_3",
        translation_key="climate_circuit_3",
        entity_registry_enabled_default=False
    ),
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowTemperatureCircuit4,
            Features.Temperature.Room4Temperature,
            Features.State.Hvac,
            Features.Power.FanPower,
            Features.State.Heater,
            Features.Temperature.ProgramsTemperatureCircuit4
        ],
        hvac_mode_feature=Features.State.Hvac,
        flow_temperature_feature=Features.Temperature.FlowTemperatureCircuit4,
        room_temperature_feature=Features.Temperature.Room4Temperature,
        programs_temperature_feature=Features.Temperature.ProgramsTemperatureCircuit4,
        fan_power_state_feature=Features.Power.FanPower,
        heater_state_feature=Features.State.Heater,
        key="climate_circuit_4",
        translation_key="climate_circuit_4",
        entity_registry_enabled_default=False
    ),
)
